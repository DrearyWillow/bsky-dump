
import requests

# Bluesky API base URL for creating a session
BASE_URL = 'https://bsky.social/xrpc/com.atproto.server.createSession'

def get_access_token(username, password):
    # Prepare the login payload
    payload = {
        'identifier': username,
        'password': password
    }

    # Send the POST request to create a session
    response = requests.post(BASE_URL, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response to get the access token (accessJwt)
        data = response.json()
        access_token = data.get('accessJwt')
        return access_token
    else:
        raise Exception(f"Failed to get access token. Status code: {response.status_code}, Message: {response.text}")

# Example usage
username = ''
password = ''

try:
    access_token = get_access_token(username, password)
    print(f"Access Token: {access_token}")
except Exception as e:
    print(e)

