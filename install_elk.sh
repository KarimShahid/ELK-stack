#!/usr/bin/env bash
set -euo pipefail

echo "Installing Elastic Stack 9.x (Elasticsearch, Kibana, Logstash) ..."

# 1) prerequisites

sudo apt-get install -y wget gnupg apt-transport-https ca-certificates

# 2) add Elastic signing key (keyring)
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg

# 3) add Elastic repo (9.x)
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/9.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-9.x.list

# 5) install Elastic components
sudo apt-get update -y && sudo apt-get install -y elasticsearch kibana logstash filebeat 

# 6) configure Kibana to listen on all interfaces
sudo sed -i.bak '/^[[:space:]]*#server\.host:[[:space:]]*"localhost"[[:space:]]*$/a server.host: 0.0.0.0' /etc/kibana/kibana.yml

# 7) enable + start services
sudo systemctl daemon-reload
sudo systemctl enable --now elasticsearch
sudo systemctl enable --now kibana
sudo systemctl enable --now logstash
sudo systemctl enable --now filebeat

sudo mkdir -p /etc/logstash/certs
sudo cp /etc/elasticsearch/certs/http_ca.crt /etc/logstash/certs/http_ca.crt
sudo chown root:logstash /etc/logstash/certs/http_ca.crt
sudo chmod 640 /etc/logstash/certs/http_ca.crt

sudo tee /etc/logstash/conf.d/test.conf >/dev/null <<'EOF'
input {
  stdin { }
}

output {
  elasticsearch {
    hosts => ["https://localhost:9200"]
    user => "elastic"
    password => "<password>"
    ssl_enabled => true
    ssl_certificate_authorities => "/etc/logstash/certs/http_ca.crt"
    index => "logstash-test-%{+YYYY.MM.dd}"
  }
  stdout { codec => rubydebug }
}
EOF

sudo systemctl restart kibana
sudo systemctl restart logstash

echo "Done."