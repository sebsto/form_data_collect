import os
import json
import logging
import base64
from datetime import datetime
from urllib.parse import parse_qs

import boto3 
import botocore
import botocore.errorfactory
from boto3.dynamodb.conditions import Key, Attr

log = logging.getLogger('data-collection-form')
log.setLevel(logging.DEBUG)

try:
    REGION_NAME = os.environ['AWS_REGION']
    log.info(f'Going to use region name {REGION_NAME}')
except KeyError:
    log.warning("No AWS_REGION environment variable defined, using default 'eu-central-1'")
    REGION_NAME = 'eu-central-1'

try:
    DDB_TABLE_NAME = os.environ['TABLE_NAME']
    log.info(f'Going to use table name {DDB_TABLE_NAME}')
except KeyError:
    log.error("No TABLE_NAME environment variable defined, calls will fail with error code 500")
    DDB_TABLE_NAME = None

DDB_LOCAL_ENDPOINT = 'http://localhost:8000'

def dynamodb_resource():
    result = None 
    # check if we are running on AWS Lambda or locally (for tests)
    try:
        LAMBDA_RUNTIME = os.environ['AWS_EXECUTION_ENV']
        # we assume we're running on Lambda
        session = boto3.Session(region_name=REGION_NAME)
        result = session.resource('dynamodb')
    except KeyError:
        # env var does not exist, assume we're running locally
        log.info("We're running locally for tests.  Did you start DynamoDB local ?")
        session = boto3.Session(region_name=REGION_NAME)
        result = session.resource('dynamodb', endpoint_url=DDB_LOCAL_ENDPOINT)

    return result

# wrap in a separate function for easy mocking during tests 
# https://stackoverflow.com/questions/23988853/how-to-mock-set-system-date-in-pytest
def now():
    # return datetime.now()
    return int(datetime.utcnow().timestamp())

def write_data(event, data):

    try:
        data['created_at'] = now()
        data['event'] = event
        data['sk'] = data[data['sk']]

        table = dynamodb_resource().Table(DDB_TABLE_NAME)
        response = table.put_item(Item=data)

        log.debug(json.dumps(response))

    except botocore.exceptions.EndpointConnectionError:
        log.error("Timeout when calling DynamoDB")
        raise TimeoutError

def lambda_handler(event, context):

    log.debug(event) 

    if DDB_TABLE_NAME == None:
        response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            "isBase64Encoded": False,
            'body': json.dumps({ 'error' : 'Environment variable TABLE_NAME is not defined:'})
        }
        return response

    body = None 
    if event['isBase64Encoded']:
        body = base64.b64decode(event['body']).decode('utf-8')
    else:
        body = event['body']
 
    data = parse_qs(body)
    data = { k: v if type(v) != list else v[0] for k, v in data.items()}
    log.debug(data)

    log.debug('Writing to dynamodb')
    write_data(event, data)
    log.debug('Done writing to dynamodb')

    #TODO catch exceptions and return 500 
    
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },        
        "isBase64Encoded": False,
        'body': json.dumps({ 'status' : 'OK' })
    }
    log.debug(response)

    return response
