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

from flask import Flask, render_template, request, redirect, url_for
from geojson import Point, Feature, FeatureCollection, dump
import time
import os
import json
from flask_pymongo import PyMongo
from datetime import datetime, timedelta, timezone
import certifi

from apscheduler.schedulers.background import BackgroundScheduler

import meraki_api
import webex 
import helpers

app = Flask(__name__)

app.config['MONGO_URI'] = os.environ['MONGODB_CON'] 
mongo = PyMongo(app,tlsCAFile=certifi.where())
db = mongo.db

dropdown_content = []

SCHEDULER_INTERVAL_SEC = int(os.environ['SCHEDULER_INTERVAL_SEC'])

def calculate_aggregated_alert_level(uplinks):
    '''
    Calculate an overall alert level based on the rsrq and rsrp value of all interface of an device.
    alert_levels: 
    0 - excellent
    1 - good
    2 - fair to poor
    3 - no signal
    -1 - no data
    More details on: https://wiki.teltonika-networks.com/view/RSRP_and_RSRQ
    '''
    rsrp_alert_level = None
    rsrq_alert_level = None
    aggregated_alert_level = None
    smallest_rsrp = None
    smallest_rsrq = None 

    #Retrieve smallest RSRP and RSRQ value of all interfaces
    for uplink in uplinks:
        if 'rsrp' in uplink['signalStat']:
            rsrp = int(uplink['signalStat']['rsrp'])
            if smallest_rsrp == None or rsrp < smallest_rsrp:
                smallest_rsrp = rsrp

        if 'rsrq' in uplink['signalStat']:
            rsrq = int(uplink['signalStat']['rsrq'])
            if smallest_rsrq == None or rsrq < smallest_rsrq:
                smallest_rsrq = rsrq

    #Identifiy RSRP alert level for smallest RSRP
    if smallest_rsrp == None:
        rsrp_alert_level = -1
    elif smallest_rsrp >= -80:
        rsrp_alert_level = 0
    elif smallest_rsrp < -80 and smallest_rsrp >= -90:
        rsrp_alert_level = 1
    elif smallest_rsrp < -90 and smallest_rsrp > -100:
        rsrp_alert_level = 2
    elif smallest_rsrp <= -100:
        rsrp_alert_level = 3

    #Identifiy RSRP alert level for smallest RSRQ
    if smallest_rsrq == None:
        rsrq_alert_level = -1
    elif smallest_rsrq >= -10:
        rsrq_alert_level = 0
    elif smallest_rsrq < -10 and smallest_rsrq >= -15:
        rsrq_alert_level = 1
    elif smallest_rsrq < -15 and smallest_rsrq > -20:
        rsrq_alert_level = 2
    elif smallest_rsrq <= -20:
        rsrq_alert_level = 3

    #Identify if RSRP or RSRQ has higher and thereby worse alert level
    if rsrq_alert_level > rsrp_alert_level:
        aggregated_alert_level = rsrq_alert_level
    else:
        aggregated_alert_level = rsrp_alert_level
            
    return aggregated_alert_level
    

def remove_non_cellular_interfaces(uplinks):
    '''
    Return list only with the cellular interfaces for a device
    '''

    filtered_uplinks = []

    for uplink in uplinks:
        interface = uplink['interface']

        if 'cellular' in interface:
            filtered_uplinks.append(uplink)

    return filtered_uplinks


def create_map_marker_json(selected_orga_id):
    '''
    Create json file representing the map markes based on information retrieved from the Meraki Dashboard
    '''
    
    features = []

    statuses = meraki_api.get_orga_uplink_statuses(selected_orga_id)

    for device in statuses:

        device_model = device['model']

        if 'MG' in device_model or 'MX' in device_model:
    
            network_id = device['networkId']
            device_serial = device['serial']
            last_reported_at = device['lastReportedAt']
            uplinks = device['uplinks']

            filtered_uplinks = remove_non_cellular_interfaces(uplinks)
            #Do not add device on map/list if it has no cellular interface
            if filtered_uplinks == []:
                continue
            else:
                alert_level = calculate_aggregated_alert_level(filtered_uplinks)
            
                network_details = meraki_api.get_network(network_id)
                network_name= network_details['name']

                device_details = meraki_api.get_device(device_serial)
                if 'name' in device_details:
                    device_name = device_details['name']
                else:
                    device_name = device_details['model']
                device_model = device_details['model']
                device_firmware = device_details['firmware']
                device_latitude = device_details['lat']
                device_longitude = device_details['lng']
                device_address = device_details['address'] #even if address data is not available the Meraki Dashboard knows the longitude and latitude of a device
                device_dashboard_link = device_details['url']

                point = Point((device_longitude,device_latitude))

                properties = {
                            "name": device_name,
                            "location": device_address,
                            "alertLevel": alert_level,
                            "lastReportedAt": last_reported_at,
                            "networkName": network_name,
                            "network_Id": network_id,
                            "serial": device_serial,
                            "model": device_model,
                            "dashboard_url": device_dashboard_link,
                            "uplinks": filtered_uplinks
                        }

                features.append(Feature(geometry=point, properties=properties))

    feature_collection = FeatureCollection(features)

    helpers.write_json('static/data/devices.geojson', feature_collection)

    return feature_collection



def automatic_data_transfer(): 
    '''
    Store current cellular gateway information in a DB and sends out a Webex notification about the status
    '''

    global dropdown_content

    print("------------Automatic data transfer-----------------")

    for orga in dropdown_content:
        
        orga_id = orga['id']
        orga_name = orga['name']

        statuses = meraki_api.get_orga_uplink_statuses(orga_id)
        filtered_statuses = []

        now = datetime.now()

        #Prepare and store informating in DB
        for (index, device_status) in enumerate(statuses): 

            device_model = device_status['model']

            if 'MG' in device_model or 'MX' in device_model:
                
                uplinks = device_status['uplinks']

                filtered_uplinks = remove_non_cellular_interfaces(uplinks)

                #Do not add device on map/list if it has no cellular interface
                if filtered_uplinks != []:

                    #Only save cellular uplinks in the DB
                    print("Add new device data to DB.")
                    
                    device_serial = device_status['serial']

                    device_stats = {
                        "orga_id": orga_id,
                        "serial": device_serial,
                        "timestamp": now,
                        "status": device_status
                        }

                    db.mg_collection.insert_one(device_stats)
                    filtered_statuses.append(device_status)


        #Perpare and send notification 
        if filtered_statuses != []:
            webex.send_notifications(filtered_statuses, orga_name)


# For a production environment I would suggest to move the functionality around 
# the periodic data transfer to a separate script/Flask app to preventing unwanted 
# delay for user input operations when the automatic transfer is happening.
def scheduler():
    '''
    Executes automatic data base information transfer and webex notification on a defined interval
    '''
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=automatic_data_transfer, trigger="interval", seconds=SCHEDULER_INTERVAL_SEC , max_instances=1)
    scheduler.start()
    print("Scheduler Started with interval of seconds: " + str(SCHEDULER_INTERVAL_SEC))


######ROUTES
'''
Main Page - Map and List View 
'''
app.route('/?orga_id=<orga_id>')
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    
    global dropdown_content

    orga_id = request.args.get('orga_id')
    
    try:
        if request.method == 'POST':
            orga_id = request.form.get("organizations_select")
            return redirect("/?orga_id="+str(orga_id))

        if orga_id != '':
            devices = create_map_marker_json(orga_id)

            device_features = devices['features']

            #Sort the devices based on the alert level to show the MG/MX without signal on top of list
            device_features.sort(key=lambda x: x['properties']["alertLevel"])
            device_features.reverse()
        else:
            device_features = []
                
        return render_template('dashboard.html', devices = device_features, hiddenLinks=True, dropdown_content=dropdown_content, selected_orga_id=orga_id, last_updated=helpers.dir_last_updated('static/data'))
    
    except Exception as e: 
        print(f'EXCEPTION!! {e}')
        return render_template('dashboard.html', error=True, hiddenLinks=True, dropdown_content=dropdown_content, selected_orga_id=orga_id)


'''
Device detail page
'''
app.route('/details?serial=<serial>&orga_id=<orga_id>')
@app.route('/details', methods=["POST", "GET"])
def details():

    current_devices_data = helpers.get_json('static/data/devices.geojson')
    
    if current_devices_data == []:

        return redirect(url_for('dashboard'))

    else:
        #Retrieve information
        serial = request.args.get('serial')
        orga_id = request.args.get('orga_id')
        
        current_devices_data = helpers.get_json('static/data/devices.geojson')['features']

        now = datetime.now()
        labels = []
        rsrp_data = []
        rsrq_data = []
        
        #Create label list for graph - hours of the last 24h 
        for i in range(23, -1, -1):
            past_hour_date_time = datetime.now() - timedelta(hours = i)
            label = past_hour_date_time.strftime('%H:00') 

            labels.append(label)
            rsrp_data.append(None)
            rsrq_data.append(None)

        #Retrieve DB entries for a specific device of the last 24 h
        date_24_hours_ago = now - timedelta(hours = 24)    
        db_device_data = list(db.mg_collection.find({"serial" : serial, "timestamp" : {'$gte' : date_24_hours_ago }}))
        
        #Create data lists for graph
        for label in labels:
            for element in db_device_data:
                if label == element['timestamp'].strftime('%H:00'):
                    position = int(labels.index(label))
                    signalstats = element['status']['uplinks'][0]['signalStat']
                    if 'rsrp' in signalstats: 
                        rsrp_data[position] = signalstats['rsrp']
                    if 'rsrq' in signalstats: 
                        rsrq_data[position] = signalstats['rsrq']
        
    return render_template('details.html', devices=current_devices_data, serial=serial, orga_id=orga_id, labels=labels, rsrp_data=rsrp_data, rsrq_data=rsrq_data, hiddenLinks=False, last_updated=helpers.dir_last_updated('static/data'))



if __name__ == "__main__":
    
    #Init DB
    mongo.init_app(app)

    #Retrieve organization for dropdown    
    dropdown_content = meraki_api.get_organizations()

    #Reset map data
    helpers.write_json('static/data/devices.geojson', [])

    #Clean db
    #helpers.clean_db(db)
    
    #Start scheduler
    scheduler()

    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)


