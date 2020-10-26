#!/bin/bash 

# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html 

java -Djava.library.path=./dynamodb_local_latest/DynamoDBLocal_lib -jar ./dynamodb_local_latest/DynamoDBLocal.jar -sharedDb &

PID=$(jps | grep DynamoDBLocal.jar | cut -f 1 -d " ")
LOCAL_DDB="--endpoint-url http://localhost:8000"
TABLE_NAME="nata-data-collection-form"

aws dynamodb describe-table --table-name $TABLE_NAME $LOCAL_DDB
if [ $? != 0 ];
then
    echo "Creating table "
    aws dynamodb create-table --table-name $TABLE_NAME --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 $LOCAL_DDB
else 
    echo "Table already exist, ready to use"
fi

Echo "To stop DynamoDB Local, type: kill -9 $PID"