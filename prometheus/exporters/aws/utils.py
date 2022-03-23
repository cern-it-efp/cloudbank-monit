#!/usr/bin/env python3

import boto3
import json
import csv
import gzip
import shutil
import pandas as pd
import numpy as np
import json
import config
import datetime as dt
import string
import geonamescache
from geonamescache.mappers import country
import pycountry


local_path = "C:/Users/atheodor/AppData/Local/Temp"
local_path = "/tmp"

def getGroups():
    """ Returns a dictionary containing properties, groupdID:name. """

    # This dict will contain properties having groupd ID and name
    groups_ids = {}

    # Get IAM boto3 client
    client_iam = boto3.client(
        "iam",
        aws_access_key_id=config.ACC_KEY,
        aws_secret_access_key=config.SEC_KEY
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


def getAWS():

    dateNow = dt.datetime.now()
    year = dateNow.strftime("%Y")
    month = dateNow.strftime("%m")
    next_month = int(month)+1

    currentMonth_json = dateNow.strftime("%m-%Y")
    currentMonth = "%s%s01-%s0%s01" % (year,month,year,next_month)

    current_path = ("/sb-cern-aws/" + currentMonth + "/sb-cern-aws-Manifest.json")


    ###### Create a boto3 client that allows you to programmatically use the S3 service:
    print("Source code updated")
    client_s3 = boto3.client(
            "s3",
            aws_access_key_id=config.ACC_KEY,
            aws_secret_access_key=config.SEC_KEY,
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
    df = pd.read_csv(local_path + '/file.csv',usecols = ['lineItem/UsageStartDate',
                                                        'lineItem/UsageAccountId',
                                                        'lineItem/UnblendedCost',
                                                        'product/location',
                                                        'product/region'])
    #df.rename(columns = {'product/region':'productregion'}, inplace = True)
    #df[['continent','country']] = df['productlocation'].str.split('(', expand=True)
    #df[['region','city']]= df.productlocation.str.split('\(|\)', expand=True).iloc[:,[0,1]]
    #df[['continent','direction']]= df.region.str.split(' ', expand=True).iloc[:,[0,1]]

    #df.loc[df['productregion'] == 'us-east-2', 'productregion'] = 'US'

    df['product/region'] = df['product/region'].replace(['us-east-2','us-east-1','us-west-1','us-west-2','af-south-1','ap-east-1','ap-southeast-3','ap-south-1','ap-northeast-3','ap-northeast-2','ap-southeast-1','ap-southeast-2','ap-northeast-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-south-1','eu-west-3','eu-north-1','me-south-1','sa-east-1','us-gov-east-1','us-gov-west-1'],
                                                      ['US','US','US','US','ZA','HK','ID','IN','JP','KR','SG','AU','JP','CA','DE','IR','GB','IT','FR','SE','BH','BR','US','US'])
    ###### Filter data: take only the consumption from the last 24 hours
    period = 48
    df["lineItem/UsageStartDate"] = pd.to_datetime(df["lineItem/UsageStartDate"]).dt.tz_localize(None)
    startTime = (dt.datetime.now()-dt.timedelta(hours=period))
    latestConsumption = (df[df['lineItem/UsageStartDate'] >= startTime])

    ###### Group by UsageAccountId (projects) and sum: the sum is done for all the columns that contain numbers. The others are left out
    AmountPerId = latestConsumption.groupby('lineItem/UsageAccountId').sum()
    LocationPerId = latestConsumption.groupby('product/region').count()
    ###### Use the function getGroups() to get a dictionary containing properties, groupdID:name
    projects_dict = getGroups()

    ###### Rename the DataFrame's row names: replace each project ID with its name
    AmountPerId = AmountPerId.rename(projects_dict, axis='index')
    ###### Convert the obtained DataFrame to dict
    AmountPerId_dict = AmountPerId.to_dict()["lineItem/UnblendedCost"]
    LocationPerId_dict = LocationPerId.to_dict()["lineItem/UnblendedCost"]
    ###### Structure data as needed
    #AWS_data = {
    #           "amountSpent": AmountPerId_dict, "location": LocationPerId_dict
    #          }

    return {"amountSpent": AmountPerId_dict, "location": LocationPerId_dict}
