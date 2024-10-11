import json
import os
import boto3

sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]


def handler(event, context):
    # Your logic to generate the list
    my_list = ["item1", "item2", "item3"]

    # Send the list to table
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(my_list))

    return {"statusCode": 200, "body": json.dumps("List sent to SQS successfully")}
