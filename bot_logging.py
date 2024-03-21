import logging
import os
from logging.handlers import TimedRotatingFileHandler
import requests
import json


# Configuring basic logging with a specified file and format
main_formatter = logging.Formatter(
    "%(levelname)s => %(message)s => %(asctime)s", "%Y-%m-%d %H:%M:%S"
)

logging.basicConfig(
    level=logging.INFO,
    filename="logs.log",
    format="%(name)s => %(levelname)s => %(message)s",
)


# Defining handler for Slack notifications(I activated incoming webhooks for my Slack channel - It worked:))
class SlackErrorHandler(logging.Handler):
    def __init__(self, webhook_url):
        super().__init__(level=logging.ERROR)
        self.webhook_url = webhook_url

    def emit(self, record):
        log_entry = self.format(record)
        headers = {"Content-type": "application/json"}
        payload = {"text": f"ERROR: {log_entry}"}
        # It is just for me to know if it works
        try:
            response = requests.post(
                self.webhook_url, data=json.dumps(payload), headers=headers
            )
            if response.status_code != 200:
                print(f"Error sending message to Slack: {response.text}")
        except Exception as e:
            print(f"Failed to send log to Slack: {e}")


# Excluding specific log messages: it ignores debug logs from being sent to Slack
class SomeLogFilter(logging.Filter):
    def filter(self, record):
        return not record.levelno == logging.DEBUG


# Console Handler for INFO logs
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(main_formatter)

# File Handler for ERROR logs, using TimedRotatingFileHandler
file = TimedRotatingFileHandler(
    "important_errors.log", when="midnight", interval=1, backupCount=7
)
file.setLevel(logging.ERROR)
file.setFormatter(main_formatter)

# Slack Handler for ERROR logs
slack = SlackErrorHandler(os.getenv("SLACK_WEBHOOK_URL"))
slack.setLevel(logging.ERROR)
slack.setFormatter(main_formatter)

root_logger = logging.getLogger()
root_logger.addHandler(console)
root_logger.addHandler(file)
root_logger.addHandler(slack)

# Applying the custom filter to the Slack handler
slack.addFilter(SomeLogFilter())
