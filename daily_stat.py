from datetime import datetime, timedelta
import sys
from zeep import Client
from zeep.wsse.username import UsernameToken
from statistics import Statistics
from slackNotification import SlackNotification

def makeStatisticsAPICall(client, startTime, endTime):
    sessionsSearchQuery = {
        'fromTimeStamp': startTime,
        'toTimeStamp': endTime,
    }
    data = client.service.getChargingSessionData(sessionsSearchQuery)
    return data

def main():

    startTime = datetime.now() - timedelta(hours=24)
    endTime = datetime.now()

    if len(sys.argv) < 3:
        print ("greendrive needs username(key) and password")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]

    wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
    client = Client(wsdl_url, wsse=UsernameToken(username, password))

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
        message = message + ("{} | {} \n".format(row['username'],human_readable))

    print("Completed ...")

    message = message + ("Have a good evening! Drive responsibly!")

    slack = SlackNotification(sys.argv[3], "#greendrive-hackday-2019")
    slack.sendMessage(message)

    print(message)

if __name__== '__main__':
    main()