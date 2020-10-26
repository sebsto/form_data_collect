import os
import json
import logging

log = logging.getLogger('database-streaming')
log.setLevel(logging.DEBUG)

def lambda_handler(event, context):

    log.debug(event)
    
    response = {
        'status' : 'OK'
    }
    log.debug(response)

    return response
