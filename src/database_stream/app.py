import os
import json
import logging

import boto3

log = logging.getLogger('database-streaming')
log.setLevel(logging.DEBUG)

try:
    REGION_NAME = os.environ['AWS_REGION']
    log.info(f'Going to use region name {REGION_NAME}')
except KeyError:
    log.warning("No AWS_REGION environment variable defined, using default 'eu-central-1'")
    REGION_NAME = 'eu-central-1'

def lambda_handler(event, context):

    log.debug(event)
    
    try:
        SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
        log.info(f'Going to use topic {SNS_TOPIC_ARN}')
    except KeyError:
        log.error("No SNS_TOPIC_ARN environment variable defined, calls will fail with error code 500")
        response = {
            'status' : 'ERROR, no SNS_TOPIC_ARN environment variable defined'
        }
        return response

    try: 
        batch_size = len(event['Records'])
        insert_count = 0
        message = ""
        for r in event['Records']:
            if r['eventName'] == 'INSERT':
                insert_count += 1
                data = r['dynamodb']['NewImage']
                message = message + f"Page :\t{data['pk']['S']}\nName :\t{data['name']['S']}\nEmail :\t{data['sk']['S']}\n\n"

        if message != "":
            plural = 's' if insert_count > 1 else ''
            subject = f"You have {insert_count} new subscription{plural}"
            message = message + "\nSent with ❤️ from the ☁️"

            profile = os.environ['UNIT_TEST_PROFILE'] if 'UNIT_TEST_PROFILE' in os.environ else None
            session = boto3.Session(region_name=REGION_NAME, profile_name=profile)
            client = session.client('sns')
            client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject=subject
            )

    except Exception as e: 
        log.error("Can not post message to topic")
        log.exception(e)
        response = {
            'status' : 'ERROR, can not post message to topic',
            'exception': repr(e)
        }
        return response

    response = {
        'status' : 'OK',
        'batchSize' : batch_size,
        'messages' : insert_count
    }
    log.debug(response)

    return response
