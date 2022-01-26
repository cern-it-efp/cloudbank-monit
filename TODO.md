# TODO

- Investigate whether Deployment should be used over DeploymentConfig.

- Include a license.

- Repo's README should be more detailed and give a better overview not only of what this system is all about, but also about the CloudBank project itself.

- Regarding data dates: in google, the entries have two dates: usage start and usage end. What if those are in different days (not even today-tomorrow but one week from now)? Sure we can plot using usage start, but then probably the plots would not be really correct.

- Migrate to the public repo: https://github.com/cern-it-efp/cloudbank-monit

- Add logs to the exporters (after 'Serving the application on port 7979') to show some details of the requests.

- The users should not be able to modify the queries of the dashboards in principle. Otherwise, they could select data that should not be visible to them (for example, other projects'). Only admins can create datasources/dashboards, can viewer edit the dashboards though?

- Firewalling or authentication of requests should be used for the containers, to avoid anyone HTTP-querying them directly (currently there's no auth, anyone could query the exporters and the Prometheus server. But in reality only one route can be defined in Openshift so it's not possible to reach other services). In other words:
    - Only the Prometheus server should be able to query the exporters
    - The Prometheus server should not serve any request

- Configure Grafana's start page, remove what's not needed

- Refactor both AWS and GCP code: use on-dictionary replacement if possible/needed

- Use credentials with read-only permissions:
    - For AWS, key pair that can only read data from S3 and ideally, only from the bucket strategic-blue-reports-cern: DONE
    - For Google, use a token instead of a JSON file which would be able to only read data from the billing dataset from BigQuery. Did not manage to use token authentication, limited JSON's key file scope to "BigQuery Data Viewer" and "BigQuery Job User" but should limit also to only a specific dataset/table.

- Reorganize /exporters in a way that common code can be reused across exporters.

- Use logging properly, getLogger(), etc

- collector.py: the class' collect method is called on registration (so a query is indeed run), desired?

- main.py: any path works to GET the HTTP server, desired?

- The Grafana+SSO Openshift Template works, it deploys the needed resources. However, it doesn't create the "Provisioned Services" section. How to bundle all the services from the Template like the UI deployment (from the catalog) does?

- AWS's utils.py
    - There are some ID's that are not replaced (253635982411, 357458753298, 618456240250, 622943311693)
    - Add more metrics

- GCP's utils.py:
    - getQuery should allow more granular periods
    - cant filter by cost greater than 0 because some metrics that are relevant (number of MVs, memory, etc) may not be always associated with costs
    - When using '< 0' several rows are retrieved, what are those? discounts?
    - Are 'cores', 'machine_spec' and 'memory' all the possible labels at system_labels?
    - The function reorganise() puts the results in a way that is easier for collect() to create the metrics BUT that should be done inside getGCP directly
    - At reorganise(), it's assumed always 'month', but could be 'day' later
    - sumCores has nothing to do with hours but it's shown as 'CPUh'
    - For GPUh calculation: if contains "GPU" then update the time (usage_end_time - usage_start_time + sumTimeGPU)
    - Regarding querying the BQ dataset, seems like after some time it becomes slow, around 4.10 minutes. Changing IP fixes that (switch from cable to wifi), does BQ ban IPs?
    - getGCP has to be improved. Its last lines add the last project otherwise it would be processed but skipped
    - machine_spec was used to count the number of VMs but it's not correct because multiple entries can be referencing the same resource (VM). Hence, numberVM is showing numbers that do not make sense. The same applies to cores and memory, multiple rows reference the same resource. To fix that, isn't there some sort of resource ID that uniquely identities the resources?
