""" Copyright (c) 2020 Cisco and/or its affiliates.
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

from requests.models import HTTPError

load_dotenv()

BASE_URL = "https://api.meraki.com/api/v1"
API_KEY = os.environ['MERAKI_API_TOKEN']

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Cisco-Meraki-API-KEY": API_KEY
}


def get_organizations():
    '''
    Get all organization available for the api key
    '''

    print('Request list of organizations')

    try:
        url = BASE_URL+f'/organizations'

        response = requests.get(url, headers=HEADERS)
        
        if response.status_code >= 400:
            raise Exception(f'HTTP error code: {response.status_code} - {response.reason}')

        return response.json()

    except Exception as err:
        print('Error in get_organizations()')
        raise Exception(err)


def get_networks(organizationId):
    '''
    Get all network of a organization
    '''

    print('Request list of networks for ' + organizationId)

    try:
        url = BASE_URL+f'/organizations/{organizationId}/networks'

        response = requests.get(url, headers=HEADERS)
        
        if response.status_code >= 400:
            raise Exception(f'HTTP error code: {response.status_code} - {response.reason}')

        return response.json()

    except Exception as err:
        print('Error in get_networks()')
        raise Exception(err)


def get_network(networkId):
    '''
    Get detailed information about a networks based on the network ID
    '''

    print('Request network information for ' + networkId)

    try:
        url = BASE_URL+f'/networks/{networkId}'

        response = requests.get(url, headers=HEADERS)
        
        if response.status_code >= 400:
            raise Exception(f'HTTP error code: {response.status_code} - {response.reason}')

        return response.json()

    except Exception as err:
        print('Error in get_network()')
        raise Exception(err)
     

def get_device(serial):
    '''
    Get detailed information about a device based on the serial number
    '''

    print('Request device information for ' + serial)

    try:
        url = BASE_URL+f'/devices/{serial}'

        response = requests.get(url, headers=HEADERS)
        
        if response.status_code >= 400:
            raise Exception(f'HTTP error code: {response.status_code} - {response.reason}')

        return response.json()

    except Exception as err:
        print('Error in get_device()')
        raise Exception(err)


def get_cellular_gateway_statuses(organizationId):
    '''
    Return cellular gateway information for a organization - e.g. rsrp and rsrq value
    '''

    print('Request orga-wide cellular uplink statuses for ' + organizationId)

    try:
        url = BASE_URL+f'/organizations/{organizationId}/cellularGateway/uplink/statuses'

        response = requests.get(url, headers=HEADERS)
        
        if response.status_code >= 400:
            raise Exception(f'HTTP error code: {response.status_code} - {response.reason}')

        return response.json()

    except Exception as err:
        print('Error in get_cellular_gateway_statuses()')
        raise Exception(err)


def get_orga_uplink_statuses(organizationId):
    '''
    Return the uplink status of every Meraki MX, MG and Z series devices in the organization
    '''

    print('Request orga-wide uplink statuses for ' + organizationId)

    try:
        url = BASE_URL+f'/organizations/{organizationId}/uplinks/statuses'

        response = requests.get(url, headers=HEADERS)
        
        if response.status_code >= 400:
            raise Exception(f'HTTP error code: {response.status_code} - {response.reason}')

        return response.json()

    except Exception as err:
        print('Error in get_orga_uplink_statuses()')
        raise Exception(err)



