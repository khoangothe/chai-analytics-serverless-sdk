import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda_event_sources as lambda_event_sources,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    Duration,
)
from constructs import Construct


class ChaiServerlessCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        model_meta_table = dynamodb.Table(
            self,
            "chai_model_metada",
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # On-demand capacity mode
            # time_to_live_attribute="ttl",  # Enable TTL
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Automatically delete the table when the stack is destroyed
        )

        queue = sqs.Queue(self, "chai_model_queue")

        # Define the Lambda function
        cron_lambda = _lambda.Function(
            self,
            "CronHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="cron_handler.handler",
            timeout=Duration.seconds(300),
            environment={
                "QUEUE_URL": queue.queue_url,
            },
        )

        # Grant permission to send messages to SQS
        queue.grant_send_messages(cron_lambda)

        # Create Lambda function for processing queue messages
        process_lambda = _lambda.Function(
            self,
            "ProcessLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="process.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": model_meta_table.table_name,
            },
        )

        # Grant permission to write to DynamoDB
        model_meta_table.grant_write_data(process_lambda)

        # Add SQS as event source for process Lambda
        process_lambda.add_event_source(lambda_event_sources.SqsEventSource(queue))

        # Define the CloudWatch Event Rule
        rule = events.Rule(
            self,
            "CronRule",
            schedule=events.Schedule.rate(Duration.hours(6)),
        )
        # Add the Lambda function as a target for the CloudWatch Event Rule
        rule.add_target(targets.LambdaFunction(cron_lambda))
