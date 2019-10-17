""" 

"""
import os
import sys
from slackNotification import SlackNotification

from zeep import Client
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta

def makeUsageAPIcall(client, tStart, tEnd):
	"""
	Inputs:    tStart: Start time for API call in datetime format. 
						E.g. tStart=datetime(2018, 5, 30, 00, 00, 00)
	Note: the tEnd parameter will be set to the end of the day, e.g. datetime(2018, 5, 30, 23, 59, 59)
	"""
	print("Making usage API query..")
	#tEnd = tStart + timedelta(hours=23, minutes=59, seconds=59)
	usageSearchQuery = {
		'fromTimeStamp': tStart,
		'toTimeStamp': tEnd,
	}
	data = client.service.getChargingSessionData(usageSearchQuery)
	# print("Number of records in time-frame: ", len(data.ChargingSessionData))

	## Fill Sessions Table
	for d in data.ChargingSessionData:
		## enclose in try-except to avoid TypeError: int() argument must be a string or a number, not 'NoneType'
		## when userID is None, and other errors
		try:
			row_session = [int(d.sessionID), d.startTime.strftime('%Y-%m-%d %H:%M:%S'), 
							d.endTime.strftime('%Y-%m-%d %H:%M:%S'), float(d.Energy), 
							str(d.stationID), int(d.portNumber), int(d.userID)]
			print(row_session)
		except:
			pass


def makeStationAPIcall(client):
	print("Making station API query..")
	## Get station data
	searchQuery = {}
	stationData = client.service.getStations(searchQuery)
	numStations = len(stationData.stationData)
	print(numStations)

	print(stationData)

	## Fill Pricing Table Rows - assumes only one pricing model exists currently
	#price = stationData.stationData[0].Pricing[0]
        #print price

def main():
	startTime = datetime(2019, 10, 16, 9, 00, 00) - timedelta(hours=7, minutes=0, seconds=0)
	endTime = datetime(2019, 10, 17, 18, 00, 00) - timedelta(hours=7, minutes=0, seconds=0)
        
	if len(sys.argv) < 3:
		print ("greendrive needs username(key) and password")
		sys.exit(1)
	username = sys.argv[1]
	password = sys.argv[2]

	wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
	client = Client(wsdl_url, wsse=UsernameToken(username, password))

	#makeStationAPIcall(client) ## can make some check: if len(getStations)

	makeUsageAPIcall(client, startTime, endTime)
	print("Completed ...")

	slack = SlackNotification(sys.argv[3], "#greendrive-hackday-2019")
	slack.sendMessage("It works!")

if __name__== '__main__':
	main()
