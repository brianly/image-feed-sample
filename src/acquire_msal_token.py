import json

import msal

# Define the necessary parameters. First 2 are from the Entra portal.
CLIENT_ID = "338ab182-1608-4097-9b95-7497ccf7319d"
AUTHORITY = "https://login.microsoftonline.com/f14ae0cd-8ed1-4e54-b2e2-67a0429df851"

# Do not use 'https://login.microsoftonline.com/common' for the scope here.
SCOPE = ["https://api.yammer.com/user_impersonation"]


# Create a public client application
app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

# Setup the device code flow
flow = app.initiate_device_flow(scopes=SCOPE)
if "user_code" not in flow:
    raise ValueError(
        f"Failed to create device flow. Error: {json.dumps(flow, indent=4)}"
    )

print(flow["message"])

# Complete the device flow using the code from the console output.
result = app.acquire_token_by_device_flow(flow)

if "access_token" in result:
    print("Access token acquired:")
    print(result["access_token"])
else:
    print("Failed to acquire token:")
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))
