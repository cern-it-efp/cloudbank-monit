#!/usr/bin/env python3

import json
import time
import os
from google.cloud import bigquery
from enum import Enum
import sys


BQtable =  "sbsl_cern_billing_info.gcp_billing_export_v1_012C54_B3DAFC_973FAF"
Period = Enum('Period', 'DAY MONTH')

def getQuery(table=BQtable, period=Period.DAY):
    """ Returns the SELECT query for the given table.

    Parameters:
        table (str): BigQuery table to query. Defaults BQtable.
        period (enum): Period to use - current month or current day (default).

    Returns:
        str: BigQuery query, ready to be used by the client.
    """

    if period == Period.MONTH:
        periodFilter = (" AND EXTRACT(MONTH FROM usage_start_time) = EXTRACT(MONTH FROM CURRENT_DATE()) "
                        " AND EXTRACT(YEAR FROM usage_start_time) = EXTRACT(YEAR FROM CURRENT_DATE()) ")
    else:
        periodFilter = (" AND EXTRACT(DAY FROM usage_start_time) = EXTRACT(DAY FROM CURRENT_DATE()) "
                        " AND EXTRACT(MONTH FROM usage_start_time) = EXTRACT(MONTH FROM CURRENT_DATE()) "
                        " AND EXTRACT(YEAR FROM usage_start_time) = EXTRACT(YEAR FROM CURRENT_DATE()) ")

    return ("SELECT"
                    " cost,"
                    " project.id AS project_id,"
                    " usage_start_time,"
                    " usage_end_time"
         	  " FROM %s"
         	  " WHERE project.id IS NOT NULL"
              "%s"
        	  " AND project.id!=\"billing-cern\""
              " AND cost > 0"
        	  " ORDER BY project.id, usage_start_time" % (table, ""))
              # TODO: should not filter by cost greater than 0
              # " AND project.id=\"it-openlab-cern\" OR project.id=\"it-db-sas-cern\""



def reorganise(results):
    """ Reorganises the data in a way that can be easily processed in the
        exporter's collect method.

    Parameters:
        results (obj): data retrieved from GCP's BigQuery

    Returns:
        obj: The object after its reorganisation.
    """

    example = results[0]
    resultsNew = {}

    for key, value in example.items():
        if key == "month":
            resultsNew[key] = value
        elif key != "projectid":
            resultsNew[key] = {}

    for projectMetrics in results:
        projectid = projectMetrics["projectid"]
        for key, value in projectMetrics.items():
            if key != "month" and key != "projectid":
                resultsNew[key][projectid] = value

    return resultsNew


def getGCP():
    """Get the Google credit/consumption data and process it, grouping by
       project. The fields the objects returned by this function have depend
       on the SELECT query defined above.

    Returns:
       obj: The data retrieved from Google, grouped by project.
    """

    # Get the RAW data from Google's BigQuery, sorted by project ID
    query_job = bigquery.Client().query(getQuery())

    data_by_project = {}

    # For earch row in the RAW data...
    for row in query_job:

        usage_start_time_unix_day = row.usage_start_time.replace(minute=59, hour=23, second=59).timestamp() * 1000000000
        if row.project_id not in data_by_project:
            data_by_project[row.project_id] = {}

        if usage_start_time_unix_day not in data_by_project[row.project_id]:
            data_by_project[row.project_id][usage_start_time_unix_day] = 0

        data_by_project[row.project_id][usage_start_time_unix_day] += row.cost


    return data_by_project

data = getGCP()
with open('dataGCP', 'a') as file:
    for project, value in data.items():
        for timestamp_day , consumption in value.items():
            file.write("amountSpent,projectid=%s,platform=GCP value=%s %s\n" % (project, consumption, int(timestamp_day)))
