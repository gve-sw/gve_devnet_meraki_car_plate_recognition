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

# When the user make an order from app > post JSON payload to JSON server DB

import requests
import json
import os
from dotenv import load_dotenv

# search .env and load environment variable
load_dotenv()
DB_HOST = os.getenv('DB_HOST')

url = DB_HOST+"/order"

payload = json.dumps({
    "customer": "Bob",
    "menu": "Fries",
    "qty": 3,
    "car_plate": "MY70 BMW",
    "time": "2021-04-23T08:09:46Z"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
