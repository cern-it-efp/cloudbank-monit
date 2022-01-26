# Grafana

## Admins

To create datasources and dashboards `Admin` or `Editor` role is required. When deploying Grafana with CERN SSO via Openshift's catalog, it is not possible to specify more than one admin. To have multiple admins/editors:

1. Do the deployment normally with a single admin.
2. Ask the user that should be an additional admin/editor to log in on the newly provisioned Grafana.
3. Browse to `/org/users/`. The new user should be there listed.
4. Change their permission from viewer to Editor/Admin.

## Get token

Browse to /org/apikeys

## Create datasource (requires Admin token)

### Localhost

```bash
curl -XPOST -i -H "Authorization: Bearer 1234abcd" http://localhost:3000/api/datasources --data-binary @PATH_TO_DS_DEFINITION.json -H "Content-Type: application/json"
```

### Remote and behind CERN SSO

Besides the Grafana API token, the SSO cookie is needed for this. To get it use the browser's developer tools.

```bash
curl -XPOST -i \
	--cookie "YOUR_COOKIE_HERE" \
	-H "Authorization: Bearer YOUR_TOKEN_HERE" \
	-H "Content-Type: application/json" \
	--data-binary @PATH_TO_DS_DEFINITION.json \
	https://PROJECT_NAME.web.cern.ch/api/datasources
```

## Create dashboard

1. Export the manually created dashboard from the UI
2. Include it in the scaffolding JSON file, without id (or setting it to null)
3. Run:

### Localhost

```bash
curl -XPOST -i -H "Authorization: Bearer 1234abcd" http://localhost:3000/api/dashboards/db --data-binary @PATH_TO_DB_DEFINITION.json -H "Content-Type: application/json"
```

### Remote and behind CERN SSO

Besides the Grafana API token, the SSO cookie is needed for this. To get it use the browser's developer tools.

```bash
curl -XPOST -i \
	--cookie "YOUR_COOKIE_HERE" \
	-H "Authorization: Bearer YOUR_TOKEN_HERE" \
	-H "Content-Type: application/json" \
	--data-binary @PATH_TO_DB_DEFINITION.json \
	https://PROJECT_NAME.web.cern.ch/api/dashboards/db
```
