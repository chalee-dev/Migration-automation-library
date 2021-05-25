#!/usr/bin/python
import json
import xlrd
import csv
import argparse
import sys

import os

#1
def put_machine_names_from_csvfiles_in_array():
    print("")
    with open('myMachinesFromCloudendure.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        machine_names_in_csv = []
        for row in csv_reader:
            if line_count == 0:
                # print(f'\t{row[2]}')
                line_count += 1
            else:
                # print(f'\t{row[2]}')
                machine_names_in_csv.append(row[2])
                line_count += 1
        print(f'machines in CloudEndure (CSV) = {line_count-1}.')
        print(machine_names_in_csv)
        print("-------------")
        return machine_names_in_csv


#3
def get_field_location(sheet, col_string, row_with_field_names):
    col_num = -1
    # print(sheet.ncols)
    for col in range(sheet.ncols):
        if sheet.cell_value(row_with_field_names, col) == col_string:
            col_num = col
            # print(f'{col_string} name found in column {col_num}')
            break
    if col_num == -1:
        print(f'{col_string} name not found.')
    
    # print("----------")
    return col_num


#4
def put_server_names_from_excelfile_in_array(sheet, servers_col, waves_col, wave_name, row_with_field_names):
    machine_name_in_excel = []
    line_count = 0
    print("Total rows in the file = ", sheet.nrows)
    for nrow in range(row_with_field_names+1, sheet.nrows):
        if str(sheet.cell_value(nrow, waves_col)) == wave_name:
            machine_name_in_excel.append(str(sheet.cell_value(nrow, servers_col)))
            line_count += 1
    print (f'machines in Excel on wave {wave_name} = {line_count}')
    print (machine_name_in_excel)
    print("------")
    return (machine_name_in_excel)

#5
def compare_arrays_of_machine_names(csv, excel):
    update_machines = []
    item_count = 0
    for machine_excel in excel:
        for machine_csv in csv:
            if machine_csv == machine_excel:
                update_machines.append(machine_csv)
                item_count += 1
                break
    print(f'# of machines that match Excel file with CloudEndure = {item_count}')
    # create_csv(update_machines)
    print (update_machines)
    print("------")
    return update_machines


#6.1
# def create_csv(machines, sheet, app_col, servers_col, first_tag_col, last_tag_col, row_with_field_names):
def create_MigrationFactory_form_CSV(argswave, excel_servers, sheet, wave_id_col, tenancy_col, instanceType_col, iamRole_col, securitygroup_IDs_test_col, subnet_IDs_test_col, securitygroup_IDs_col, privateIPs_col, subnet_IDs_col, server_environment_col, server_tier_col, app_col, cloudendure_projectname_col, aws_accountid_col, servers_col, server_os_col, server_os_version_col, server_fqdn_col, first_tag_col, last_tag_col, row_with_field_names):

    export_csv = "MigrationFactoryForm_" + argswave + ".csv"
    file = open(export_csv, 'w+')
    # first row
    file.write('wave_id,app_name,cloudendure_projectname,aws_accountid,server_name,server_os,server_os_version,server_fqdn,server_tier,server_environment,subnet_IDs,privateIPs,securitygroup_IDs,subnet_IDs_test,securitygroup_IDs_test,iamRole,instanceType,tenancy\n')
    line_count = 0
    # print(machines)

    # start append tag process
    data = [sheet.row_values(i) for i in range(sheet.nrows)]

    # labels = data[1]  # Don't sort our headers
    data = data[row_with_field_names:]  # Data begins on the second row
    data = list(filter(lambda x: x[wave_id_col] == argswave, data))
    data.sort(key=lambda x: x[servers_col])

    for nrow in range(len(data)):
        # print(nrow)
        machine = data[nrow][servers_col]
        if nrow < len(data) - 1:
            # print(data[nrow][servers_col])
            # check if current server = to next server
            if data[nrow][servers_col] != data[nrow + 1][servers_col]:
                print(f'added blueprint to server {data[nrow][servers_col]}')
                v_wave_id_col = str(data[nrow][wave_id_col]).replace(",", " / ")
                v_app_col = str(data[nrow][app_col]).replace(",", " / ")
                v_cloudendure_projectname_col = str(data[nrow][cloudendure_projectname_col]).replace(",", " / ")
                v_servers_col = str(data[nrow][servers_col]).replace(",", " / ")

                if type(data[nrow][aws_accountid_col]) == float:
                    # print ('I am float')
                    v_aws_accountid_col = str(int(data[nrow][aws_accountid_col]))
                else:
                    v_aws_accountid_col = str(data[nrow][aws_accountid_col])


                v_server_os_col = str(data[nrow][server_os_col]).replace(",", " / ")
                v_server_os_version_col = str(data[nrow][server_os_version_col]).replace(",", " / ")
                v_server_fqdn_col = str(data[nrow][server_fqdn_col]).replace(",", " / ")
                v_server_tier_col = str(data[nrow][server_tier_col]).replace(",", " / ")
                v_server_environment_col = str(data[nrow][server_environment_col]).replace(",", " / ")
                v_subnet_IDs_col = str(data[nrow][subnet_IDs_col]).replace(",", " / ")
                v_privateIPs_col = str(data[nrow][privateIPs_col]).replace(",", " / ")
                v_securitygroup_IDs_col = str(data[nrow][securitygroup_IDs_col]).replace(",", " / ")
                v_subnet_IDs_test_col = str(data[nrow][subnet_IDs_test_col]).replace(",", " / ")
                v_securitygroup_IDs_test_col = str(data[nrow][securitygroup_IDs_test_col]).replace(",", " / ")
                v_iamRole_col = str(data[nrow][iamRole_col]).replace(",", " / ")
                v_instanceType_col = str(data[nrow][instanceType_col]).replace(",", " / ")
                v_tenancy_col = str(data[nrow][tenancy_col]).replace(",", " / ")

                file.write(f'{v_wave_id_col},'
                           f'{v_app_col},'
                           f'{v_cloudendure_projectname_col},'                           
                           f'{v_aws_accountid_col},'
                           f'{v_servers_col},'
                           f'{v_server_os_col},'
                           f'{v_server_os_version_col},'
                           f'{v_server_fqdn_col},'
                           f'{v_server_tier_col},'
                           f'{v_server_environment_col},'
                           f'{v_subnet_IDs_col},'
                           f'{v_privateIPs_col},'
                           f'{v_securitygroup_IDs_col},'
                           f'{v_subnet_IDs_test_col},'
                           f'{v_securitygroup_IDs_test_col},'
                           f'{v_iamRole_col},'
                           f'{v_instanceType_col},'
                           f'{v_tenancy_col}\n')

            else:
                # print("append app name")
                if data[nrow][cloudendure_projectname_col] == data[nrow + 1][cloudendure_projectname_col] \
                        and data[nrow][aws_accountid_col] == data[nrow + 1][aws_accountid_col]\
                        and data[nrow][server_os_col] == data[nrow + 1][server_os_col]\
                        and data[nrow][server_os_version_col] == data[nrow + 1][server_os_version_col]\
                        and data[nrow][server_fqdn_col] == data[nrow + 1][server_fqdn_col]\
                        and data[nrow][server_tier_col] == data[nrow + 1][server_tier_col]\
                        and data[nrow][server_environment_col] == data[nrow + 1][server_environment_col]\
                        and data[nrow][subnet_IDs_col] == data[nrow + 1][subnet_IDs_col]\
                        and data[nrow][privateIPs_col] == data[nrow + 1][privateIPs_col]\
                        and data[nrow][securitygroup_IDs_col] == data[nrow + 1][securitygroup_IDs_col] \
                        and data[nrow][subnet_IDs_test_col] == data[nrow + 1][subnet_IDs_test_col] \
                        and data[nrow][securitygroup_IDs_test_col] == data[nrow + 1][securitygroup_IDs_test_col] \
                        and data[nrow][iamRole_col] == data[nrow + 1][iamRole_col]\
                        and data[nrow][instanceType_col] == data[nrow + 1][instanceType_col]\
                        and data[nrow][tenancy_col] == data[nrow + 1][tenancy_col]:

                    if type(data[nrow][app_col]) == float:
                        data[nrow][app_col] = str(int(data[nrow][app_col])).replace((",", " / "))
                    if type(data[nrow + 1][app_col]) == float:
                        data[nrow + 1][app_col] = str(int(data[nrow + 1][app_col])).replace(",", " / ")
                    data[nrow + 1][app_col] = str(data[nrow + 1][app_col]) + " / " + str(data[nrow][app_col])
                else:
                    print(f'Server blueprint does not match for server {data[nrow][servers_col]}. Check your excel file')
                    sys.exit()

        if nrow == len(data) - 1:
            v_wave_id_col = str(data[nrow][wave_id_col]).replace(",", " / ")
            v_app_col = str(data[nrow][app_col]).replace(",", " / ")
            v_cloudendure_projectname_col = str(data[nrow][cloudendure_projectname_col]).replace(",", " / ")
            v_servers_col = str(data[nrow][servers_col]).replace(",", " / ")

            if type(data[nrow][aws_accountid_col]) == float:
                # print ('I am float')
                v_aws_accountid_col = str(int(data[nrow][aws_accountid_col]))
            else:
                v_aws_accountid_col = str(data[nrow][aws_accountid_col])

            v_server_os_col = str(data[nrow][server_os_col]).replace(",", " / ")
            v_server_os_version_col = str(data[nrow][server_os_version_col]).replace(",", " / ")
            v_server_fqdn_col = str(data[nrow][server_fqdn_col]).replace(",", " / ")
            v_server_tier_col = str(data[nrow][server_tier_col]).replace(",", " / ")
            v_server_environment_col = str(data[nrow][server_environment_col]).replace(",", " / ")
            v_subnet_IDs_col = str(data[nrow][subnet_IDs_col]).replace(",", " / ")
            v_privateIPs_col = str(data[nrow][privateIPs_col]).replace(",", " / ")
            v_securitygroup_IDs_col = str(data[nrow][securitygroup_IDs_col]).replace(",", " / ")
            v_subnet_IDs_test_col = str(data[nrow][subnet_IDs_test_col]).replace(",", " / ")
            v_securitygroup_IDs_test_col = str(data[nrow][securitygroup_IDs_test_col]).replace(",", " / ")
            v_iamRole_col = str(data[nrow][iamRole_col]).replace(",", " / ")
            v_instanceType_col = str(data[nrow][instanceType_col]).replace(",", " / ")
            v_tenancy_col = str(data[nrow][tenancy_col]).replace(",", " / ")

            print(f'last row - added blueprint normally to {data[nrow][servers_col]}')

            file.write(f'{v_wave_id_col},'
                       f'{v_app_col},'
                       f'{v_cloudendure_projectname_col},'
                       f'{v_aws_accountid_col},'
                       f'{v_servers_col},'
                       f'{v_server_os_col},'
                       f'{v_server_os_version_col},'
                       f'{v_server_fqdn_col},'
                       f'{v_server_tier_col},'
                       f'{v_server_environment_col},'
                       f'{v_subnet_IDs_col},'
                       f'{v_privateIPs_col},'
                       f'{v_securitygroup_IDs_col},'
                       f'{v_subnet_IDs_test_col},'
                       f'{v_securitygroup_IDs_test_col},'
                       f'{v_iamRole_col},'
                       f'{v_instanceType_col},'
                       f'{v_tenancy_col}\n')


#6.3
# def create_csv(machines, sheet, app_col, servers_col, first_tag_col, last_tag_col, row_with_field_names):
def create_MigrationFactory_tag_CSV(argswave, waves_col, excel_servers, sheet, servers_col, first_tag_col, last_tag_col, row_with_field_names):

    export_csv = "MigrationFactoryTAG_" + argswave + ".csv"
    file = open(export_csv, 'w+')
    # first row
    file.write('Name,')
    for tag_num in range(first_tag_col, last_tag_col+1):
        # remove .0 from the end of string
        check_string = (sheet.cell_value(row_with_field_names, tag_num))
        file.write(f'{check_string}')
        if tag_num < last_tag_col:
            file.write(",")
    file.write(f'\n')
    line_count = 0
    # print(excel_servers)
    # end of the first row

    # start append tag process
    data = [sheet.row_values(i) for i in range(sheet.nrows)]

    # labels = data[1]  # Don't sort our headers
    data = data[row_with_field_names:]  # Data begins on the second row
    data = list(filter(lambda x: x[waves_col] == argswave, data))
    data.sort(key=lambda x: x[servers_col])

    for nrow in range(len(data)):
        # print(nrow)
        if nrow < len(data)-1:
            # print(data[nrow][servers_col])
            # check if current server = to next server
            if data[nrow][servers_col] != data[nrow+1][servers_col]:
                print(f'added tag normally to {data[nrow][servers_col]}')
                file.write(f'{data[nrow][servers_col]},{format_tags(data, nrow, first_tag_col, last_tag_col)}\n')
            else:
                # print("append if tag is different")
                for tag_num in range(first_tag_col, last_tag_col + 1):
                    if data[nrow][tag_num] != data[nrow+1][tag_num]:
                        if type(data[nrow][tag_num]) == float:
                            data[nrow][tag_num] = str(int(data[nrow][tag_num]))
                        if type(data[nrow+1][tag_num]) == float:
                            data[nrow+1][tag_num] = str(int(data[nrow+1][tag_num]))
                        data[nrow + 1][tag_num] = str(data[nrow+1][tag_num]) + " / " + str(data[nrow][tag_num])

        if nrow == len(data)-1:
            print(f'last row - added tags normally to {data[nrow][servers_col]}')
            file.write(f'{data[nrow][servers_col]},{format_tags(data, nrow, first_tag_col, last_tag_col)}\n')
    # for machine in excel_servers:
    #     file.write(f'{machine},{format_tags(sheet, machine, first_tag_col, last_tag_col, servers_col)}\n')

# 6.4
def format_tags(data, nrow, first_tag_col, last_tag_col):
    string_tag = ""
    # add key value to string_tag
    for tag_num in range(first_tag_col, last_tag_col+1):
        # remove .0 from the end of string
        check_string = data[nrow][tag_num]
        if type(check_string) == float:
            # print ('I am float')
            value = str(int(check_string))
        else:
            value = str(check_string)
        value = value.replace(",", " / ")
        string_tag += value
        if tag_num < last_tag_col:
            string_tag += ","
    return string_tag 
#### excelToCE end ####




###################################################################################################



def main(args):
	print(chr(27) + "[2J")
	print("Excel To Migration Factory")
	while (args.wave is None) or (args.wave == ''):
		args.wave = input("Enter wave. Ex. R02W03:")


# This main function gets all the servers and project in an account and create a csv file to be
# used as a template input file to update the blueprints
# 
# Usage: main(args)


	###### ExcelToCE start ########

	wb_machine_names =  xlrd.open_workbook(args.inputfile)

	with open('0-ConfigExcelToMigrationFactory.json') as json_file:
		data = json.load(json_file)
		for param in data['config']:
			# wb_machine_names = xlrd.open_workbook(param['Excel_File_Name'])
			sheet = wb_machine_names.sheet_by_name(param['Excel_Tab_Name'])
			row_with_field_names = param['Row_With_Field_Names'] - 1
			server_col_string = param['Server_Column_Name']
			wave_col_string = param['Wave_Column_Name']
			wave_id_col_string = param['wave_id_Column_Name']
			app_name_string = param['Application_Column_Name']
			cloudendure_projectname_string = param['cloudendure_projectname_Column_Name']
			aws_accountid_string = param['aws_accountid_Column_Name']
			server_os_string = param['server_os_Column_Name']
			server_os_version_string = param['server_os_version_Column_Name']
			server_fqdn_string = param['server_fqdn_Column_Name']
			server_tier_string = param['server_tier_Column_Name']
			server_environment_string = param['server_environment_Column_Name']
			subnet_IDs_string = param['subnet_IDs_Column_Name']
			privateIPs_string = param['privateIPs_Column_Name']
			securitygroup_IDs_string = param['securitygroup_IDs_Column_Name']
			subnet_IDs_test_string = param['subnet_IDs_test_Column_Name']
			securitygroup_IDs_test_string = param['securitygroup_IDs_test_Column_Name']
			iamRole_string = param['iamRole_Column_Name']
			instanceType_string = param['instanceType_Column_Name']
			tenancy_string = param['tenancy_Column_Name']
			first_tag_string = param['First_Tag_Name']
			last_tag_string = param['Last_Tag_Name']

	#3
	servers_col = get_field_location(sheet, server_col_string, row_with_field_names)
	waves_col = get_field_location(sheet, wave_col_string, row_with_field_names)
	wave_id_col = get_field_location(sheet, wave_id_col_string, row_with_field_names)
	first_tag_col = get_field_location(sheet, first_tag_string, row_with_field_names)
	last_tag_col = get_field_location(sheet, last_tag_string, row_with_field_names)
	cloudendure_projectname_col = get_field_location(sheet, cloudendure_projectname_string, row_with_field_names)
	aws_accountid_col = get_field_location(sheet, aws_accountid_string, row_with_field_names)
	server_os_col = get_field_location(sheet, server_os_string, row_with_field_names)
	server_os_version_col = get_field_location(sheet, server_os_version_string, row_with_field_names)
	server_fqdn_col = get_field_location(sheet, server_fqdn_string, row_with_field_names)
	server_tier_col = get_field_location(sheet, server_tier_string, row_with_field_names)
	server_environment_col = get_field_location(sheet, server_environment_string, row_with_field_names)
	subnet_IDs_col = get_field_location(sheet, subnet_IDs_string, row_with_field_names)
	privateIPs_col = get_field_location(sheet, privateIPs_string, row_with_field_names)
	securitygroup_IDs_col = get_field_location(sheet, securitygroup_IDs_string, row_with_field_names)
	subnet_IDs_test_col = get_field_location(sheet, subnet_IDs_test_string, row_with_field_names)
	securitygroup_IDs_test_col = get_field_location(sheet, securitygroup_IDs_test_string, row_with_field_names)
	iamRole_col = get_field_location(sheet, iamRole_string, row_with_field_names)
	instanceType_col = get_field_location(sheet, instanceType_string, row_with_field_names)
	tenancy_col = get_field_location(sheet, tenancy_string, row_with_field_names)
	app_col = get_field_location(sheet, app_name_string, row_with_field_names)
	#4
	excel_servers = put_server_names_from_excelfile_in_array(sheet, servers_col, waves_col, args.wave, row_with_field_names)
	#5
	# machines = compare_arrays_of_machine_names(csv_machines, excel_servers)
	#6
	create_MigrationFactory_form_CSV(args.wave, excel_servers, sheet, wave_id_col ,tenancy_col, instanceType_col, iamRole_col, securitygroup_IDs_test_col, subnet_IDs_test_col, securitygroup_IDs_col, privateIPs_col, subnet_IDs_col, server_environment_col, server_tier_col, app_col, cloudendure_projectname_col, aws_accountid_col, servers_col, server_os_col, server_os_version_col, server_fqdn_col, first_tag_col, last_tag_col, row_with_field_names)
	create_MigrationFactory_tag_CSV(args.wave, waves_col, excel_servers, sheet, servers_col, first_tag_col, last_tag_col, row_with_field_names)
	goforintakeform = input("update Blueprint? (Y/N) ->")
	if goforintakeform == "Y" or goforintakeform == "y":
		os.system('python 0-Import-intake-form.py --Intakeform MigrationFactoryForm_' + args.wave + '.csv')
	gofortag = input("update TAGs? (Y/N) ->")
	if gofortag == "Y" or gofortag == "y":
		os.system('python 0-import-tags.py --Intakeform MigrationFactoryTAG_' + args.wave + '.csv')

###### excelToCE end ########


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	# parser.add_argument('-u', '--user', required=False, help='User name')
	# parser.add_argument('-p', '--password', required=False, help='Password')
	# ##### excelToCE start ######
	# parser.add_argument('-t', '--task', required=False, help='<add>, <del> or <dryrun>')
	parser.add_argument('-w', '--wave', required=False, help='example R0xWxx, Pilot or <all> for all server on spreadsheet')
	# ###### excelToCE end ########
	parser.add_argument('-i', '--inputfile', required=True, help='Excel file')
	main(args = parser.parse_args())


