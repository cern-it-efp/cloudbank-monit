#!/usr/bin/env python3

import time
import os
import sys
import boto3
import json
import csv
import gzip
import shutil
import pandas as pd
import numpy as np
import json
from datetime import datetime, date, timedelta

local_path = "/tmp"
aws_access_key_id=""
aws_secret_access_key=""

def getGroups():
    """ Returns a dictionary containing properties, groupdID:name. """

    # This dict will contain properties having groupd ID and name
    groups_ids = {}

    # Get IAM boto3 client
    client_iam = boto3.client(
        "iam",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    # Iterate through IAM groups (*_Users and *_Admin)
    for gr in client_iam.list_groups()["Groups"]:

        group_name = gr["GroupName"]

        # List groups inline policies
        group_policies = client_iam.list_group_policies(GroupName=group_name)

        for policy_name in group_policies["PolicyNames"]:

            # The policies that have the group ID's are named: policygen-*_Users-*
            if "policygen" in policy_name and "Users" in policy_name:

                # Retrieve policy information (the JSON data that is seen on the UI)
                response = client_iam.get_group_policy(GroupName=group_name,PolicyName=policy_name)

                # Get the resource arn that contains the group ID from the policy JSON
                inline_policy_arn = response["PolicyDocument"]["Statement"][0]["Resource"][0]

                # Take the group ID from the arn
                group_id = inline_policy_arn.replace("arn:aws:iam::","").replace(":role/AccountPowerUser","")

                # Add to the groups_ids dict a property containing groupd ID and name
                groups_ids[int(group_id)] = group_name.replace("_Users","")

    return groups_ids


def getAWS(current_path):
    ###### Create a boto3 client that allows you to programmatically use the S3 service:
    client_s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="us-east-2" # compulsory
    	)

    ###### Use the client to download the JSON manifest file:
    client_s3.download_file('strategic-blue-reports-cern',
                         current_path,
                         local_path + '/file.json')

    ###### The manifest's 'reportKeys' tells you which one is the latest CSV:
    with open(local_path + '/file.json') as json_file:
        latestCSV = json.load(json_file)["reportKeys"][0]

    ###### Now that you know which one is the latest CSV, you can download it (as a .gz):
    client_s3.download_file('strategic-blue-reports-cern',
                         latestCSV,
                         local_path + '/file.csv.gz')

    ###### Unzip the .gz file in order to get its .csv file:
    with gzip.open(local_path + '/file.csv.gz', 'rb') as f_in:
        with open(local_path + '/file.csv', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    ###### Load the obtained CSV file as a Pandas DataFrame with specific columns
    df = pd.read_csv(local_path + '/file.csv',usecols = ['lineItem/UsageAccountId',
                                                         'lineItem/UnblendedCost',
                                                         'lineItem/UsageStartDate'])
    return df.to_numpy()


# TODO: this should be done programmatically
months = ["20201101-20201201/",
        "20201201-20210101/",
        "20210101-20210201/",
        "20210201-20210301/",
        "20210301-20210401/",
        "20210401-20210501/",
        "20210501-20210601/",
        "20210601-20210701/",
        "20210701-20210801/"]
#months = ["20210601-20210701/"]

###### Use the function getGroups() to get a dictionary containing properties, groupdID:name
projects_dict = getGroups()

def getNameFromID(projectID):
    try:
        return projects_dict[projectID]
    except:
        return projectID

data_by_project = {}

for month in months:
    current_path = ("/sb-cern-aws/" + month + "sb-cern-aws-Manifest.json")

    data = getAWS(current_path)

    for d in data:
        cost = d[2]
        if cost > 0:
            projectName = getNameFromID(d[0])

            usage_start_time_unix_day = int(datetime.strptime(d[1], "%Y-%m-%dT%H:%M:%SZ").replace(minute=59, hour=23, second=59).timestamp() * 1000000000)

            if projectName not in data_by_project:
                data_by_project[projectName] = {}

            if usage_start_time_unix_day not in data_by_project[projectName]:
                data_by_project[projectName][usage_start_time_unix_day] = 0

            data_by_project[projectName][usage_start_time_unix_day] += cost


with open('dataAWS', 'a') as file:
    for project, value in data_by_project.items():
        for timestamp_day , consumption in value.items():
            # TODO: for some reason, the consumption is stable day to day, but actually it shouldnt
            file.write("amountSpent,projectid=%s,platform=AWS value=%s %s\n" % (project, consumption, int(timestamp_day)))
