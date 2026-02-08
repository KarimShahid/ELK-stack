# ELK + CloudWatch Logging Project

## Overview

This project demonstrates a centralized logging setup using the **Elastic Stack (ELK)** with **AWS CloudWatch** integration. Logs generated from a Python application are sent both to **Logstash** (for Elasticsearch/Kibana visualization) and to **AWS CloudWatch Logs**.

---

## Components

### 1. Elastic Stack (ELK)

- **Elasticsearch**: Stores and indexes log data.
- **Logstash**: Receives logs from external applications, applies parsing/filtering, and forwards them to Elasticsearch.
- **Kibana**: Visualizes and analyzes the log data.
- **Filebeat**: Lightweight log shipper (optional in this setup).

### 2. Python Log Generator

- **Application**: `app.py` continuously generates log messages with random log levels (`INFO`, `WARNING`, `ERROR`, `DEBUG`).
- **Output**:
  - Sends logs to Logstash over TCP (JSON format).  
  - Sends logs to AWS CloudWatch Logs using `boto3`.
- **Dockerized** for easy deployment using `Dockerfile` and `docker-compose.yml`.

**CloudWatch Integration:**

- Log group: `/shahid/python-app`  
- Log stream: `shahid-stream`  

### 3. AWS Setup

- **EC2 Instance**: Hosts ELK stack and Python application.  
- **Security Groups**: Configured to allow TCP connections to Logstash (port `5044`) and web access to Kibana (port `5601`).  
- **Docker & Docker Compose**: Installed to run the Python log generator container.

### 4. Kibana Visualization

- Created **Data Views** in Kibana to explore the logs ingested via Logstash.
- Logs can be filtered and visualized in **Discover** and **Dashboard** sections of Kibana.

---

## Summary

This setup provides a complete logging pipeline:

1. Python application generates logs.
2. Logs are sent to **Logstash** → stored in **Elasticsearch** → visualized in **Kibana**.
3. Logs are also sent to **AWS CloudWatch Logs** for centralized monitoring in AWS.  

It allows real-time log analysis, monitoring, and easy integration with AWS services.

