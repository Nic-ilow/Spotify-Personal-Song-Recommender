import base64
import requests
import webbrowser
import random
import string
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from creds import client_id, client_secret

# Local server parameters
server_address = ("localhost", 7777)
redirect_uri = "http://localhost:7777/callback"
state = ''.join(random.choices(string.ascii_lowercase + string.digits, k=21))
# Spotify API endpoints
authorize_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"


def get_auth_url():
    # Generate the authorization URL
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": "user-top-read"  # required scope to retrieve user's top tracks
    }
    query_string = urlencode(params)
    return f"{authorize_url}?{query_string}"


def get_access_token(code):
    # Exchange the authorization code for an access token
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }
    response = requests.post(token_url, headers=headers, data=data)
    return response.json().get("access_token")


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        # Check if the state parameter matches the expected value
        if params['state'][0] != state:
            self.send_response(400)
            self.end_headers()
            return
        # Exchange the authorization code for an access token
        access_token = get_access_token(params["code"][0])
        self.server.access_token = access_token
        # Send the access token back to the client
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


def main():
    server = HTTPServer(server_address, CallbackHandler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Obtain the authorization URL and open it in a browser
    auth_url = get_auth_url()
    webbrowser.open(auth_url)
    access_token = server.access_token

    server.shutdown()
    server.server_close()

    return access_token