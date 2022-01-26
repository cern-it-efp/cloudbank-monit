# Prometheus

To configure the Prometheus server, a YAML file is needed. Below is an example of such file, tailored for our scenario.

```yaml
global:
  scrape_interval: 30s
  scrape_timeout: 30s
scrape_configs:
- job_name: Cloud Consumpion Data Exporters
  metrics_path: /probe
  static_configs:
  - targets:
    - exportera:7979
      exporterb:7979
      exporterc:7979
remote_write:
  - url: https://dbod-cbankeu.cern.ch:8081/api/v1/prom/write?db=database
    tls_config:
      insecure_skip_verify: true
    basic_auth:
      username: username
      password: password1234
```

In our setup this file is provided to the Prometheus server (which runs inside an Openshift/Kubernetes pod) as a [ConfigMap](../openshift/complete.yaml).

Refer to the folder [exporters](exporters) for more information specific to the exporters.
