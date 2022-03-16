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

    og_query = ("SELECT"
                    " cost,"
                    " sku.description AS sku_description,"
                    " system_labels, project.id AS project_id,"
                    " usage_start_time,"
                    " usage_end_time"
         	  " FROM %s"
         	  " WHERE project.id IS NOT NULL"
              "%s"
        	  " AND project.id!=\"billing-cern\""
        	  " ORDER BY project.id, usage_start_time" % (table, periodFilter))

    return ("SELECT"
                    " cost,"
                    " sku.description AS sku_description,"
                    " system_labels,"
                    " project.id AS project_id,"
                    " usage_start_time,"
                    " usage_end_time,"
                    " location.country AS location,"
                    " service.description AS service,"
                    " c.amount"

         	  " FROM %s, UNNEST(credits) as c"
         	  " WHERE project.id IS NOT NULL"
              " AND usage_start_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)"
        	  " AND project.id!=\"billing-cern\""
        	  " ORDER BY project.id, usage_start_time" % table)


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


def getGCP_og():
    """Get the Google credit/consumption data and process it, grouping by
       project. The fields the objects returned by this function have depend
       on the SELECT query defined above.

    Returns:
       obj: The data retrieved from Google, grouped by project.
    """

    # Get the RAW data from Google's BigQuery, sorted by project ID
    query_job = bigquery.Client().query(getQuery())

    data_by_project = []
    processed_projects = []

    # For earch row in the RAW data...
    for row in query_job:

        if row.project_id not in processed_projects:

            # This is only run when moving to a different project (row[i].projectID != row[i-1].projectID) # TODO: what if there's only one project in the results?
            if len(processed_projects) > 0:
                # Append to results
                project_data = {}
                project_data["CPUh"] = sumCores
                project_data["GPUh"] = 0
                project_data["amountSpent"] = sumCost
                project_data["memoryMB"] = sumMemory
                project_data["month"] = usage_start_time.strftime("%m-%Y")
                project_data["numberVM"] = sumVM
                project_data["projectid"] = currentProjectID
                data_by_project.append(project_data)

            sumVM = 0
            sumMemory = 0
            sumCores = 0
            sumGPUh = 0
            sumCost = 0

        currentProjectID = row.project_id

        # Update cost per project
        sumCost += row.cost

        usage_start_time = row.usage_start_time
        usage_end_time = row.usage_end_time

        if "GPU" in row.sku_description:
            sumGPUh += (usage_end_time - usage_start_time).seconds//3600

        system_labels = row.system_labels # cores, machine_spec, memory
        if len(system_labels) > 0:

            for label in system_labels:
                if "cores" in label["key"]:
                    sumCores += int(label["value"])
                #elif "machine_spec" in label["key"]:
                #    machine_spec = label["value"]
                elif "memory" in label["key"]:
                    sumMemory += int(label["value"])

        # Keep control of what projects have already been processed
        processed_projects.append(row.project_id)

    project_data = {}
    project_data["CPUh"] = sumCores
    project_data["GPUh"] = sumGPUh
    project_data["amountSpent"] = sumCost
    project_data["memoryMB"] = sumMemory
    project_data["month"] = usage_start_time.strftime("%m-%Y")
    project_data["numberVM"] = sumVM
    project_data["projectid"] = currentProjectID
    data_by_project.append(project_data)

    # Reorganise data and return
    return reorganise(data_by_project)


def getGCP():
    """Get the Google credit/consumption data of the last 24 hours and process
       it, grouping by project.

    Returns:
       obj: The data retrieved from Google, grouped by project.
    """

    # Get the RAW data from Google's BigQuery, sorted by project ID
    client = bigquery.Client()


    dataframe = (
        client.query(getQuery())
        .result()
        .to_dataframe(
            # Optionally, explicitly request to use the BigQuery Storage API. As of
            # google-cloud-bigquery version 1.26.0 and above, the BigQuery Storage
            # API is used by default.
            create_bqstorage_client=True,
        )
    )
    dataframe['Final_cost'] = dataframe['cost'] + dataframe['amount']
    AmountPerId = dataframe.groupby('project_id').sum("Final_cost")

    AmountPerId_dict = AmountPerId.to_dict()["Final_cost"]

    NumPerLocation = dataframe.groupby('location').count()

    locationPerId_dict = NumPerLocation.to_dict()["service"]


    return {"amountSpent": AmountPerId_dict, "location": locationPerId_dict}
