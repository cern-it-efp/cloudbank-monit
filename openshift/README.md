# Openshift Deployment

This folder contains the YAML file(s) that should be used to deploy all the resources to Openshift 4:

- CERN SSO
- Grafana
- Prometheus
- AWS Exporter
- GCP Exporter

The original template (Grafana + CERN SSO) for Openshift 3 can be seen [here](https://gitlab.cern.ch/db/grafana-openshift/-/tree/master/templates).

## Openshift 4

Follow the steps below to deploy the cloudbank-monit application on Openshift, using the resources provided in this repository.

### Deployment Steps

### 1. Create project

If not yet done, create project as Administrator.

### 2. Delete existing resources

Delete existing resource that may conflict with cloudbank-monit's if any, via UI or using the commands in the section below.

### 3. Deploy

To deploy from the UI, switch to Developer. Using the template allows to make use of parameters. After creating the template, search for it in the catalog and create from there. Fill in the the variables to configure the template (refer to the table below).

| Variable      | Description   |
| ------------- | ------------- |
| ADMIN_USER    | CERN username of the admin of the Grafana instance. It can be only one. |
| AUTHORIZED_GROUPS | E-group(s) with Viewer access to the Grafana instance. It can be more than one if separated by spaces.  |
| ADMIN_PASSWORD| Please leave blank: a random password will be generated. Admin password is useless when using SSO.  |
| DB_NAME| Name of the InfluxDB database. Should be `prometheus_data`. |
| DB_USERNAME | Database username. |
| DB_PASSWORD | Database password. |
| SCRAPE_INTERVAL| Prometheus scrape interval. Should be in in seconds and following the format `*s`, for example `30s` |
| SCRAPE_TIMEOUT| Prometheus scrape timeout. Should be in in seconds and following the format `*s`, for example `30s` |
| AWS_EXPORTER_ACC_KEY | AWS access key. |
| AWS_EXPORTER_SEC_KEY | AWS secret key. |
| EXPORTER_IMAGE | Indicates what Docker image to use. Leave blank for the production Openshift project, use `dev` for the development one. |
| GCP_AUTH | Content of GCP's authentication JSON file. |

It is also possible to deploy making use of Openshift's CLI with the following command:

```bash
oc create -f PATH_TO_RESOURCES_DEFINITION.yaml
```

### 4. Check deployment

On the UI, switch to Administrator to see the pods (under Workloads), networking, etc. Otherwise, you can check the deployment with the following command:

```bash
oc get all
```

### 5. Allow external access

Remove networking annotation to allow access from outside CERN (https://paas.docs.cern.ch/5._Exposing_The_Application/2-network-visibility/)

### 6. Configure Grafana

If the previous steps completed successfully, all the components should be correctly running and the platform reachable. Now it's time to create Grafana's datasource and dashboard. For that follow the indications [here](../grafana).

## Users

To add users to a project in Openshift 4, go to https://paas.cern.ch/k8s/cluster/projects/PROJECT_NAME/roles and click on "Create binding". Under "Suject name" specify a CERN username.

## Openshift CLI

You can get Openshift's CLI [here](https://github.com/openshift/okd/releases/).

#### Login

Browse to https://oauth-openshift.paas.cern.ch/oauth/token/display to get the token.

```bash
oc login --token=TOKEN --server=https://api.paas.okd.cern.ch
```

#### List projects
```bash
oc projects
```

#### Switch project
```bash
oc project PROJECT_NAME
```

#### List pods
```bash
oc get pods
```

#### List all resources
```bash
oc get all
```

#### Delete resources
```bash
oc delete dc --all # Delete all DeploymentConfig
oc delete Deployments --all # Delete all Deployments
oc delete services --all # Delete all Service
oc delete route --all # Delete all Route
oc delete cm --all # Delete all ConfigMap
oc delete pvc --all # Delete all PersistentVolumeClaim
oc delete OidcReturnURI --all # Delete all OidcReturnURI
```
