# InfluxDB

## Data Schema

For the initial data (consumption per project), the decided data schema is (shown with an example):

`amountSpent,projectid=it-openlab-cern,platform=GCP value=82.9842249 1622591999000000000`

The initial string, `amountSpent` indicates the database measurement.

The tags are projectid and platform and only the amount spent is a value field. The reason behind that decision is that tags are indexed while fields are not. According to the [official docs](https://docs.influxdata.com/influxdb/v1.8/concepts/key_concepts/), in general, fields should not contain commonly-queried metadata.

The Integer at the end of the line is a timestamp in Unix time - nanoseconds since January 1, 1970 UTC. That timestamp is optional, If you do not specify a timestamp, InfluxDB uses the server’s local nanosecond timestamp in Unix epoch. Time in InfluxDB is in UTC format by default.

For the past data, we use that timestamp for the consumption day. For the new data, the prometheus server will push the daily consumption, so the influxDB generated timestamp would be enough, no need to supply a timestamp on each line.

## Historical Data

To get the historical data from the providers use the scripts `AWS_past_data_daily.py` and `GCP_past_data_daily.py`.

The files those script generate can then be used to push data to the database.


## Client

To work with the DB (to push the historical data for example) use InfluxDB's Docker container as the client.

#### Start container

Start the container. Note v1.8.3 is used, to match CERN's (version 2 client has conflicts).

```bash
docker run -p 8086:8086 influxdb:1.8.3
```

On a different terminal, connect to the container as follow.

```bash
docker ps # get container ID
docker exec -it CONTAINER_ID bash
```

#### Connect to database

Once inside the container, connect to the database with the following command. Note this can only be done from the CERN network.

```bash
influx --username username --password password --ssl -host dbod-cbankeu.cern.ch -port 8081 --unsafeSsl
```

## Useful Commands

#### Create database
```bash
create database billing
```

#### Returns a list of all databases on my instance
```bash
show databases
```

#### Use a specific database
```bash
use billing
```

#### Returns a list of measurements for the specified database. (NOTE: each metric will be a measurement)
```bash
show measurements on billing
```

#### Insert data with timestamp to local DB
```bash
curl -i -XPOST 'http://localhost:8086/write?db=billing' --data-binary 'billing,project=projectE,day=2021-06-14T00:00:00Z,platform=AWS consumption=2.00 1000'
```

#### Insert data from local file to local DB
```bash
curl -i -XPOST 'http://localhost:8086/write?db=billing' --data-binary @records
```

#### Insert data from local file to remote DB
```bash
curl -ik -XPOST 'https://dbod-cbankeu.cern.ch:8081/api/v2/write?bucket=billing' --header 'Authorization: Token username:password'  --data-binary @recordsGCP_full
```

#### See data (here a "measurement", seen with "show measurements" has to be used)
```bash
SELECT * FROM "billing"
```

#### Delete series
```bash
DROP SERIES FROM billing
```

#### Delete database
```bash
drop database prometheus
```
