import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)


def handler(event, context):
    for record in event["Records"]:
        # Parse the list from the SQS message
        body = json.loads(record["body"])

        # Process each item in the list
        for item in body:
            # Add a record to DynamoDB
            table.put_item(
                Item={
                    "id": item,  # Use the item as the id, or generate a unique id
                    "data": "Some data for " + item,
                }
            )

    return {"statusCode": 200, "body": json.dumps("Processing complete")}
