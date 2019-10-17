""" 

"""
import sys
import time as t
from slackNotification import SlackNotification
import signal

from zeep import Client
from zeep.wsse.username import UsernameToken
from datetime import datetime, time

availableCount = 0
inUseCount = 0
slack = None
client = None

def makeStationStatuscall(client):
	# Get station data
	searchQuery = {
		'portDetails': True
	}

	stationData = client.service.getStationStatus(searchQuery)
	numStations = len(stationData.stationData)
	i = 0
	inuse = 0
	available = 0
	while i < numStations:
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


def duringWorkday():
	startHour = time(8, 0)
	endHour = time(18, 0)
	currentTime = datetime.now().time()
	if currentTime > startHour and currentTime < endHour:
		return True
	else:
		return False


def sig_handler(sig, frame):
	print("It's the end of the 'day'")
	return endWorkday()


def endWorkday():
	#invoke kates function
	slack.sendMessage("Have a good evening! Drive responsibly!")
	sys.exit(0)


def main():
	if len(sys.argv) < 4:
		print("greendrive needs username(key), password, and slack token")
		sys.exit(1)
	username = sys.argv[1]

	password = sys.argv[2]
	slack_token = sys.argv[3]
	global slack
	slack = SlackNotification(slack_token, "#greendrive-hackday-2019")

	slack.sendMessage("Good Morning! Charge responsibly!")

	wsdl_url = "https://webservices.chargepoint.com/cp_api_5.1.wsdl"
	global client
	client = Client(wsdl_url, wsse=UsernameToken(username, password))
	global inUseCount, availableCount

	while duringWorkday():
		signal.signal(signal.SIGINT, sig_handler)
		inuse, available = makeStationStatuscall(client)
		if inuse != inUseCount or available != availableCount:
			inUseCount = inuse
			availableCount = available
			if availableCount == 0:
				slack.sendMessage("Out of luck! All spots taken")
			elif availableCount != 4:
				slack.sendMessage("Time to charge up! {} free spots as of {}.".format(availableCount, datetime.now().strftime("%I:%M %p")))
			else:
				slack.sendMessage("No one is charging! Grab your spot!")
		t.sleep(60)

	endWorkday()


if __name__== '__main__':
	main()
