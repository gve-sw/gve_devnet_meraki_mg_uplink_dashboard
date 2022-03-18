""" Copyright (c) 2022 Cisco and/or its affiliates.
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

from webexteamssdk import WebexTeamsAPI

from dotenv import load_dotenv
import os
import json
from datetime import datetime

import meraki_api
import helpers

load_dotenv()

api = WebexTeamsAPI(access_token=os.environ['WEBEX_TEAMS_ACCESS_TOKEN'])

room_id= os.environ['ROOM_ID']
RSRP_MIN_ALERTING_THRESHOLD = int(os.environ['RSRP_MIN_ALERTING_THRESHOLD'])
RSRQ_MIN_ALERTING_THRESHOLD = int(os.environ['RSRQ_MIN_ALERTING_THRESHOLD'])
NOTIFY_CARD_JSON = "notifyCard.json"


def extract_formatted_data(statuses):
    '''
    Extract signal and missing address data
    '''

    no_signal_data = ''
    no_address_data = ''

    for device in statuses:
        device_serial = device['serial']

        device_details = meraki_api.get_device(device_serial)

        if 'name' in device_details:
            device_name = device_details['name']
        else:
            device_name = device_details['model']
        device_dashboard_url = device_details['url']

        #Create list of devices without signal
        for uplink in device['uplinks']: 
            
            device_interface = uplink['interface']
            device_ip = uplink['ip']
            
            if uplink['signalStat'] == []:
                no_signal_data = no_signal_data + ' * '+ device_name +'('+ device_serial +'): [Dashboard URL]('+ device_dashboard_url+')\n'
            elif 'rsrp' in uplink['signalStat'] and int(uplink['signalStat']['rsrp']) <= RSRP_MIN_ALERTING_THRESHOLD:
                no_signal_data = no_signal_data + ' * '+ device_name +'('+ device_serial +'): [Dashboard URL]('+ device_dashboard_url+')\n'
            elif 'rsrq' in uplink['signalStat'] and int(uplink['signalStat']['rsrq']) <= RSRQ_MIN_ALERTING_THRESHOLD:
                no_signal_data = no_signal_data + ' * '+ device_name +'('+ device_serial +'): [Dashboard URL]('+ device_dashboard_url+')\n'
        
        #Create list of devices without address
        device_address = device_details['address']
        if(device_address == ""):
            no_address_data = no_address_data + ' * '+ device_name +'('+ device_serial +'): [Dashboard URL]('+ device_dashboard_url+')\n '

    return no_signal_data, no_address_data


def prepare_alert_card(statuses, orga_name):
    '''
    Fill status data in card template
    '''

    no_signal_data, no_address_data = extract_formatted_data(statuses)

    adapted_card = helpers.get_json(NOTIFY_CARD_JSON)
    adapted_card_body = adapted_card['body']

    now = datetime.now()

    for element in adapted_card_body:
        if 'id' in element:
            if element['id'] == 'no_signal':
                element['inlines'][0]['text'] = no_signal_data
            if element['id'] == 'no_address':
                element['inlines'][0]['text'] = no_address_data
            if element['id'] == 'date':
                element['columns'][0]['items'][0]['columns'][1]['items'][0]['text'] = now.strftime("%d/%m/%Y, %H:%M")
            if element['id'] == 'headline_no_signal':
                element['text'] = 'Device with RSRP < ' + str(RSRP_MIN_ALERTING_THRESHOLD) + ' and RSRQ < ' + str(RSRQ_MIN_ALERTING_THRESHOLD) + ' or no data'
            if element['id'] == 'headline':
                element['columns'][0]['items'][0]['text'] = "Meraki MG Status Alerts for " + orga_name
    return adapted_card


def send_notifications(statuses, orga_name):
    '''
    Notfiy all specified employees that new help request is available
    '''
    
    print("Send notification bot message for " + orga_name)    
    
    card_content = prepare_alert_card(statuses, orga_name)

    api.messages.create(room_id, text="If you see this your client cannot render cards.", attachments=[{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": card_content
        }])


