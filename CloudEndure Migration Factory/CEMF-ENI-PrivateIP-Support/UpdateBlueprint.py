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

from __future__ import print_function
import sys
import requests
import json
import os
import multiprocessing

def update(launchtype, session, headers, endpoint, HOST, projectId, machinelist, dryrun, serverlist):
    if launchtype == "test" or launchtype == "cutover":
        try:
            b = requests.get(HOST + endpoint.format('projects/{}/blueprints').format(projectId), headers=headers, cookies=session)
            processes = []
            manager = multiprocessing.Manager()
            status_list = manager.list()
            return_dict = manager.dict()
            if len(serverlist) < 8:
                for newlist in chunks(serverlist, len(serverlist)):
                    p = multiprocessing.Process(target=multiprocessing_ce_update, args=(launchtype, session, headers, endpoint, HOST, projectId, machinelist, dryrun, b, newlist, return_dict, status_list))
                    processes.append(p)
                    p.start()
                    print(newlist)
            else:
                for newlist in chunks(serverlist, 8):
                    p = multiprocessing.Process(target=multiprocessing_ce_update, args=(launchtype, session, headers, endpoint, HOST, projectId, machinelist, dryrun, b, newlist, return_dict, status_list))
                    processes.append(p)
                    p.start()
                    print(newlist)
            for process in processes:
                process.join()
            final_status = 0
            for item in status_list:
                final_status += item
            print("")
        except:
            return "ERROR: Updating blueprint task failed...."
        if len(return_dict.values()) > 0:
            print(return_dict.values())
            return str(return_dict.values()[0])
        else:
            if dryrun.lower() == "yes" and final_status == len(serverlist):
                return "Dry run was successful for all machines...."
            elif dryrun.lower() == "yes":
                return "ERROR: Dry run failed, please check the attribute syntax...."
    else:
        print("Invalid Launch Type !")

def multiprocessing_ce_update(launchtype, session, headers, endpoint, HOST, projectId, machinelist, dryrun, b, newlist, return_dict, status_list):
    dryrun_status = 0
    for blueprint in json.loads(b.text)["items"]:
        machineName = machinelist[blueprint["machineId"]]
        for server in newlist:
            if server['server_name'].lower() == machineName.lower():
                url = endpoint.format('projects/{}/blueprints/').format(projectId) + blueprint['id']
                blueprint["instanceType"] = server["instanceType"]
                if "iamRole" in server:
                    if server["iamRole"].lower() != "none":
                        blueprint["iamRole"] = server["iamRole"]
                if "tenancy" in server:
                    if server["tenancy"].lower() == "shared":
                        blueprint["tenancy"] = 'SHARED'
                    if server["tenancy"].lower() == "dedicated":
                        blueprint["tenancy"] = 'DEDICATED'
                    if server["tenancy"].lower() == "dedicated host":
                        blueprint["tenancy"] = 'HOST'
                for disk in blueprint["disks"]:
                    disk["type"] = "GP3"
                    disk["iops"] = 3000
                    disk["throughput"] = 125
                existing_subnetId = blueprint["subnetIDs"]
                existing_SecurityGroupIds = blueprint["securityGroupIDs"]
                existing_privateIPAction = blueprint["privateIPAction"]
                existing_privateIPs = blueprint["privateIPs"]
                if launchtype == "test":
                    if "subnet_IDs_test" in server:
                        blueprint["subnetIDs"] = server["subnet_IDs_test"]
                    else:
                        message = "ERROR: subnet_IDs_test attribute is empty for server: " + machineName +"."
                        return_dict[machineName] = message
                        break
                    if "securitygroup_IDs_test" in server:
                        blueprint["securityGroupIDs"] = server["securitygroup_IDs_test"]
                    else:
                        message = "ERROR: securitygroup_IDs_test attribute is empty for server: " + machineName +"."
                        return_dict[machineName] = message
                        break
                elif launchtype == "cutover":
                    if "subnet_IDs" in server:
                        blueprint["subnetIDs"] = server["subnet_IDs"]
                    else:
                        message = "ERROR: subnet_IDs attribute is empty for server: " + machineName +"."
                        return_dict[machineName] = message
                        break
                    if "securitygroup_IDs" in server:
                        blueprint["securityGroupIDs"] = server["securitygroup_IDs"]
                    else:
                        message = "ERROR: securitygroup_IDs attribute is empty for server: " + machineName +"."
                        return_dict[machineName] = message
                        break
                blueprint["publicIPAction"] = 'DONT_ALLOCATE'
                blueprint["privateIPAction"] = 'CREATE_NEW'
                # ***********  New Changes for supporting ENI/Private IP address as part of blueprint ***************

                if ("privateIPAction" in server.keys()) and (server.get("privateIPAction") is not None):
                    if server.get("privateIPAction", "") == "CUSTOM_IP":
                        # Case when privateIPAction is CUSTOM_IP. ie private static IP to be assigned to the instance.
                        blueprint['privateIPAction'] = "CUSTOM_IP"
                        if ("privateIPs" in server.keys()) and (server.get("privateIPs") is not None):
                            blueprint['privateIPs'] = server.get("privateIPs", "")
                        else:
                            return "ERROR: Provide privateIPs when privateIPAction is 'CUSTOM_IP'. " \
                                   "Server: " + server['server_name']
                    elif server.get("privateIPAction", "") == "USE_NETWORK_INTERFACE":
                        # Case when privateIPAction is USE_NETWORK_INTERFACE. ie Network interface to be assigned
                        # to the instance.
                        blueprint['privateIPAction'] = "USE_NETWORK_INTERFACE"
                        if ("networkInterface" in server.keys()) and (server.get("networkInterface") is not None):
                            blueprint['networkInterface'] = server.get("networkInterface", "")
                        else:
                            return "ERROR: Provide networkInterface when privateIPAction is 'USE_NETWORK_INTERFACE'. " \
                                   "Server: " + server['server_name']
                    else:
                        # Case when privateIPAction is CREATE_NEW or is not passed from the intake form
                        blueprint['privateIPAction'] = "CREATE_NEW"

                # *********** End of changes for supporting ENI/Private IP address as part of blueprint *************

                if "privateIPs" in server:
                    if len(server['privateIPs']) > 0:
                        if server['privateIPs'][0].strip() != "":
                            blueprint["privateIPs"] = server["privateIPs"]
                            blueprint["privateIPAction"] = 'CUSTOM_IP'
                tags = []
                existing_tag = []
                if 'tags' in server:
                    for tag in server['tags']:
                        keytag = tag['key']
                        valuetag = tag['value']
                        tag = {"key":keytag, "value":valuetag}
                        tags.append(tag)
                    existing_tag = blueprint["tags"]
                    blueprint["tags"] = tags
                result = requests.patch(HOST + url, data=json.dumps(blueprint), headers=headers, cookies=session)
                if result.status_code != 200:
                    message = "ERROR: Updating blueprint failed for machine: " + machineName +", invalid blueprint config "
                    if 'message' in result.text:
                        if json.loads(result.text)['message'] is not None:
                            message = message + "- " + json.loads(result.text)['message']
                    print(message)
                    return_dict[machineName] = message
                machinelist[blueprint["machineId"]] = "updated"
                print("Pid: " + str(os.getpid()) + " - Blueprint for machine: " + machineName + " updated....")
                if dryrun.lower() == "yes":
                    blueprint["subnetIDs"] = existing_subnetId
                    blueprint["securityGroupIDs"] = existing_SecurityGroupIds
                    blueprint["privateIPAction"] = existing_privateIPAction
                    blueprint["privateIPs"] = existing_privateIPs
                    if len(existing_tag) > 0:
                        blueprint["tags"] = existing_tag
                    result = requests.patch(HOST + url, data=json.dumps(blueprint), headers=headers, cookies=session)
                    if result.status_code != 200:
                        print(result.text)
                        return "ERROR: Failed to roll back subnet,SG and tags for machine: " + machineName +"...."
                    else:
                        print("Pid: " + str(os.getpid()) + " - Dryrun was successful for machine: " + machineName +"...." )
                        dryrun_status += 1
    status_list.append(dryrun_status)

def chunks(l, n):
    for i in range(0, n):
        yield l[i::n]