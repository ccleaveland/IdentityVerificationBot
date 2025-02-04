#
# Methods and variables related to messages sent to users
#

INVALID_COMMAND_FORMAT_ERROR_MSG = "To verify a user, you must specify at least one user. Ex: /verify-user @User. Please try again."

INCIDENT_REPORT_MODAL = [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "You are reporting a suspected employee impersonation attempt."
			}
		},
		{
			"type": "input",
			"block_id": "incident-details",
			"element": {
				"type": "plain_text_input",
				"multiline": True,
				"action_id": "incident-details-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Please provide details about the incident."
			}
		}
	]


def build_instruction_message(requesting_user_id, users_to_verify):
    # Format message based on number of users involved
    message = f"Verification is required to ensure <@{requesting_user_id}>"
    if len(users_to_verify) > 1:
        for user in users_to_verify[:-1]:
            message += f", <@{user}>"
        message += ","
    message += f" and <@{users_to_verify[-1]}> are currently in communication with one another.\n\nPlease confirm your identities by responding to your respective Okta push notifications. Results will be posted to this channel."
    return message


def post_instruction_message(app, channel_id, requesting_user_id, users_to_verify):
    blocks = [
		{
            "type": "section",
			"text": {
				"type": "mrkdwn",
				"text": build_instruction_message(requesting_user_id, users_to_verify)
			}
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "If you are not communicating, please report this incident to Security."
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Report Incident"
				},
				"action_id": "report_incident"
			}
		}
    ]
    app.client.chat_postMessage(channel = channel_id, blocks = blocks, text = "Please verify your identities.")


def post_message(app, channel, message):
    blocks = [
         {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": message
			}
		},
	]
    app.client.chat_postMessage(channel = channel, text = "Message", blocks = blocks)


def build_incident_reported_message(submitting_user_id):
    return f":alert: ALERT! <@{submitting_user_id}> has indicated that this is a potential impersonation attempt and has submitted a report to security. Please cease all communication immediately."


def build_okta_verified_message(user_id):
    return f":check: <@{user_id}> has been verified."


def build_okta_rejected_message(user_id):
    return f":alert: ALERT! <@{user_id}> has rejected the Okta request. Please cease all communication immediately."


def build_okta_timeout_message(user_id):
    return f":warning: The Okta request to <@{user_id}> has timed out."


def build_okta_error_message(user_id):
    return f":warning: Something went wrong with the Okta request to <@{user_id}>."