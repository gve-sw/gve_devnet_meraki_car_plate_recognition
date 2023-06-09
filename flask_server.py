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

# Flask server as webhook receiver > then triggers a series of scripts

from flask import Flask, request, Response, abort
import time
import os
from dotenv import load_dotenv
from functions import *
from webexteamssdk import Webhook

# search .env file and load environment variable
load_dotenv()
MV_SHARED_KEY = os.getenv('MV_SHARED_KEY')

# webex destination
WEBEX_ROOM_ID = os.getenv('WEBEX_ROOM_ID')

# snapshot timing in seconds
waitTime = 12
intervalTime = 4

# boolean for filtering webhooks
runScript = True

# Flask server setup
mainApp = Flask(__name__)
mainApp.debug = True


@mainApp.route('/webhook', methods=['POST'])
def webhook():
    global runScript
    if request.method == 'POST' and request.headers['Content-Type'] == 'application/json' and runScript == True:
        payload = request.json
        if payload['sharedSecret'] == MV_SHARED_KEY and payload['alertTypeId'] == 'motion_alert':

            # change the runScript to prevent the server from being flooded by alerts
            if runScript == True:
                runScript = False

            # define variable
            deviceSerial = payload['deviceSerial']
            deviceName = payload['deviceName']
            occurredAt = payload['occurredAt']

            # wait several seconds for the car to be parked, then take a snapshot
            time.sleep(waitTime)
            snapTime = addSeconds(occurredAt, waitTime)

            # then take max 5 snapshots loop: retrieving snapshot, car plate, image labels
            for i in range(3):
                print('---------HERE COMES SNAPSHOT LOOP #%d---------' % i)
                # generate snapshot url
                snapResponse = snapshotAndUri(
                    deviceSerial, occurredAt, snapTime)

                # for testing without meraki camera
                # snapResponse = {'url': ''}
                # snapResponse['url'] = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/image_data/file/110487/s960_960-green-number-plate.jpg'

                # filter the snapshot for vehicle and car plate
                filterResult = visionFiltering(snapResponse['url'])

                # if there are relevant labels detected, run plate detection
                if filterResult == True:
                    # detecting car plate from snapshot url
                    detectedPlate = detectTextURI(snapResponse['url'])

                    # if car plate is detected, check order information
                    if detectedPlate != []:
                        # loop through the text detection result
                        for plate in detectedPlate:
                            # search for a plate match in the order database
                            print('1st order check for breaking the loop:')
                            searchOrder = getOrder(plate)

                        # if there is an order match, break from the loop
                        if searchOrder != []:
                            break
                        # if there is no order match, wait and take the snapshot again
                        else:
                            time.sleep(intervalTime)
                            snapTime = addSeconds(snapTime, intervalTime)
                            continue

                    # if there is no car plate detected, wait and take the snapshot again
                    else:
                        time.sleep(intervalTime)
                        snapTime = addSeconds(snapTime, intervalTime)
                        continue

                # if no relevant labels detected, wait and take snapshot again
                else:
                    time.sleep(intervalTime)
                    snapTime = addSeconds(snapTime, intervalTime)
                    continue

            # if there is relevant labels but car plate is not detected at all, send snapshot url to webex for manual check, using a dedicated space
            if filterResult == True and detectedPlate == []:
                postCard_noPlate(snapResponse, WEBEX_ROOM_ID)

            # if there is relevant labels and a car plate is detected, store car event in database, then send webex notification
            elif filterResult == True and detectedPlate != []:
                for plate in detectedPlate:
                    # store car event to database
                    carToDB(plate, snapTime, deviceName)

                    # retrieve the order again
                    print('2nd order check for webex payload:')
                    searchOrder = getOrder(plate)

                    # post to webex. the message will be different based on whether a plate match an order or not
                    postCard_plateDetected(
                        snapResponse, searchOrder, plate, WEBEX_ROOM_ID)

            # if no relevant labels detected
            elif filterResult == False:
                print(
                    "Invalid alert: Motion not related to ['Vehicle', 'Vehicle registration plate', 'Car']")

            # reset the runScript for the next car event
            runScript = True
            return Response(status=200)

        else:
            print('Invalid Meraki secret key, or not a motion alert')
            abort(400, 'Invalid Meraki secret key, or not a motion alert')

    else:
        print('Unauthorized action, or webhook is filtered by runScript')
        abort(400, 'Unauthorized action, or webhook is filtered by runScript boolean')


@mainApp.route("/card_action", methods=["POST"])
def card_action():
    webhook_obj = Webhook(request.json)
    # print(webhook_obj)
    # print(request.json)

    # change serviced status in db
    respond_to_button_press(webhook_obj)
    return Response(status=200)


# run Flask server
if __name__ == '__main__':
    mainApp.run()
