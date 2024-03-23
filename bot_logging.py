import logging
import os
from logging.handlers import TimedRotatingFileHandler
import requests
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs.log",
)

main_formatter = logging.Formatter(
    "%(levelname)s => %(message)s => %(asctime)s", "%Y-%m-%d %H:%M:%S"
)


# Defining handler for Slack notifications - only errors (I activated incoming webhooks for my Slack channel - It worked:))
class SlackErrorHandler(logging.Handler):
    def __init__(self, webhook_url):
        super().__init__(level=logging.ERROR)
        self.webhook_url = webhook_url

    def emit(self, record):
        log_entry = self.format(record)
        headers = {"Content-type": "application/json"}
        payload = {"text": f"ERROR: {log_entry}"}
        # It is just for me to check if it works
        try:
            response = requests.post(
                self.webhook_url, data=json.dumps(payload), headers=headers
            )
            if response.status_code != 200:
                print(f"Error sending message to Slack: {response.text}")
        except Exception as e:
            print(f"Failed to send log to Slack: {e}")


# Excluding user-related errors messages from being sent to Slack
class SlackErrorFilter(logging.Filter):
    def filter(self, record):
        # Assuming error messages that include "Updates" are system-related
        return "updates" in record.msg.lower()


# Collecting log messages for searches that had no results
class UnsuccessfulSearchFilter(logging.Filter):
    def filter(self, record):
        return "number of results: 0" in record.msg.lower()


root_logger = logging.getLogger()

# Console Handler for INFO logs
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(main_formatter)
root_logger.addHandler(console)

# File Handler for Unsuccessful Searches, using TimedRotatingFileHandler
unsuccess = TimedRotatingFileHandler(
    "unsuccessful_searches.log", when="midnight", interval=1, backupCount=30
)
unsuccess.setLevel(logging.INFO)
unsuccess.setFormatter(main_formatter)
root_logger.addHandler(unsuccess)

# Applying the custom Unsuccessful Searches filter
unsuccess.addFilter(UnsuccessfulSearchFilter())

# File Handler for ERROR logs
file = logging.FileHandler("important_errors.log")
file.setLevel(logging.ERROR)
file.setFormatter(main_formatter)
root_logger.addHandler(file)

# Slack Handler for ERROR logs
slack = SlackErrorHandler(os.getenv("SLACK_WEBHOOK_URL"))
slack.setLevel(logging.ERROR)
slack.setFormatter(main_formatter)
root_logger.addHandler(slack)

# Applying the custom filter to the Slack handler
slack.addFilter(SlackErrorFilter())
