""" Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import requests
import json
import os
from dotenv import load_dotenv

# search .env and load environment variable
load_dotenv()
NGROK_URL = os.getenv('NGROK_URL')
WEBEX_ROOM_ID = os.getenv('WEBEX_ROOM_ID')
WEBEX_TOKEN = os.getenv('WEBEX_TOKEN')

url = "https://webexapis.com/v1/webhooks"

webhook_name = "your webhook name"
secret = "optional secret key"

payload = json.dumps({
    "name": webhook_name,
    "targetUrl": NGROK_URL + "/card_action",
    "resource": "attachmentActions",
    "event": "created",
    "filter": "roomId=" + WEBEX_ROOM_ID,
    "secret": secret
})
headers = {
    'Authorization': 'Bearer ' + WEBEX_TOKEN,
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
