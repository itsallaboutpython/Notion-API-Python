# Importing required modules
from getopt import GetoptError, getopt # To analyze command line arguments
import requests # Requests library is used to make HTTP requests to Notion API
import json # json library to process data as json
import art # To make the script more attractive
import sys # To analyze command line arguments
from prettytable import PrettyTable # To display data in pretty table format

# Global variables
url = 'https://api.notion.com/v1/databases/'
database_id = ''
integration_token = ''

# Retrieve database ID from files
with open("database_id.txt", 'r') as file:
    database_id = file.read()

# Retrieve integration token from files
with open("integration_token.txt", 'r') as file:
    integration_token = file.read()

# This is how the curl GET request should be
'''
curl -X GET https://api.notion.com/v1/database/{database_id} \
  -H "Authorization: Bearer {INEGRATION_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2021-05-13" \
'''

# Set URL, request headers and response
url = url + database_id
request_headers = {
    "Authorization":integration_token,
    "Content-Type":"application/json",
    "Notion-Version": "2021-05-13"
}
response = None


# Check for connectivity with notion API
def check_connectivity():

    # Send get request to API and capture response
    response = requests.get(url, headers = request_headers)

    # If response status code is 2000 i.e. the response is successfull
    # continue and leave the function
    if response.status_code == 200:
        return 0

    # In case if the response is incorrect
    else:
        # Check for internet connectivity
        try:
            # Trying to send a get request to google.com to check what happens
            resp = requests.get("https://www.google.com")

            # If we are able to connect to google.com, this means internet conenction is present
            # Which means, there must be something wrong with database ID or integration token
            if resp.status_code == 200:
                print("Something is wrong with you database Id or intergation token.")
                print("Please check it and try again.")
                exit(0)

            # If we are unable to connect to google.com, it means there is no internet connection
            # available
            else:
                print("Unable to connect to the internet.")
                print("Please check your internet connection and try again")
                exit(0)

        # Exception handling
        except:
            print("Some exception occured...please try again")
            exit(0)


# Now we will create functions to perform specific tasks
# This function will retrieve data content

def retrieve_data():
    # We will use the response generated above to get the data
    response_data = requests.get(url, headers = request_headers)

    # Get json data from response
    data = response_data.json()

    # Return json data
    return data

# This function will save retrieved data in json
def save_data_as_json(data, filename):
    # If user enters filename with json extension
    if filename.endswith('.json'):
        # Write data to json
        with open(filename, 'w+') as file:
            file.write(json.dumps(data))
    # In case .json is not included in filename, add it and then save the file
    else:
        # Write data to json 
        with open(filename + ".json", 'w+') as file:
            file.write(json.dumps(data))


def display_data(data):
    # Displaying basic information
    print('\n[INFO] Displaying basic information')
    # Creating prettytable object to create table of basic database information and add data to it
    data_table = PrettyTable()
    data_table.field_names = ["Object", "ID", "Created On", "Last Edited On"]
    data_table.add_row([data['object'], data['id'], data['created_time'], data['last_edited_time']])
    print(data_table)

    # Creating prettytable object to create table of Title information and add data to it
    print("\n[INFO] Displaying Title Information")
    title_table = PrettyTable()
    title_table.field_names = ['Plaintext', 'Type', 'Content', 'Link', 'href']
    title_table.add_row([data['title'][0]['plain_text'], data['title'][0]['type'], data['title'][0]['text']['content'], data['title'][0]['text']['link'], data['title'][0]['href']])
    print(title_table)

    # Creating prettytable object to create table of properties information and add data to it
    print("\n[INFO] Properties Information")
    all_properties = data['properties']
    properties_table = PrettyTable()
    properties_table.field_names = ["Name", 'Type']
    for property in all_properties:
        prop_data = data['properties'][property]
        if 'Meditation' in str(property):
            properties_table.add_row([property[2:] + '  ', prop_data['type']])
        else:
            properties_table.add_row([property.strip(), prop_data['type']])
    print(properties_table)


if __name__ == '__main__':

    # Variables for analyzing command line arguments
    isRead = False
    saveFilename = ''

    # Display ASCII art
    print(art.text2art("Notion API Python"))
    
    # First check for connectivity
    check_connectivity()

    # Help message 
    help_message = '''
    Usage: python main.py [OPTIONS]
    Options:
    -h | --help : To display this help message
    -r | --read : To read data from databse and display it on the screen (default setup)
    -o 'filename.json' | --output 'filename.json' : To save data as json file

    Ex:
    python main.py -r [Also reads data]
    python main.py -h [Displays help message]
    python main.py -o 'filename.json' [Saves retrieved data to json]
    '''

    # Checking if command line arguments are given or not
    try:
        if sys.argv[1]:
            pass
    except:
        print("[ERROR] No command line arguments found...please try again")
        print(help_message)
        exit(0)

    # Setting getopt
    try:
        arguments, values = getopt(sys.argv[1:], "hrt:o:", ["help", "read", "title", "output"])
    except GetoptError:
        print("[ERROR] Invalid command line arguments found...please try again")
        print(help_message)

    # Analyzing command line arguments
    for arg, value in arguments:
        if arg in ['-h', '--help']:
            print(help_message)
            exit(0)
        elif arg in ['-r', '--read']:
            isRead = True
            print("[INFO] Reading and displaying data from database")
        elif arg in ['-o', '--output']:
            saveFilename = value
            isRead = True
            if saveFilename.endswith('.json'):
                print("[INFO] Saving database output to {0}".format(value))
            else:
                print("[INFO] Saving database output to {0}.json".format(value))

    # Performing action
    if isRead:
        data = retrieve_data()
        display_data(data)
        if saveFilename != '':
            save_data_as_json(data, saveFilename)