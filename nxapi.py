'''Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.'''


import requests
import json
from dcUniConfig import config

from tabulate import tabulate

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

N9KV_URL = config.N9KV_URL
N9KV_USER = config.N9KV_USER
N9KV_PASSWORD = config.N9KV_PASSWORD

hosts = N9KV_URL.split(",")

myheaders={'content-type':'application/json'}
payload={
  "ins_api": {
    "version": "1.0",
    "type": "cli_show",
    "chunk": "0",
    "sid": "sid",
    "input": "show version ;show interface brief ;show ip interface brief ;show feature ;show license usage",
    "output_format": "json"
  }
}
for host in hosts:
    print("\n")
    print("****************** HOST: {} ******************".format(host))

    try:
        response = requests.post("https://{}/ins".format(host),data=json.dumps(payload), headers=myheaders, verify=False,auth=(N9KV_USER,N9KV_PASSWORD))
    
        if response.status_code == 200 or response.status_code == 201:
            response =  json.loads(response.text)
            response = response["ins_api"]["outputs"]["output"]

            for command in response:
                if command["input"] == "show version":
                    print("\n")
                    response = command["body"]
                    print(tabulate([[response["chassis_id"], response["kickstart_ver_str"],response["bootflash_size"]]], headers=["Chassis ID","NXOS Version", "Bootflash"]))
                
                elif command["input"] == "show interface brief":
                    response = command["body"]["TABLE_interface"]
                    interfaces = []
                    for interface in response["ROW_interface"]:
                        if "state_rsn_desc" in interface:
                            interfaces.append([interface["interface"], interface["state"],interface["state_rsn_desc"]])
                        else:
                            interfaces.append([interface["interface"], interface["state"],"Unknown"])
                    print("\n")
                    print(tabulate(interfaces,headers=["Interface","State", "Reason"]))
                
                elif command["input"] == "show ip interface brief":
                    if "TABLE_intf" in command["body"]:
                        response = command["body"]["TABLE_intf"]
                        interfaces = []
                        if type(response["ROW_intf"]) is list:
                            for interface in response["ROW_intf"]:
                                interfaces.append([interface["intf-name"], interface["prefix"], interface["proto-state"],interface["link-state"],interface["admin-state"]])
                        else:
                            interface = response["ROW_intf"]
                            interfaces.append([interface["intf-name"], interface["prefix"], interface["proto-state"],interface["link-state"],interface["admin-state"]])
                        print("\n")
                        print(tabulate(interfaces,headers=["Interface","Prefix", "Protocol State", "Link State", "Admin State"]))

                elif command["input"] == "show feature":
                    response = command["body"]["TABLE_cfcFeatureCtrlTable"]
                    features = []

                    for feature in response["ROW_cfcFeatureCtrlTable"]:
                        if not any(feature["cfcFeatureCtrlName2"] in f for f in features):
                            features.append([feature["cfcFeatureCtrlName2"], feature["cfcFeatureCtrlOpStatus2"],feature["cfcFeatureCtrlOpStatusReason2"]])
                        
                    print("\n")
                    print(tabulate(features,headers=["Feature","Status", "Comment"]))
                
                elif command["input"] == "show license usage":
                    response = command["body"]["TABLE_show_lic_usage"]
                    licenses = []

                    for license in response["ROW_show_lic_usage"]:
                        licenses.append([license["feature_name"], license["lic_installed"],license["count"],license["status"],license["expiry_date"],license["comments"]])
                        
                    print("\n")
                    print(tabulate(licenses,headers=["Feature","License Installed?", "Count","Status","Expiry Date","Comment"]))

    except requests.exceptions.ConnectionError as ece:
        print("\n Connection Error: ", ece)
        continue
    except requests.exceptions.Timeout as et:
        print("\n Timeout Error: ", et)
        continue
    except requests.exceptions.RequestException as e:
        print("\n Request Exception: ", e)
        continue
       