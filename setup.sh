#!/bin/bash

# Updated: Enhanced comment for clarity
echo "Installing required Python packages and setting up DynamoDB tables..."

# Installing dependencies
pip3 install boto3

# Python script to create DynamoDB tables
python3 - <<EOF
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Creating Users table
try:
    table = dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {'AttributeName': 'email', 'KeyType': 'HASH'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    print("Users table created successfully.")
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("Users table already exists.")
    else:
        raise e

# Creating Events table
try:
    table = dynamodb.create_table(
        TableName='Events',
        KeySchema=[
            {'AttributeName': 'event_id', 'KeyType': 'HASH'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'event_id', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    print("Events table created successfully.")
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("Events table already exists.")
    else:
        raise e

# Creating RSVPs table
try:
    table = dynamodb.create_table(
        TableName='RSVPs',
        KeySchema=[
            {'AttributeName': 'event_id', 'KeyType': 'HASH'},
            {'AttributeName': 'email', 'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'event_id', 'AttributeType': 'S'},
            {'AttributeName': 'email', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    print("RSVPs table created successfully.")
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("RSVPs table already exists.")
    else:
        raise e

# Creating Feedback table
try:
    table = dynamodb.create_table(
        TableName='Feedback',
        KeySchema=[
            {'AttributeName': 'event_id', 'KeyType': 'HASH'},
            {'AttributeName': 'email', 'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'event_id', 'AttributeType': 'S'},
            {'AttributeName': 'email', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    print("Feedback table created successfully.")
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("Feedback table already exists.")
    else:
        raise e

# Updated: Added Attendance table for tracking attendance
try:
    table = dynamodb.create_table(
        TableName='Attendance',
        KeySchema=[
            {'AttributeName': 'event_id', 'KeyType': 'HASH'},
            {'AttributeName': 'email', 'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'event_id', 'AttributeType': 'S'},
            {'AttributeName': 'email', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    print("Attendance table created successfully.")
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("Attendance table already exists.")
    else:
        raise e

# Updated: Added CommunicationLog table for communication oversight
try:
    table = dynamodb.create_table(
        TableName='CommunicationLog',
        KeySchema=[
            {'AttributeName': 'log_id', 'KeyType': 'HASH'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'log_id', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    print("CommunicationLog table created successfully.")
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("CommunicationLog table already exists.")
    else:
        raise e

print("DynamoDB table setup complete.")
EOF

# Removed: Self-referential chmod +x (should be applied after script creation)
echo "Setup script execution completed. Ensure execute permissions are set (chmod +x setup.sh) if not already done."
