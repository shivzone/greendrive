class User:

    users = {
        '180173': 'Pivot1',
        '779203': 'Pivot2',
        '20446281': 'Pivot3',
        '3585081': 'Pivot4',
        '739319': 'Pivot5'
    }

    def __init__(self, id):
        self.id = id

    def getName(self):
        if self.id in User.users:
            return User.users[self.id]
        else:
            return "Undefined user " + self.id