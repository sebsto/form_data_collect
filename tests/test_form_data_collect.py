import json
import os
import pytest
from pytest_mock import mocker

import boto3 

from src.form_data_collect import app

@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "version": "2.0",
        "routeKey": "POST /form",
        "rawPath": "/prod/form",
        "rawQueryString": "",
        "headers": {
            "accept": "text/html, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-length": "31",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "host": "vija6eqvi4.execute-api.eu-central-1.amazonaws.com",
            "origin": "http://localhost:1313",
            "referer": "http://localhost:1313/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "x-amzn-trace-id": "Root=1-5f95c31b-4be6db7b59a4652e03c932cf",
            "x-forwarded-for": "86.245.187.149",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https"
        },
        "requestContext": {
            "accountId": "401955065246",
            "apiId": "vija6eqvi4",
            "domainName": "vija6eqvi4.execute-api.eu-central-1.amazonaws.com",
            "domainPrefix": "vija6eqvi4",
            "http": {
            "method": "POST",
            "path": "/prod/form",
            "protocol": "HTTP/1.1",
            "sourceIp": "86.245.187.149",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
            },
            "requestId": "U-tsUilQFiAEMXQ=",
            "routeKey": "POST /form",
            "stage": "prod",
            "time": "25/Oct/2020:18:25:31 +0000",
            "timeEpoch": 1603650331593
        },
        "body": "cGs9bmF0YS5jb2FjaC5sYW5kaW5nX3BhZ2Umc2s9ZW1haWwmbmFtZT1zZWImZW1haWw9c2ViJTQwc3Rvcm1hY3EuY29t",
        "isBase64Encoded": True
        }

def test_happy_path(apigw_event, mocker):
    
    mocker.patch.dict(os.environ, {'TABLE_NAME':'nata-data-collection-form'})

    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret['body'])

    assert ret['statusCode'] == 200
    assert 'status' in ret['body']
    assert data['status'] == 'OK'

def test_no_table_env_var(apigw_event, mocker):
    
    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret['body'])

    assert ret['statusCode'] == 500
    assert 'error' in ret['body']
    assert 'TABLE_NAME' in data['error']

def test_happy_path_dynamodb(apigw_event, mocker):
    
    DDB_LOCAL_ENDPOINT = 'http://localhost:8000'
    mocker.patch.dict(os.environ, {'TABLE_NAME':'nata-data-collection-form'})

    session = boto3.Session(region_name='eu-central-1')
    resource = session.resource('dynamodb', endpoint_url=DDB_LOCAL_ENDPOINT)
    table = resource.Table(os.environ['TABLE_NAME'])
    table.delete_item(
        Key= {
            'pk': 'nata.coach.landing_page',
            'sk': 'seb@stormacq.com'
        }
    )

    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret["body"])

    # check response
    assert ret['statusCode'] == 200
    assert 'status' in ret['body']
    assert data['status'] == 'OK'

    # check database
    result = table.get_item(
        Key= {
            'pk': 'nata.coach.landing_page',
            'sk': 'seb@stormacq.com'
        }        
    )
    record = result['Item']
    assert 'event' in record
    assert 'name' in record
    assert record['name'] == 'seb'

    # assert "location" in data.dict_keys()
