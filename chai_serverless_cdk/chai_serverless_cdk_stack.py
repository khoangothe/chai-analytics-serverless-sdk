from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
)
from constructs import Construct


class ChaiServerlessCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the Lambda function
        cron_lambda = _lambda.Function(
            self,
            "CronHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="cron_handler.handler",
            timeout=Duration.seconds(300),
        )

        # Define the CloudWatch Event Rule
        rule = events.Rule(
            self, "CronRule", schedule=events.Schedule.rate(Duration.minutes(1))
        )
        # Add the Lambda function as a target for the CloudWatch Event Rule
        rule.add_target(targets.LambdaFunction(cron_lambda))
