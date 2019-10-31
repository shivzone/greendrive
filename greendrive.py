"""

"""
import sys
import time as t
from slackNotification import SlackNotification
import signal

from zeep import Client
from zeep.wsse.username import UsernameToken
from datetime import datetime, time, timedelta
from statistics import Statistics

availableCount = 0
inUseCount = 0
slack = None
client = None
MAX_RETRIES = 3
startHour = time(8, 0)
endHour = time(18, 0)
debug = False

def makeStationStatuscall(client):
	# Get station data
	searchQuery = {
		'portDetails': True
	}
	stationData = {}
	retries = MAX_RETRIES
	while retries > 0:
		try:
			stationData = client.service.getStationStatus(searchQuery)
			break
		except Exception as ex:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			message = template.format(type(ex).__name__, ex.args)
			print(message)
			retries -= 1
	if retries == 0:
		print("Error contacting chargepoint...exiting")
		sys.exit(1)

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
	global startHour
	global endHour
	currentTime = datetime.now().time()
	if currentTime > startHour and currentTime < endHour:
		return True
	else:
		return False



def makeStatisticsAPICall(client, startTime, endTime):
	sessionsSearchQuery = {
		'fromTimeStamp': startTime,
		'toTimeStamp': endTime,
	}
	data = client.service.getChargingSessionData(sessionsSearchQuery)
	return data


def endWorkday():

	startTime = datetime.now() - timedelta(hours=10)
	endTime = datetime.now()

	print("Pulling on statistics...")
	result = makeStatisticsAPICall(client, startTime, endTime)
	if result.responseCode != '100':
		print ("Can not fetch statistics data for given period of time")
		sys.exit(1)

	data = result.ChargingSessionData

	stat = Statistics(data)

	message = ""

	message = message + ("Total number of users charged today: {} \n".format(stat.totalNumberOfUsers()))
	message = message + ("Total Energy: {} kWh \n".format(round(stat.totalEnergy(), 2)))

	message = message + ("Charging time per user:\n")
	timePerUser = stat.timePerUser()

	for key in timePerUser:
		row = timePerUser[str(key)]
		time = row['totaltime']

		separated_time = str(time).split(':')
		human_readable = separated_time[0] + " hrs " + separated_time[1] + " minutes"
		message = message + ("{}  |  {} \n".format(row['username'],human_readable))

	print("Completed ...")

	message = message + ("Have a good evening! Drive responsibly!")

	global slack
	slack.sendMessage(message)

	print(message)
	sys.exit(0)


def sig_handler(sig, frame):
	print("It's the end of the 'day'")
	return endWorkday()


def main():
	if len(sys.argv) < 4:
		print("greendrive needs username(key), password, and slack token")
		sys.exit(1)
	username = sys.argv[1]
	password = sys.argv[2]
	slack_token = sys.argv[3]
	global debug
	if len(sys.argv) == 5 and sys.argv[4] == '--debug':
		debug = True

	global slack
	slack = SlackNotification(slack_token, "#greendrive-hackday-2019", debug)

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
		t.sleep(120)

	endWorkday()


if __name__== '__main__':
	main()
