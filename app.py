import json 
import sys 
import time 
import random 
from datetime import datetime, timezone 
import socket 
import boto3 
from botocore.exceptions import ClientError 

LEVELS = ["INFO", "WARNING", "ERROR", "DEBUG"] 
MESSAGES = { "INFO": "Service running normally", 
            "WARNING": "CPU usage is slightly high", 
            "ERROR": "Failed to connect to database", 
            "DEBUG": "Debugging application flow" } 

# For logstash connection 
LOGSTASH_HOST = "172.31.3.134" 
LOGSTASH_PORT = 5044 

sequence_token = None

# For AWS CloudWatch Logs 
AWS_REGION = "us-east-1" 
LOG_GROUP = "/shahid/python-app" 
LOG_STREAM = "shahid-stream" 

client = boto3.client("logs", region_name=AWS_REGION) 

def init_cloudwatch(): 
    """Ensure log group and stream exist""" 
    global sequence_token 
    try: 
        client.create_log_group(logGroupName=LOG_GROUP) 
    except ClientError as e: 
        if e.response["Error"]["Code"] != "ResourceAlreadyExistsException": 
            raise 
    try: 
        client.create_log_stream( 
            logGroupName=LOG_GROUP, 
            logStreamName=LOG_STREAM
        ) 
    except ClientError as e: 
        if e.response["Error"]["Code"] != "ResourceAlreadyExistsException": 
            raise 
            
    # fetch sequence token if stream already exists 
    streams = client.describe_log_streams( 
        logGroupName=LOG_GROUP, 
        logStreamNamePrefix=LOG_STREAM 
    ) 
    if streams["logStreams"]: 
        sequence_token = streams["logStreams"][0].get("uploadSequenceToken") 
        
def send_to_cloudwatch(log): 
    """Send log event to CloudWatch Logs""" 
    global sequence_token 
    event = { "timestamp": int(time.time() * 1000), 
               "message": json.dumps(log) 
        } 
    kwargs = { 
        "logGroupName": LOG_GROUP, 
        "logStreamName": LOG_STREAM, 
      "logEvents": [event] 
    
    } 
    if sequence_token: 
        kwargs["sequenceToken"] = sequence_token 
    try: 
        response = client.put_log_events(**kwargs) 
        sequence_token = response["nextSequenceToken"] 
    except ClientError as e: 
        print(f"CloudWatch send failed: {e}", file=sys.stderr) 
        
        
        
def send_to_logstash(log): 
    try: 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sock.connect((LOGSTASH_HOST, LOGSTASH_PORT)) 
        sock.sendall((json.dumps(log) + "\n").encode("utf-8")) 
        sock.close() 
    except Exception as e: 
        print(f"Logstash send failed: {e}", file=sys.stderr) 

        
if __name__ == "__main__": 
    init_cloudwatch() 
    
    while True: 
        level = random.choice(LEVELS) 
        log = { "timestamp": datetime.now(timezone.utc).isoformat(), 
               "level": level, 
               "service": "shahid", 
               "message": MESSAGES[level] 
               } 
        send_to_cloudwatch(log) 
        send_to_logstash(log) 
        time.sleep(4)

