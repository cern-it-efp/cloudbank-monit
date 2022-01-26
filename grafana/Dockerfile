FROM gitlab-registry.cern.ch/db/grafana-openshift:latest

RUN yum install wget unzip -y
RUN wget https://storage.googleapis.com/plugins-community/grafana-worldmap-panel/release/0.3.3/grafana-worldmap-panel-0.3.3.zip

RUN mkdir -p /usr/share/grafana/data/plugins
RUN unzip grafana-worldmap-panel-0.3.3.zip -d /usr/share/grafana/data/plugins
 
ENTRYPOINT ["./run.sh"]
