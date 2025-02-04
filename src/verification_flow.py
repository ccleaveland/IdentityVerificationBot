import logging
import time

from threading import Thread

import messaging
import okta

#
# Methods and variables related to threaded verification flow
#

class VerificationThread(Thread):
    def __init__(self, app, channel_id, slack_id, email):
        Thread.__init__(self)
        self.app = app
        self.channel_id = channel_id
        self.slack_id = slack_id
        self.email = email

    def run(self):
        try:
            user_id = okta.get_okta_user_id(self.email)
            factor_id = okta.get_okta_factor_id(user_id)
            response = okta.send_okta_push_factor(user_id, factor_id)
            transaction_id = okta.extract_transaction_id(response)
            factor_result = wait_for_result(user_id, factor_id, transaction_id, response["factorResult"])
        except Exception as e:
            logging.error(f"Error during okta verification flow: {e}") 
            factor_result = "EXCEPTION"
        
        if factor_result == "SUCCESS":
            result_message = messaging.build_okta_verified_message(self.slack_id)
        elif factor_result == "REJECTED":
            result_message = messaging.build_okta_rejected_message(self.slack_id)
        elif factor_result == "TIMEOUT":
            result_message = messaging.build_okta_timeout_message(self.slack_id)
        else: #Options: https://developer.okta.com/docs/reference/api/factors/#factor-verify-result-object
            result_message = messaging.build_okta_error_message(self.slack_id)
        
        messaging.post_message(self.app, self.channel_id, result_message)


def wait_for_result(user_id, factor_id, transaction_id, factor_result):
    while (factor_result == "WAITING"):
            time.sleep(10)
            response = okta.poll_okta_result(user_id, factor_id, transaction_id)
            factor_result = response["factorResult"]
    return factor_result