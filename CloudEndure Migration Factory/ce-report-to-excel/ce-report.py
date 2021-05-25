# Generates a CloudEndure Report for all Machines in Excel format.

import xlsxwriter
import requests
import json
import sys
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d_%H_%M_%S")

excelfilename = "ce-report-"+dt_string+".xlsx"
# Create an new Excel file and add a worksheet.

workbook = xlsxwriter.Workbook(excelfilename)
ws_rawdata = workbook.add_worksheet("All Servers")
ws_filter = workbook.add_worksheet("Filtered")
ws_report = workbook.add_worksheet("Report")


cell_num = workbook.add_format()
cell_num.set_num_format('#,##0')
cell_num.set_align('center')
cell_num.set_align('vcenter')


ws_rawdata.freeze_panes(1, 2)
ws_filter.freeze_panes(1, 2)

# Widen Column
ws_rawdata.set_column('A:A', 20)
ws_rawdata.set_column('B:B', 40)
ws_rawdata.set_column('C:D', 20)
ws_rawdata.set_column('E:J', 32)
ws_rawdata.set_column('K:N', 20)
ws_rawdata.set_column('O:O', 45)


# Widen Column
ws_filter.set_column('A:A', 20)
ws_filter.set_column('B:B', 40)
ws_filter.set_column('C:D', 20)
ws_filter.set_column('E:J', 32)
ws_filter.set_column('K:N', 20)
ws_filter.set_column('O:O', 45)

# Widen Column
ws_report.set_column('A:A', 20)
ws_report.set_column('B:B', 12)

table_raw = {'autofilter': True, 'header_row': True, 'name': 'raw','columns': [\
    {'header': 'Server Name'},\
    {'header': 'Project Name'},\
    {'header': 'Agent Installed?'},\
    {'header': 'Replication Status'},\
    {'header': 'Agente Installation Date'},\
    {'header': 'Last Test'},\
    {'header': 'Cutover Date'},\
    {'header': 'Last Seen'},\
    {'header': 'Last Consistent'},\
    {'header': 'ETA Next Consistent'},\
    {'header': 'Total Storage'},\
    {'header': 'Replication Storage'},\
    {'header': 'Backlog'},\
    {'header': 'Rescanned Storage'},\
	{'header': 'OS'}]}

table_filter = {'autofilter': True, 'header_row': True, 'name': 'filter','columns': [\
    {'header': 'Server Name'},\
    {'header': 'Project Name'},\
    {'header': 'Agent Installed?'},\
    {'header': 'Replication Status'},\
    {'header': 'Agente Installation Date'},\
    {'header': 'Last Test'},\
    {'header': 'Cutover Date'},\
    {'header': 'Last Seen'},\
    {'header': 'Last Consistent'},\
    {'header': 'ETA Next Consistent'},\
    {'header': 'Total Storage'},\
    {'header': 'Replication Storage'},\
    {'header': 'Backlog'},\
    {'header': 'Rescanned Storage'},\
	{'header': 'OS'}]}



HOST = 'https://console.cloudendure.com'
headers = {'Content-Type': 'application/json'}

# remove the comment for the next 3 rows want to use userAPIToken as parameter instead of Username and password
# if len(sys.argv) != 2:
# 	print ("Usage: CloudEndureAPIExample.py userApiToken")
# 	sys.exit(10)

session = {}

endpoint = '/api/latest/{}'

p_user = input("CloudEndure user (email):")
import getpass 
  
try: 
    p_pass = getpass.getpass() 
except Exception as error: 
    print('ERROR', error) 
else: 
    print('Wait...') 

# remove comment below to use userApiToken as argument
# login_data = {'userApiToken': sys.argv[1]}

# Comment the line bolow to use userApiTokon as agument
login_data = {"username": p_user,"password": p_pass}

r = requests.post(HOST + endpoint.format('login'), data = json.dumps(login_data), headers = headers)
if r.status_code != 200 and r.status_code != 307:
	print ("Bad login credentials")
	sys.exit(1)

# check if need to use a different API entry point
if r.history:
	endpoint = '/' + '/'.join(r.url.split('/')[3:-1]) + '/{}'
	r = requests.post(HOST + endpoint.format('login'), data = json.dumps(login_data), headers = headers)

session = {'session': r.cookies['session']}

headers['X-XSRF-TOKEN'] = r.cookies['XSRF-TOKEN']

r = requests.get(HOST + endpoint.format('projects'), headers = headers, cookies = session)
if r.status_code != 200:
	print ("Failed to fetch the project")
	sys.exit(2)

try:
# Write some numbers, with row/column notation.
	# firstrow = [\
	# "Server Name",\
	# "Project Name",\
	# "Agent installed Date",\
	# "Last Test",\
	# "Cutover",\
	# "Last Seen",\
	# "Last Consistent",\
	# "Estimated Next Consistent",\
	# "Total Storage",\
	# "Replicated Storage",\
	# "Backlog",\
	# "Rescanned Storage"]

	row_num = 0
	# column_num = 0
	# for column_name in firstrow:
	# 	ws_rawdata.write(row_num, column_num, column_name)
	# 	column_num += 1
	row_num +=1

	projects = json.loads(r.content)['items']
	for project in projects:
		machines = False
		project_id = project['id']
		r = requests.get(HOST + endpoint.format('projects/{}/machines?all=true').format(project_id), headers = headers, cookies = session)
		if r.status_code != 200:
			print ("Failed to fetch the machines")
			sys.exit(5)


		for machine in json.loads(r.content)['items']:
			backlog = 0

			if 'backloggedStorageBytes' in machine['replicationInfo']:
				backlog = machine['replicationInfo']['backloggedStorageBytes']
			else:
				backlog = 0

			if 'lastConsistencyDateTime' in machine['replicationInfo']:
				last_consistent = machine['replicationInfo']['lastConsistencyDateTime']
			else:
				last_consistent = 'Not Available'

			if 'lastTestLaunchDateTime' in machine['lifeCycle']:
				testDate = machine['lifeCycle']['lastTestLaunchDateTime']
			else:
				testDate = 'Not Available'

			if 'lastCutoverDateTime' in machine['lifeCycle']:
				cutoverDate = machine['lifeCycle']['lastCutoverDateTime']
			else:
				cutoverDate = 'Not Available'

			if 'agentInstallationDateTime' in machine['lifeCycle']:
				AgentDate = machine['lifeCycle']['agentInstallationDateTime']
			else:
				AgentDate = 'Not Available'

			if 'rescannedStorageBytes' in machine['replicationInfo']:
				rescannedStorage = machine['replicationInfo']['rescannedStorageBytes']
			else:
				rescannedStorage = 'Not Available'

			if 'nextConsistencyEstimatedDateTime' in machine['replicationInfo']:
				nextConsistencyEstimatedDateTime = machine['replicationInfo']['nextConsistencyEstimatedDateTime']
			else:
				nextConsistencyEstimatedDateTime = 'Not Available'

			if 'replicatedStorageBytes' in machine['replicationInfo']:
				replicatedStorageBytes = machine['replicationInfo']['replicatedStorageBytes']
			else:
				replicatedStorageBytes = 'Not Available'

			if 'totalStorageBytes' in machine['replicationInfo']:
				totalStorageBytes = machine['replicationInfo']['totalStorageBytes']
			else:
				totalStorageBytes = 'Not Available'

			if 'lastSeenDateTime' in machine['replicationInfo']:
				lastSeenDateTime = machine['replicationInfo']['lastSeenDateTime']
			else:
				lastSeenDateTime = 'Not Available'
			
			


			api_data =[machine['sourceProperties']['name'],\
            project['name'], \
            machine['isAgentInstalled'],\
            machine['replicationStatus'],\
            AgentDate,\
			testDate,\
            cutoverDate,\
            lastSeenDateTime,\
			last_consistent,\
			nextConsistencyEstimatedDateTime,\
			totalStorageBytes,\
			replicatedStorageBytes,\
			backlog,\
			rescannedStorage,\
			machine['sourceProperties']['os']]

			column_num = 0
			for column_api_data in api_data:
				ws_rawdata.write(row_num, column_num, column_api_data, cell_num)

                
				# vlookup start
				if column_num > 0:
					# look = "=VLOOKUP($A"+str(row_num+1)+",raw[],"+str(column_num+1)+",FALSE)"
					look = '=IF(A'+str(row_num+1)+'="","",VLOOKUP($A'+str(row_num+1)+',raw[],'+str(column_num+1)+',FALSE))'
					# =IF(A2="","",VLOOKUP($A2,raw,2,FALSE))		
					# look = "=VLOOKUP($A"+str(row_num+1)+",raw data'!$A$2:$Z$10000,"+str(column_num+1)+",FALSE)"
					ws_filter.write(row_num, column_num, look, cell_num)
				# vlookup end

				column_num +=1
			row_num +=1

			machines = True

		# if not machines:
		# 	# print ('No machines for project {}'.format(project['name']))
	
	# ws_rawdata.autofilter(0,0,row_num, column_num-1)

    
# table

	ws_rawdata.add_table(0,0,row_num-1, column_num-1, table_raw)
	ws_filter.add_table(0,0,row_num-1, column_num-1, table_filter)
	# ws_report.add_table(0,0,5,1, table_report)
	# report tab start

	ws_report.write(0,0,"Task",cell_num)
	ws_report.write(0,1,"# of Servers",cell_num)

	ws_report.write(1,0,"Agent installed")
	ws_report.write(1,1,"=COUNTIFS('All Servers'!C2:C" + str(row_num) + ",\"=TRUE\")",cell_num)

	ws_report.write(2,0,"Cutover")
	ws_report.write(2,1,"=COUNTIFS('All Servers'!C2:C" + str(row_num) + ",\"=TRUE\",'All Servers'!G2:G" + str(row_num) + ",\"<>Not Available\")",cell_num)

	ws_report.write(3,0,"Ready for Testing")
	ws_report.write(3,1,"=COUNTIFS('All Servers'!C2:C" + str(row_num) + ",\"=TRUE\",'All Servers'!F2:F" + str(row_num) + ",\"=Not Available\",'All Servers'!I2:I" + str(row_num) + ",\"<>Not Available\")",cell_num)
	
	ws_report.write(4,0,"Tested")
	ws_report.write(4,1,"=COUNTIFS('All Servers'!C2:C" + str(row_num) + ",\"=TRUE\",'All Servers'!F2:F" + str(row_num) + ",\"<>Not Available\",'All Servers'!G2:G" + str(row_num) + ",\"=Not Available\",'All Servers'!I2:I" + str(row_num) + ",\"<>Not Available\")",cell_num)

	ws_report.write(5,0,"NOT Ready for Testing")
	ws_report.write(5,1,"=COUNTIFS('All Servers'!C2:C" + str(row_num) + ",\"=TRUE\",'All Servers'!F2:F" + str(row_num) + ",\"=Not Available\",'All Servers'!I2:I" + str(row_num) + ",\"=Not Available\")",cell_num)


	# report tab end

	print(f'Excel file created: {excelfilename}')
except:
	print ("Error / No associated project")
	sys.exit(3)

finally:
	workbook.close()
	print("Job Complete.")