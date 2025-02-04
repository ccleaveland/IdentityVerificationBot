import json
import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import messaging
from verification_flow import VerificationThread

#
# Methods and variables related to Slack listeners
#

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token = SLACK_BOT_TOKEN, name = "Identity Verification Bot")

# Example flow:
# /verify-user @User1 @User2
# [submitted by User3]

# Retrieve slack ids from slash command parameter and submitting user
    # DM submitting user if parameter is invalid or missing
# DM all users to verify they are communicating and to respond via Okta push notification.
    # Provide a way to report suspected malicious activity to security (if communication isn't occurring)
# Send Okta push notification to all users
# Post results to the channel:
    # Confirms their identity via Okta push
    # Denies their identity via Okta push
    # The Okta request times or errors out
    # Clicks to report suspected malicious activity (verifies they are NOT communicating with you)

@app.command("/verify-user")
def start_verification(ack, body):
    ack()
    requesting_user_id = body["user_id"]
    users_to_verify = re.findall("@(.+?)\|", body["text"])
    
    if not users_to_verify:
        # Send error message for invalid paramaters
        messaging.post_message(app, requesting_user_id, messaging.INVALID_COMMAND_FORMAT_ERROR_MSG)
    else:
        # Start verification flow
        channel_id = app.client.conversations_open(users = f"{requesting_user_id},{','.join(users_to_verify)}")["channel"]["id"]
        messaging.post_instruction_message(app, channel_id, requesting_user_id, users_to_verify)

        # Retrieve email for Okta
        slack_id_to_email_map = {}
        for slack_id in (users_to_verify + [requesting_user_id]):
            email = app.client.users_info(user = slack_id)["user"]["profile"]["email"]
            slack_id_to_email_map[slack_id] = email
        
        # Perform Okta verification for all users
        threads = []
        for slack_id, email in slack_id_to_email_map.items():
            thread = VerificationThread(app, channel_id, slack_id, email)
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()


@app.action("report_incident")
def handle_incident_report(ack, body):
    ack()
    channel_id = body["channel"]["id"]
    app.client.views_open(view = {
			"title": {
			"type": "plain_text",
			"text": "Report Incident"
				},
				"submit": {
					"type": "plain_text",
					"text": "Submit",
				},
				"blocks": json.dumps(messaging.INCIDENT_REPORT_MODAL),
				"type": "modal",
				"callback_id": "incident_report_submission",
				"private_metadata": channel_id
	}, trigger_id = body["trigger_id"])


@app.view("incident_report_submission")
def handle_incident_report_submission(ack, body):
    ack()
    channel_id = body["view"]["private_metadata"]
    blocks = [
         {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": messaging.build_incident_reported_message(body['user']['id'])
			}
		},
	]
    app.client.chat_postMessage(channel = channel_id, text = "Thank you for your report.", blocks = blocks)


def main():
    SocketModeHandler(app, SLACK_APP_TOKEN).start()


if __name__ == "__main__":
    main()