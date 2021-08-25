# lagPortMember adminStatus lastTimeLinkChanged esmLinkStateChangeTime specificType
import os
import sys
import requests
import getpass
import ipaddress
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning


# Hide SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Enter OmniVista URL
ov_url = "localhost"


# Create request session
session = requests.Session() 


# Output information
output = ""


# Input data
input_data = ""


# Instance ID list
instance_id = []





# Get API Function
def getData():


	# POST login credentials into OV API
	try:


		# Get username and password
		username = input("Enter Username:")
		password = getpass.getpass(prompt = "Enter Password:")


		# Use Login API to login
		login = session.post(ov_url + 'api/login', json = {'userName': username, 'password': password}, verify=False)


		# Check if login was successful
		if login.json()['message'] == "Login failed":
			print("Incorrect Omnivista login credentials.")
			exit()



	except:
		print("Cannot connect to " + ov_url)
		exit()


	try:

		# Define cookie
		cookie = session.cookies.get_dict()
		device_api = session.get(ov_url + 'api/port/devices', cookies=cookie, verify=False)


		# Convert requests to JSON
		device_list = device_api.json()["response"]

	except:
		# Error! Cannot fetch API
		print("Cannot fetch device API.")
		exit()


	# Get all port information from device list
	for num in range(len(device_list)):

		# Append device
		instance_id.append(device_list[num]["instanceid"])


	# Get port data for all instance ID
	port_data = session.post(ov_url + 'api/port/ports', json = instance_id, verify=False)
	return port_data.json()



# Get LinkAgg info
def getLinkAgg(data):


	global output


	# Get port information



	# Output data
	for num in range(len(data['response'])):


		# Get Port info
		portInfo = data['response'][num]['portList']


		# Get Port Length
		port_length = len(portInfo)


		# Get all ports
		for port_num in range(port_length):


			# Output data only if specificType is LAG
			if portInfo[port_num]['portData']['specificType'] != "LAG":

				# Convert and get Last Uptime
				try:
					last_op = str(datetime.utcfromtimestamp(int(portInfo[port_num]['portData']['esmLinkStateChangeTime'])/1000).strftime("%m/%d/%Y %H:%M:%S")) + " GMT"
				except:
					last_op = "None"


				try:
					last_lnk = str(datetime.utcfromtimestamp(int(portInfo[port_num]['portData']['lastTimeLinkChanged'])/1000).strftime("%m/%d/%Y %H:%M:%S")) + " GMT"
				except:
					last_lnk = "None"


				# Format Data
				switch_data = """%s - %s - [ADMIN STATUS] %s - [PORT STATUS] %s - %s - %s - [OP CHG] %s - [LINK CHG] %s \n""" % (data['response'][num]['deviceName'], data['response'][num]['deviceIp'], portInfo[port_num]['portData']['adminStatus'], portInfo[port_num]['portData']['PortStatus'], portInfo[port_num]['portData']['portNumber'], portInfo[port_num]['portData']['lagPortMember'], last_op, last_lnk)
				
				# Output Data
				print(switch_data)
				output += switch_data


	return








# Arguments

# Search for IP Address data
#try: 

# Get script directory
directory = os.path.dirname(__file__)
# Get text file directory
filename = os.path.join(directory, 'regular_port_' + datetime.today().strftime("%m_%d_%Y") + '.txt')


# Log in to API
data = getData()


# If IP is valid, find information
getLinkAgg(data)


# Write to file
f = open(filename, "w")
f.write(output)
f.close()





