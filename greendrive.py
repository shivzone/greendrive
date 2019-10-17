""" 

"""
import os
import sys
import time
from slackNotification import SlackNotification

from zeep import Client
from zeep.wsse.username import UsernameToken
from datetime import datetime, timedelta
from pytz import timezone

availableCount = 0
inUseCount = 0

def makeUsageAPIcall(client, tStart, tEnd):
	"""
	Inputs:    tStart: Start time for API call in datetime format. 
						E.g. tStart=datetime(2018, 5, 30, 00, 00, 00)
	Note: the tEnd parameter will be set to the end of the day, e.g. datetime(2018, 5, 30, 23, 59, 59)
	"""
	#tEnd = tStart + timedelta(hours=23, minutes=59, seconds=59)
	usageSearchQuery = {
		'fromTimeStamp': tStart,
		'toTimeStamp': tEnd	}
	data = client.service.getChargingSessionData(usageSearchQuery)
	# print("Number of records in time-frame: ", len(data.ChargingSessionData))

	## Fill Sessions Table
	for d in data.ChargingSessionData:
		try:
			row_session = [int(d.sessionID), d.startTime.strftime('%Y-%m-%d %H:%M:%S'),
							d.endTime.strftime('%Y-%m-%d %H:%M:%S'), float(d.Energy),
							str(d.stationID), int(d.portNumber), int(d.userID)]
			print(row_session)
		except:
			pass


def makeStationStatuscall(client):
	## Get station data
	searchQuery = {}

	stationData = client.service.getStationStatus(searchQuery)
	numStations = len(stationData.stationData)
	i = 0
	inuse = 0
	available = 0
	while (i < numStations):
		numPorts = len(stationData.stationData[i].Port)
		j = 0
		while j < numPorts:
			if stationData.stationData[i].Port[j].Status == 'AVAILABLE':
				available = available + 1
			elif stationData.stationData[i].Port[j].Status == 'INUSE':
				inuse = inuse + 1
			j = j + 1
		i = i + 1

	print("Stations: InUse = {}, Available = {}".format(inuse, available))
	return inuse, available

#getPublicStationStatus shows status of usage

def main():
	utc = timezone('UTC')
	startTime = datetime(2019, 10, 17, 9, 00, 00).astimezone(utc)#- timedelta(hours=7, minutes=0, seconds=0)
	endTime = datetime(2019, 10, 19, 18, 00, 00).astimezone(utc)#- timedelta(hours=7, minutes=0, seconds=0)
        
	if len(sys.argv) < 3:
		print ("greendrive needs username(key) and password")
		sys.exit(1)
	username = sys.argv[1]
	password = sys.argv[2]
	slack_token = sys.argv[3]

	wsdl_url = "https://webservices.chargepoint.com/cp_api_5.1.wsdl"
	client = Client(wsdl_url, wsse=UsernameToken(username, password))
	slack = SlackNotification(slack_token, "#greendrive-hackday-2019")
	global inUseCount, availableCount

	while True:
		inuse, available = makeStationStatuscall(client)
		if inuse != inUseCount or available != availableCount:
			inUseCount = inuse
			availableCount = available
			if availableCount == 0:
				slack.sendMessage("There are no available stations at this time")
			else:
				slack.sendMessage("There are now {} available charging stations".format(availableCount))
		time.sleep(60)
	# if(return) {
	# 	notify on slack with whats available
	# }

	# makeUsageAPIcall(client, startTime, endTime)
	print("Completed ...")

	slack = SlackNotification(sys.argv[3], "#greendrive-hackday-2019")
	#slack.sendMessage("It works!")

if __name__== '__main__':
	main()
