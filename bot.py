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


'''Dont forget to set the environmental variables

WEBEX_TEAMS_ACCESS_TOKEN
BOT_EMAIL

If using ngrok, you need to update the webhook on this link with the targetUrl = ngrok Forwarding address (e.g. http://something.ngrok.io)

https://developer.webex.com/docs/api/v1/webhooks/update-a-webhook

'''


import json
from flask import Flask, abort, request 
from webexteamssdk import WebexTeamsAPI
import os
import requests
from dcUniConfig import config

BOT_ID = config.BOT_ID
ACCESS_TOKEN = config.ACCESS_TOKEN


with open('help_guide.json', 'r') as f:
    HELP_GUIDE = json.load(f)

app = Flask(__name__)
api = WebexTeamsAPI(ACCESS_TOKEN)

app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True



def gitCommitMessage(commit):

    # send a message to the webex teams room with the details of the new commit

    compare = commit["compare"]
    committerMessage = commit["head_commit"]["message"]
    author = commit["head_commit"]["author"]["name"]
    committer = commit["head_commit"]["committer"]["name"]
    added = commit["head_commit"]["added"]
    removed = commit["head_commit"]["removed"]
    modified = commit["head_commit"]["modified"]
    repository = commit["repository"]["name"]
        
    message = "There was a new commit to the {} repository. \n\n Commit Message: {} \n\n Author: {} \n\nCommiter: {} \n\n Files Added: {}\n\n Files Removed: {}\n\n Files Modified: {} \n\n Click link to compare: {}".format(repository,committerMessage,author,committer,added,removed,modified,compare)
    
    all_rooms = api.rooms.list()
    for room in all_rooms:
        api.messages.create(room.id, markdown=message)

    
    

def parseCommand(message,roomId):
    
    # i've split this out into multiple files to try and simplify the logic required here.  the following is an example of the lookup when the "?" command 
    # is posted into the webex teams room

    # ? -> HELP_OVERVIEW -> This is a bot used for the DC University Day in Eschborn

    # help_guide.json contains the translation from the command  posted in the webex teams room to the required help lookup key
    # help_guide.json was previously read and stored in the HELP_GUIDE variable
    # "config" contains the configuration settings, including help messages which are parsed from help-guide.cfg
    # help-guide.cfg contains the help messages to return, first the lookup key followed by the message to return
    # getattr(config,HELP_GUIDE[message]) will match the webex teams room command to the required help guide lookup key 

    message = message.text

    if message in HELP_GUIDE:
        api.messages.create(roomId, markdown=getattr(config,HELP_GUIDE[message]))
    else:
        api.messages.create(roomId, text=config.HELP_OVERVIEW)
    
@app.route('/',methods=['POST'])
def index():
    if not request.json:
        abort(400)
    
    # this will run if there is a new commit in the github repo
    if "commits" in request.json:
        gitCommitMessage(request.json)
        

    # this will run if there is a new message in the bot webex teams room
    if "data" in request.json:
        if request.json["data"]["personEmail"] != BOT_ID:
            roomId = request.json["data"]["roomId"]
            message = api.messages.get(request.json["data"]["id"])
            
            parseCommand(message,roomId)

    # don't need to return anything as we're sending to webex directly therefore just send a 204
    
    # The HTTP 204 No Content success status response code indicates that the request has succeeded,
    # but that the client doesn't need to go away from its current page

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/204

    return ('', 204)

if __name__ == '__main__':
    app.run(port=5000,host= '0.0.0.0', debug=True)
