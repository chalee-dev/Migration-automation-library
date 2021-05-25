# Remove servers from CE Console after migration

Script performs a delete of a wave's servers from the CE console which initiates agent uninstallation, it also provides some guard rails to ensure that servers are not deleted that have never been cutover and/or within a configurable time after cutover. This prevents accidental deletions of the servers from the CE console which lead to replication restarts that could cost time and effort.

## Key features
- Ability to specify the number of days after a Cutover was last completed and automatically remove only those systems from console. [default 21 days but configurable]
- Ability to run a DryRun of the command to verify the current status of the servers in the console before running in Live Mode.
- Ability to override all defaults and remove all servers from the CEN console regardless of status.

## CEMF requirements
This script was built and tested against version v1.0 of CEMF.

## Deployment

The script has 2 files, these need to both be copied to the scripts folder on the Execution server in order for the script to work.
- mfcommon.py is a new generic modules script that will be introduced in future releases for all existing scripts.
- 5-Remove-Agents.py provides the functions to remove agents from the console.

## Usage

Command: python 5-Remove-Agent.py --Waveid <no.>

Outcome: A non-disruptive run will be performed and output will show what actions would be performed if the parameter --LiveRun True was added.
By default the script will verify the last cutover date that CE has stored is over 21 days ago and if so will notify of removal of the agent, the script will provide an informational message for any server that has not been cutover, and also it will provide a date when removal can occur if the server is within the cutover days specified.

The command has the following optional parameters:
### --LiveRun [ default = False]
> Specifying --LiveRun True will tell the script to actually perform the deletion of the server from the console. By default the script runs in test mode, only reporting what the outcome would be without making changes.

### --CutoverDays [ default = 21 ]
> Allows the user to specify a different number of days after cutover to remove agents. By default this is 21 days.
i.e --CutoverDays 30 would then only remove servers that were cutover 30 days ago or more.

### --ForceRemoval [ default = false ]
> WARNING!!! specifying --ForceRemoval True will force the script to ignore the CutoverDays and remove the agents from all servers in the wave regardless of the status. This includes servers that have never been cutover.

## Example output

### Not been cutover.
'c:\migrations\scripts>5-Remove-Agents.py --Waveid 1
THIS IS A TEST RUN, NO CHANGES WILL BE MADE TO THE SYSTEMS!
******************************
* Login to Migration factory *
******************************
Migration Factory : You have successfully logged in


************************
* Login to CloudEndure *
************************
CE API Token: [my API token]
CloudEndure : You have successfully logged in

***********************
* Getting Server List *
***********************

***** Servers for CE Project: project1 *****
EC2AMAZ-J7IS2TD


********************************
*  Remove Agents that are over *
* 21 days after cutover  *
********************************


***** Replication Status for CE Project: project1 *****
EC2AMAZ-J7IS2TD - TEST RUN : Server has not been cutover, no action would be taken.'

### Cutover but still within the the number of days after cutover.
'c:\migrations\scripts>5-Remove-Agents.py --Waveid 3
THIS IS A TEST RUN, NO CHANGES WILL BE MADE TO THE SYSTEMS!
******************************
* Login to Migration factory *
******************************
Migration Factory : You have successfully logged in


************************
* Login to CloudEndure *
************************
CE API Token: [my API token]
CloudEndure : You have successfully logged in

***********************
* Getting Server List *
***********************

***** Servers for CE Project: project1 *****
ip-172-31-41-96.eu-central-1.compute.internal


********************************
*  Remove Agents that are over *
* 21 days after cutover  *
********************************


***** Replication Status for CE Project: project1 *****
ip-172-31-41-96.eu-central-1.compute.internal - TEST RUN : Cutover was within 21 Days please attempt after 2021-05-14.'
