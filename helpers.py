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

import json
import os

def get_json(filepath):
    '''
    Read a json file and return json variable
    '''
    with open(filepath, 'r') as f:
        jsondata = json.loads(f.read())
        f.close()
    return jsondata


def write_json(filepath, json_content):
    '''
    Write content to json file
    '''
    with open(filepath, "w") as jsonFile:
        json.dump(json_content, jsonFile)


def dir_last_updated(folder):
    '''
    Method to make sure newest version of a file is used to prevent caching issues
    '''
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))
    

def clean_db(db):
    '''
    Remove all element in the DB. 
    '''
    db.mg_collection.delete_many( { } )
   