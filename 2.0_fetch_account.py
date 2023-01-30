import helpers
import contextio as c

CONSUMER_KEY = "YOUR_CONTEXTIO_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONTEXTIO_CONSUMER_KEY"
EXISTING_ACCOUNT_ID = "AN_EXISTING_2.0_API_ACCOUNT_ID" # see the ContextIO dev console

api = c.ContextIO(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, debug=True)

account = c.Account(api, {"id": EXISTING_ACCOUNT_ID})

helpers.headerprint("FETCHING ACCOUNT INFO (Lite API)")

account.get()

helpers.cprint("id", account.id)
helpers.cprint("username", account.username)
helpers.cprint("created", account.created)
helpers.cprint("suspended", account.suspended)
helpers.cprint("email_addresses", account.email_addresses)
helpers.cprint("first_name", account.first_name)
helpers.cprint("last_name", account.last_name)
helpers.cprint("password_expired", account.password_expired)
helpers.cprint("sources", account.sources)
helpers.cprint("resource_url", account.resource_url)
print "\n"

