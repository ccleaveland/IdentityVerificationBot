# Identity Verification Bot
The Identity Verification Bot is a Slack application that provides a way for employees to validate the identities of other employees they are communicating with via their computer or phone to combat impersonation attacks.

**Use Cases**
* Employee needs to verify manager’s identity before completing a high consequence request.
* Leadership needs to verify the identities of others on a call before discussing sensitive company data.
* IT needs to verify a user’s identity before resetting their password or making an account change.
* HR needs to verify an employee’s identity before disclosing personal information.

**Example Scenario**

Bob, Alice, and Eve are on a call and about to discuss potentially sensitive information. Before continuing, Bob initiates the verification process to confirm each party’s identities by opening Slack and typing:

> /verify-user @Alice @Eve

The Slack app creates a direct message channel with the app’s bot, Bob, Alice, and Eve asking to verify that they are currently in communication with one another by responding to their respective Okta requests.

The bot posts results from the Okta verification - confirm, deny, or timed out. Denied requests will be accompanied by an advisory to cease communication.

Bob and Alice both confirm their identities but Eve denies the Okta verification therefore Bob and Alice end the call immediately.  Eve sees the Slack message but they were not on a call with Bob and Alice. They send a message to Bob and Alice letting them know and click the Report Incident button the app provided in the channel to provide details of the incident to security (functionality omitted).