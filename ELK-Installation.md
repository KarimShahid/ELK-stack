# ELK: Installation

**EC2 Basic Requirements** 

- At least 4GB RAM (8GB recommended)
- 2+ CPU cores

## 1. Create EC2

![Screenshot 2026-02-08 at 10.08.09 AM.png](images/Screenshot_2026-02-08_at_10.08.09_AM.png)

SG inbound rules

![Screenshot 2026-02-03 at 5.45.05 PM.png](images/Screenshot_2026-02-03_at_5.45.05_PM.png)

## 2.  Script to install ELK stack

install_elk.sh

```bash
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
```

<aside>
❗

No need to manually install jdk since Elastic stack 8+ it comes bundles with OpenJDK

</aside>

### Add execute permission and run the script

![Screenshot 2026-02-08 at 10.12.27 AM.png](images/Screenshot_2026-02-08_at_10.12.27_AM.png)

### ElasticSearch

![Screenshot 2026-02-08 at 10.19.34 AM.png](images/Screenshot_2026-02-08_at_10.19.34_AM.png)

### Logstash

![Screenshot 2026-02-08 at 10.20.43 AM.png](images/Screenshot_2026-02-08_at_10.20.43_AM.png)

### Kibana

![Screenshot 2026-02-08 at 10.19.08 AM.png](images/Screenshot_2026-02-08_at_10.19.08_AM.png)

## 3. Configuring  ElasticSearch

Resetting the userpassword

```
sudo /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -i
```

![Screenshot 2026-02-08 at 10.22.35 AM.png](images/2532d836-997f-48b8-a0f1-793d4251ae8a.png)

### Verifying the ES

```bash
# Test with SSL
curl -k -u elastic:YOUR_PASSWORD https://localhost:9200

# Or without SSL (if disabled)
curl -u elastic:YOUR_PASSWORD http://localhost:9200
```

![Screenshot 2026-02-08 at 10.26.25 AM.png](images/Screenshot_2026-02-08_at_10.26.25_AM.png)

## 4. Configuring Kibana

Resting the token

```bash

sudo /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
```

```bash
eyJ2ZXIiOiI4LjE0LjAiLCJhZHIiOlsiMTcyLjMxLjMuMTM0OjkyMDAiXSwiZmdyIjoiYzI2M2Q1ODA0YzE3MmJiZGFhOWYxYjljMzYxZWRkNzU2MTczNzllODBkZGFkOWQ3YmFlZWIyZDk5MGVmYWMxZCIsImtleSI6Ik5PS1BPNXdCbnZzLXpIUlpUTUJKOmVoTzJYVFJPbDN5UFRpWThzemtmZ0EifQ==
```

### Login Kibana

![Screenshot 2026-02-08 at 10.37.20 AM.png](images/Screenshot_2026-02-08_at_10.37.20_AM.png)

To get the verification code

```bash
sudo /usr/share/kibana/bin/kibana-verification-code
```

![Screenshot 2026-02-08 at 10.41.40 AM.png](images/Screenshot_2026-02-08_at_10.41.40_AM.png)

## 5. Editing logstash config file

```bash
sudo nano /etc/logstash/conf.d/test.conf
```

```bash
input {
tcp {
    port => 5044
    codec => json
}
}

output {
elasticsearch {
    hosts => ["https://localhost:9200"]
    user => "elastic"
    password => "****"
    ssl_enabled => true
    ssl_certificate_authorities => "/etc/logstash/certs/http_ca.crt"
    index => "kims-logs-%{+YYYY.MM.dd}"
}
stdout { codec => rubydebug }
}
```

restart Logstash

```bash
sudo systemctl restart logstash.service
```

to check the logs

```bash
sudo journalctl -u logstash -f
```