from user import User

class Statistics:

    userMap = {}

    def __init__(self, data):
        self.data = data
        self.buildUserMap(data)

    def buildUserMap(self, data):
        for i in range(0, len(data)):
            row = data[i]
            if row.userID in self.userMap:
                userData = self.userMap[row.userID]

                newTime = userData['time'] + (row.endTime - row.startTime)
                newEnergy = userData['energy'] + row.Energy
                newUserData = {'time' : newTime, 'energy' : newEnergy}
                self.userMap.update({row.userID : newUserData})
            else:
                userData = {'time' : row.endTime - row.startTime, 'energy' : row.Energy}
                self.userMap.update({row.userID : userData})

    def totalNumberOfUsers(self):
        return len(self.userMap)

    def totalEnergy(self):
        count = 0
        for key in self.userMap:
            count += self.userMap[key]['energy']
        return count

    def timePerUser(self):
        result = {}
        for key in self.userMap:
            user = User(key)
            userData = {'username' : user.getName(), 'totaltime' : self.userMap[key]['time']}

            result.update({key : userData})
        return result