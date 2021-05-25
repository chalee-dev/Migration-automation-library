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

import json
import os
import getpass

# ================== CEMF Helper Functions =======================

def read_file(filename):
    f = open(filename, "r")
    value = f.read()
    f.close()
    return value

def write_file(filename, stringData):
    f = open(filename, "w")
    f.write(stringData)
    f.close()

def get_cemf_settings():
    if not os.path.exists("cemf_settings.json"):
        return {} # return empty json object

    jsonString = read_file("cemf_settings.json")
    data = json.loads(jsonString)
    return data

def save_cemf_settings(jsonObject):
    data = json.dumps(jsonObject)
    write_file("cemf_settings.json", data)

def delete_cemf_settings():
    if os.path.exists("cemf_settings.json"):
        os.remove("cemf_settings.json")

def enter_windows_account():
    pass_first = getpass.getpass("Windows User Password: ")
    pass_second = getpass.getpass("Re-enter Password: ")

    while(pass_first != pass_second):
        print("Password mismatch, please try again!")
        pass_first = getpass.getpass("Windows User Password: ")
        pass_second = getpass.getpass("Re-enter Password: ")

    return pass_second

def ask_windows_account(settings, user_name, pass_key, account_answer):

    # answer is Apply the same account to all remaining servers
    if account_answer == "A":
        return user_name, pass_key, account_answer

    if "windowsUsername" in settings:
        # settings for Windows account exist then confirm if the user wants to use it.
        print("Do you want to use previously entered Windows account?")
        print("Enter [Y] if you want to use previously entered account")
        print("Enter [A] if you want to apply the same account to all remaining servers")
        print("Enter any key if you want to enter password")
        account_answer = input("Answer: ").upper()

        if account_answer == "Y":
            # get the account from settings file 
            user_name = settings["windowsUsername"]
            pass_key = settings["windowsPassword"]
            print("Using previously entered account with username '"+ user_name + "'...")

        elif account_answer == "A":
            user_name = settings["windowsUsername"]
            pass_key = settings["windowsPassword"]
            print("Using previously entered account with username '"+ user_name + "' to all windows servers...")
            
        elif account_answer != "A" :
            # ask for the account
            pass_key = enter_windows_account()

            # save account
            settings["windowsUsername"] = user_name
            settings["windowsPassword"] = pass_key
            save_cemf_settings(settings);

    else:
        # ask for the account if no account in settings
        pass_key = enter_windows_account()

        # save account
        settings["windowsUsername"] = user_name
        settings["windowsPassword"] = pass_key
        save_cemf_settings(settings);

    return user_name, pass_key, account_answer

def enter_linux_account():
    
    user_name = input("Linux Username: ")
    pass_key_second = ""
    pass_key = ""
    has_key = input("If you use a private key to login, press [Y] or if use password press [N]: ")

    if has_key.lower() in 'y':
        pass_key = input('Private Key file name: ')
    else:
        pass_key_first = getpass.getpass('Linux Password: ')
        pass_key_second = getpass.getpass('Re-enter Password: ')
        while(pass_key_first != pass_key_second):
            print("Password mismatch, please try again!")
            pass_key_first = getpass.getpass('Linux Password: ')
            pass_key_second = getpass.getpass('Re-enter Password: ')
        pass_key = pass_key_second

    return user_name, pass_key, has_key

def ask_linux_account(settings, user_name, pass_key, account_answer, has_key):

    # answer is Apply the same account to all remaining servers
    if account_answer == "A":
        return user_name, pass_key, account_answer, has_key

    if "linuxUsername" in settings:
        # settings for linux account exist then confirm if the user wants to use it.
        print("Do you want to use previously entered Linux account?")
        print("Enter [Y] if you want to use previously entered account")
        print("Enter [A] if you want to apply the same account to all remaining servers")
        print("Enter any key if you want to enter password")
        account_answer = input("Answer: ").upper()

        if account_answer == "Y":
            # get the account from settings file 
            user_name = settings["linuxUsername"]
            pass_key = settings["linuxPassword"]
            has_key = settings["linuxHas_key"]
            print("Using previously entered account with username '"+ user_name + "'...")

        elif account_answer == "A":
            user_name = settings["linuxUsername"]
            pass_key = settings["linuxPassword"]
            has_key = settings["linuxHas_key"]
            print("Using previously entered account with username '"+ user_name + "' to all linux servers...")
            
        elif account_answer != "A" :
            # ask for the account
            user_name, pass_key, has_key = enter_linux_account()

            # save account
            settings["linuxUsername"] = user_name
            settings["linuxPassword"] = pass_key
            settings["linuxHas_key"] = has_key
            save_cemf_settings(settings);

    else:
        # ask for the account if no account in settings
        user_name, pass_key, has_key = enter_linux_account()

        # save account
        settings["linuxUsername"] = user_name
        settings["linuxPassword"] = pass_key
        settings["linuxHas_key"] = has_key
        save_cemf_settings(settings);

    return user_name, pass_key, account_answer, has_key


def ask_ce_api_key(settings):

    answer = ""
    apiKey = ""
    
    if "CEApiKey" in settings :
        apiKey = settings["CEApiKey"]
        print("We found CloudEndure API Token that starts with '" + apiKey[:6] + "' and ends with '" + apiKey[50:] + "'.")
        print("Do you want to use this CloudEndure API Token? Enter [Y] if yes, or press any key to input your CloudEndure API Token.")
        answer = input("Answer: ").upper()

        if "Y" in answer:
            print("Using existing token: '" + apiKey[:6] + "' ..... '" + apiKey[50:] + "'.")
        else:
            apiKey = input('CE API Token: ')
            settings["CEApiKey"] = apiKey
            save_cemf_settings(settings)

    else:
        apiKey = input('CE API Token: ')
        settings["CEApiKey"] = apiKey
        save_cemf_settings(settings)
        

    return apiKey