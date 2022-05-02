import sys
from atlassian import Confluence
import datetime
from slack_sdk import WebClient
from dotenv import dotenv_values


def get_keys():
    config = dotenv_values("keys.env")
    return config


def get_weekend_duty(confluence_user, confluence_key, confluence_page):
    confluence = Confluence(
        url="https://marshassoc.atlassian.net/wiki",
        username=confluence_user,
        password=confluence_key,  # Confluence API Token
        cloud=True,
    )

    weekend_duty = confluence.get_page_by_id(confluence_page, expand="body.view")[
        "body"
    ]["view"]["value"]

    today = datetime.datetime.now()
    today_parser = today.strftime("%B")[:3] + " " + str(today.day)

    weekend_duty = weekend_duty[
        weekend_duty.find("Upcoming") : weekend_duty.find("Historical")
    ]

    weekend_duty = weekend_duty[weekend_duty.find(today_parser) :]

    weekend_duty = weekend_duty[: weekend_duty.find("<br/>")]

    weekend_dates, names = weekend_duty.split(":")

    message = (
        "On call for "
        + weekend_dates.strip()
        + " is "
        + names.strip()
        + ". Have a great weekend!"
    )

    return message


def send_slack_message(slack_channel, slack_key, message):
    client = WebClient(token=slack_key)
    client.conversations_open(users=slack_channel)  # Currently my user ID for testing
    result = client.chat_postMessage(channel=slack_channel, text=message)


# -----------------------------------
# Triggerable Control functions (Public)
# -----------------------------------


def lambda_handler(event, context):
    params = None
    main(params)


def main(params=None):
    keys = get_keys()
    message = get_weekend_duty(
        keys["CONFLUENCE_USER"], keys["CONFLUENCE_KEY"], keys["CONFLUENCE_PAGE"]
    )
    send_slack_message(keys["SLACK_CHANNEL"], keys["SLACK_KEY"], message)


if len(sys.argv) >= 1:
    params = None
    main(params)
