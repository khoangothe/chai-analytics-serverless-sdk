import datetime


def handler(event, context):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Cron job ran at {current_time}")
    return {
        "statusCode": 200,
        "body": f"Cron job executed successfully at {current_time}",
    }
