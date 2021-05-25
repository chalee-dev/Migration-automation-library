#########################################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                    #
# SPDX-License-Identifier: MIT-0                                                        #
#                                                                                       #
# Permission is hereby granted, free of charge, to any person obtaining a copy of this  #
# software and associated documentation files (the "Software"), to deal in the Software #
# without restriction, including without limitation the rights to use, copy, modify,    #
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to    #
# permit persons to whom the Software is furnished to do so.                            #
#                                                                                       #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,   #
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A         #
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT    #
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION     #
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE        #
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                #
#########################################################################################

# Version: 23APR2021.01

from __future__ import print_function
import sys
import argparse
import requests
import json
import boto3
import getpass
import datetime
import time
import mfcommon

HOST = mfcommon.ce_address
headers = {'Content-Type': 'application/json'}
session = {}

with open('FactoryEndpoints.json') as json_file:
    endpoints = json.load(json_file)

UserHOST = endpoints['UserApiUrl']

def GetCEProject(projectname):
    r = requests.get(HOST + mfcommon.ce_endpoint.format('projects'), headers=headers, cookies=session)
    if r.status_code != 200:
        print("ERROR: Failed to fetch the projects....")
        sys.exit(2)
    try:
        # Get Project ID
        project_id = ""
        projects = json.loads(r.text)["items"]
        project_exist = False
        for project in projects:
            if project["name"] == projectname:
               project_id = project["id"]
               project_exist = True
        if project_exist == False:
            print("ERROR: Project Name does not exist in CloudEndure....")
            sys.exit(3)
        return project_id
    except:
        print("ERROR: Failed to fetch the project....")
        sys.exit(4)

def ProjectList(waveid, token, UserHOST, serverendpoint, appendpoint):
# Get all Apps and servers from migration factory
    auth = {"Authorization": token}
    servers = json.loads(requests.get(UserHOST + serverendpoint, headers=auth).text)
    #print(servers)
    apps = json.loads(requests.get(UserHOST + appendpoint, headers=auth).text)
    #print(apps)
    newapps = []

    CEProjects = []
    # Check project names in CloudEndure
    for app in apps:
        Project = {}
        if 'wave_id' in app:
            if str(app['wave_id']) == str(waveid):
                newapps.append(app)
                if 'cloudendure_projectname' in app:
                    Project['ProjectName'] = app['cloudendure_projectname']
                    project_id = GetCEProject(Project['ProjectName'])
                    Project['ProjectId'] = project_id
                    if Project not in CEProjects:
                        CEProjects.append(Project)
                else:
                    print("ERROR: App " + app['app_name'] + " is not linked to any CloudEndure project....")
                    sys.exit(5)
    Projects = GetServerList(newapps, servers, CEProjects, waveid)
    return Projects

def GetServerList(apps, servers, CEProjects, waveid):
    servercount = 0
    Projects = CEProjects
    for Project in Projects:
        ServersList = []
        for app in apps:
            if str(app['cloudendure_projectname']) == Project['ProjectName']:
                for server in servers:
                    if app['app_id'] == server['app_id']:
                        if 'server_os' in server:
                                if 'server_fqdn' in server:
                                        ServersList.append(server)
                                else:
                                    print("ERROR: server_fqdn for server: " + server['server_name'] + " doesn't exist")
                                    sys.exit(4)
                        else:
                            print ('server_os attribute does not exist for server: ' + server['server_name'] + ", please update this attribute")
                            sys.exit(2)
        Project['Servers'] = ServersList
        # print(Project)
        servercount = servercount + len(ServersList)
    if servercount == 0:
        print("ERROR: Serverlist for wave: " + waveid + " is empty....")
        sys.exit(3)
    else:
        return Projects


def remove_agents(projects, token, cutoverThreshold, forceRemoval, liveRun):
    # Get Machine List from CloudEndure
    auth = {"Authorization": token}
    for project in projects:
        print("")
        project_id = project['ProjectId']
        serverlist = project['Servers']
        m = requests.get(HOST + mfcommon.ce_endpoint.format('projects/{}/machines').format(project_id), headers=headers, cookies=session)
        if "sourceProperties" not in m.text:
            print("ERROR: Failed to fetch the machines for project: " + project['ProjectName'])
            sys.exit(7)

        replication_not_finished = False
        print("")
        print("***** Replication Status for CE Project: " + project['ProjectName'] + " *****")
        for server in serverlist:
            machine_exist = False
            for machine in json.loads(m.text)["items"]:
                if server["server_name"].lower() == machine['sourceProperties']['name'].lower():
                    machine_exist = True
                    
                    if 'lastCutoverDateTime' in machine['lifeCycle']:
                        cutoverDateTime = datetime.datetime.fromisoformat(machine['lifeCycle']['lastCutoverDateTime'])
                        checkDateTime = cutoverDateTime + datetime.timedelta(days=int(cutoverThreshold))
                        if checkDateTime < datetime.datetime.now(datetime.timezone.utc) or forceRemoval:
                            machine_id =  machine['id']
                            if not liveRun:
                                print(server["server_name"] + ' - TEST RUN: CE agents would be removed.')
                            else:
                                d = requests.delete(HOST + mfcommon.ce_endpoint.format('projects/{}/machines/{}').format(project_id, machine_id), headers=headers, cookies=session)
                                print(server["server_name"] + ' - Removed CE agents.')
                        else:
                            if not liveRun:
                                 print(server["server_name"] + ' - TEST RUN : Cutover was within ' + str(cutoverThreshold) + ' Days please attempt after ' + str(checkDateTime.date()) + '.')
                            else:
                                print(server["server_name"] + ' - Cutover was within ' + str(cutoverThreshold) + ' Days please attempt after ' + str(checkDateTime.date()) + '.')
                    elif forceRemoval:
                        machine_id =  machine['id']
                        if not liveRun:
                            print(server["server_name"] + ' - TEST RUN: Has not been cutover but CE agents would be removed.')
                        else:
                            d = requests.delete(HOST + mfcommon.ce_endpoint.format('projects/{}/machines/{}').format(project_id, machine_id), headers=headers, cookies=session)
                            print(server["server_name"] + ' - Was not cutover but had CE agents removed.')
                    else:
                        if not liveRun:
                            print(server["server_name"] + " - TEST RUN : Server has not been cutover, no action would be taken.")
                        else:
                            print(server["server_name"] + " - Server has not been cutover, no action taken.")
            if machine_exist == False:
                print("ERROR: Machine: " + server["server_name"] + " does not exist in CloudEndure....")

def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--Waveid', required=True)
    parser.add_argument('--CutoverDays', default=21)
    parser.add_argument('--ForceRemoval', default=False)
    parser.add_argument('--LiveRun', default=False)
    args = parser.parse_args(arguments)

    if not args.LiveRun:
        print('THIS IS A TEST RUN, NO CHANGES WILL BE MADE TO THE SYSTEMS!')
    else:   
        has_key = input("""

WARNING!

Are you sure you want to stop replication and remove agents from all servers in wave """ + str(args.Waveid) + """?

Please ensure the owner of the server is aware of the uninstallation of the agent software before continuing.

Press [Y] to continue or [N] to abort.""")

        if  has_key.lower() not in 'y':
            print('TASK ABORTED!')
            sys.exit(0)

    print("******************************")
    print("* Login to Migration factory *")
    print("******************************")
    token = mfcommon.Factorylogin()

    print("")
    print("************************")
    print("* Login to CloudEndure *")
    print("************************")
    r_session, r_token = mfcommon.CElogin(input('CE API Token: '))
    if r_session is None:
        print("ERROR: CloudEndure Login Failed.")
        sys.exit(5)

    session['session'] = r_session

    if r_token is not None:
        headers['X-XSRF-TOKEN'] = r_token

    print("***********************")
    print("* Getting Server List *")
    print("***********************")
    Projects = ProjectList(args.Waveid, token, UserHOST, mfcommon.serverendpoint, mfcommon.appendpoint)
    print("")
    for project in Projects:
        print("***** Servers for CE Project: " + project['ProjectName'] + " *****")
        for server in project['Servers']:
            print(server['server_name'])
        print("")
    print("")
    print("********************************")
    print("*  Remove Agents that are over *")
    print("* " + str(args.CutoverDays) + " days after cutover  *")
    print("********************************")

    remove_agents(Projects, token, args.CutoverDays, args.ForceRemoval, args.LiveRun)
        

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
