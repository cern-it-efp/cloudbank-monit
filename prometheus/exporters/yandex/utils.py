#!/usr/bin/env python3


import boto3
import json
import csv
import gzip
import shutil
import pandas as pd
import numpy as np
import json
import datetime
import config
import yandexcloud
from yandex.cloud.resourcemanager.v1.folder_service_pb2 import ListFoldersRequest
from yandex.cloud.resourcemanager.v1.folder_service_pb2_grpc import FolderServiceStub

today = datetime.date.today()

yesterday = today - datetime.timedelta(days=1)

yesterday = yesterday.strftime('%Y%m%d')

file = (yesterday + ".csv")

#local_path = "C:/Users/atheodor/AppData/Local/Temp"
local_path = "/tmp"

client_s3 = boto3.client(
        "s3",
	aws_access_key_id=config.ACC_KEY,
        aws_secret_access_key=config.SEC_KEY,

        endpoint_url = "https://storage.yandexcloud.net"
        #region_name="us-east-2" # compulsory
    )

client_s3.download_file('cern-billing',
                        file,
			local_path + '/file'
                        )

def get_folders():
    cloudID = "b1gv4hq5u08rjf91v2an"
    auth_path = "/tmp/key.json"

    folder_service = yandexcloud.SDK(service_account_key=json.load(open(auth_path,"r"))).client(FolderServiceStub)

    cloud_folders = folder_service.List(ListFoldersRequest(cloud_id=cloudID)).folders

    folderlist=[]

    for folders in cloud_folders:
        folderlist.append(folders.name)

    return folderlist

def get_yandex():

    df = pd.read_csv(local_path + '/file', usecols = ['billing_account_id','folder_name','cost'])

    AmountPerId = df.groupby('folder_name').sum()

    AmountPerId_dict = AmountPerId.to_dict()["cost"]

    list_of_folders_inCSV = list(AmountPerId_dict.keys()) # List of folders in the CSV

    for folder in get_folders() :
        if folder not in list_of_folders_inCSV:
        #    print("This folder is missing: %s " % folder)
            AmountPerId_dict[folder] = 0 # Add missing folder

    YDX_data = {
                    "amountSpent": AmountPerId_dict
           }


    return YDX_data

print(get_yandex())
print(file)
