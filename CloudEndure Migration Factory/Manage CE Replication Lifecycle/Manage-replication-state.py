#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
 
from __future__ import print_function
import sys
import argparse
import requests
import json
import boto3
import getpass
import time

HOST = 'https://console.cloudendure.com'
headers = {'Content-Type': 'application/json'}
session = {}
endpoint = '/api/latest/{}'

serverendpoint = '/prod/user/servers'
appendpoint = '/prod/user/apps'

with open('FactoryEndpoints.json') as json_file:
    endpoints = json.load(json_file)
LoginHOST = endpoints['LoginApiUrl']
UserHOST = endpoints['UserApiUrl']

def Factorylogin(username, password, LoginHOST):
    login_data = {'username': username, 'password': password}
    r = requests.post(LoginHOST + '/prod/login',
                      data=json.dumps(login_data))
    if r.status_code == 200:
        print("Migration Factory : You have successfully logged in")
        print("")
        token = str(json.loads(r.text))
        return token
    else:
        print("ERROR: Incorrect username or password....")
        print("")
        sys.exit(1)

def CElogin(userapitoken, endpoint):
    login_data = {'userApiToken': userapitoken}
    r = requests.post(HOST + endpoint.format('login'),
                  data=json.dumps(login_data), headers=headers)
    if r.status_code == 200:
        print("CloudEndure : You have successfully logged in")
        print("")
    if r.status_code != 200 and r.status_code != 307:
        if r.status_code == 401 or r.status_code == 403:
            print('ERROR: The CloudEndure login credentials provided cannot be authenticated....')
        elif r.status_code == 402:
            print('ERROR: There is no active license configured for this CloudEndure account....')
        elif r.status_code == 429:
            print('ERROR: CloudEndure Authentication failure limit has been reached. The service will become available for additional requests after a timeout....')
    
    # check if need to use a different API entry point
    if r.history:
        endpoint = '/' + '/'.join(r.url.split('/')[3:-1]) + '/{}'
        r = requests.post(HOST + endpoint.format('login'),
                      data=json.dumps(login_data), headers=headers)
                      
    session['session'] = r.cookies['session']
    try:
       headers['X-XSRF-TOKEN'] = r.cookies['XSRF-TOKEN']
    except:
       pass

def GetCEProject(projectname):
    r = requests.get(HOST + endpoint.format('projects'), headers=headers, cookies=session)
    if r.status_code != 200:
        print("ERROR: Failed to fetch the project....")
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


def verify_replication(projects, token):
    # Get Machine List from CloudEndure
    time.sleep(10)
    auth = {"Authorization": token}
    for project in projects:
            print("")
            project_id = project['ProjectId']
            serverlist = project['Servers']
            m = requests.get(HOST + endpoint.format('projects/{}/machines').format(
                project_id), headers=headers, cookies=session)
            if "sourceProperties" not in m.text:
                print("ERROR: Failed to fetch the machines for project: " +
                      project['ProjectName'])
                sys.exit(7)
            for server in serverlist:
                machine_exist = False
                for machine in json.loads(m.text)["items"]:
                    if server["server_name"].lower() == machine['sourceProperties']['name'].lower():
                        machine_exist = True
                        replication_state = machine['replicationStatus']
                        print("CE replication status for  " + str(server["server_name"]) + "..." + replication_state )
                if machine_exist == False:
                    print(
                        "ERROR: Machine: " + server["server_name"] + " does not exist in CloudEndure....")
                    sys.exit(8)

def replication_action(projects, token, replication_action):
        # Get Machine List from CloudEndure
        auth = {"Authorization": token}
        for project in projects:
            print("")
            project_id = project['ProjectId']
            serverlist = project['Servers']
            m = requests.get(HOST + endpoint.format('projects/{}/machines').format(project_id), headers=headers, cookies=session)
            if "sourceProperties" not in m.text:
                print("ERROR: Failed to fetch the machines for project: " + project['ProjectName'])
                sys.exit(7)
            for server in serverlist:
                machine_exist = False
                for machine in json.loads(m.text)["items"]:
                    if server["server_name"].lower() == machine['sourceProperties']['name'].lower():
                        machine_exist = True
                        machine_data = {'machineIDs': [machine['id']]}
                        if replication_action.lower() == "start":
                            r = requests.post(HOST + endpoint.format('projects/{}/startReplication').format(
                                project_id), headers=headers, cookies=session, data= json.dumps(machine_data))
                            if "200" in str(r):
                                print("Replication started for machine..  " + server["server_name"])
                            else:
                                print("Replication could not be started for machine..  " + server["server_name"])
                        if replication_action.lower() == "pause":
                            r = requests.post(HOST + endpoint.format('projects/{}/pauseReplication').format(project_id), headers=headers, cookies=session, data=json.dumps(machine_data))
                            if "200" in str(r):
                                print("Replication paused for machine..  " + server["server_name"])
                            else:
                                print("Replication could not be paused for machine..  " + server["server_name"])
                        if replication_action.lower() == "stop":
                            r = requests.post(HOST + endpoint.format('projects/{}/stopReplication').format(project_id), headers=headers, cookies=session, data=json.dumps(machine_data))
                            if "200" in str(r):
                                print("Replication stopped for machine..  " + server["server_name"])
                            else:
                                print("Replication could not be stopped for machine..  " + server["server_name"])
                        if replication_action.lower() == "check":
                            pass


                if machine_exist == False:
                    print("ERROR: Machine: " + server["server_name"] + " does not exist in CloudEndure....")
                    sys.exit(8)




def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--Waveid', required=True)
    parser.add_argument('--ReplicationAction', required=True)
    args = parser.parse_args(arguments)

    print("******************************")
    print("* Login to Migration factory *")
    print("******************************")
    token = Factorylogin(input("Factory Username: "), getpass.getpass('Factory Password: '), LoginHOST)

    print("")
    print("************************")
    print("* Login to CloudEndure *")
    print("************************")
    r = CElogin(getpass.getpass('CE API Token: '), endpoint)
    if r is not None and "ERROR" in r:
        print(r)

    print("***********************")
    print("* Getting Server List *")
    print("***********************")
    Projects = ProjectList(args.Waveid, token, UserHOST, serverendpoint, appendpoint)
    print("")
    for project in Projects:
        print("***** Servers for CE Project: " + project['ProjectName'] + " *****")
        for server in project['Servers']:
            print(server['server_name'])
        print("")
    print("")
    print("*****************************")
    print("*  " + str(args.ReplicationAction.upper())+ "  Replication *")
    print("*****************************")
    replication_action(Projects, token, args.ReplicationAction)
    print("")
    print("*****************************")
    print("* Verify replication status *")
    print("*****************************")
    verify_replication(Projects, token)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
