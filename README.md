# cloudbank-monit

Platform for cloud services usage and consumption monitoring in the scope of the [CloudBankEU project](https://ngiatlantic.eu/funded-experiments/cloudbank-eu-ngi).

This is an Open Source project licensed under X, developed in collaboration with [UCSD](https://ucsd.edu/).

No personal data is stored in any circumstance. Only Project and Billing IDs, cost expenditure and usage per cloud service.

## Architecture

This application runs in the CERN Openshift and is conformed by the following core components:

- CERN SSO: authentication for CERN users.
- Grafana: dashboards displaying the data.
- Prometheus: scrapes data from the exporters.
  - AWS Exporter: gets billing data from AWS's reports (CSV files on S3).
  - GCP Exporter: gets billing data from GCP's BigQuery.
- InfluxDB: data persistence.

The architecture can be seen here: https://docs.google.com/drawings/d/1ISj875a-NIbcUbeLoM_zsnIOGmBgAniiuhPbJaJDB5I

## Deployment

Refer to the [Openshift](openshift) folder.

## License

Copyright (C) CERN.

Licensed under GNU Affero General Public License.


