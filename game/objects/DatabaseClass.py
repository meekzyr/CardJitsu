import semidbm


class AccountDB:
    def __init__(self):
        self.dbm = semidbm.open('astron/account-bridge', 'c')

    def lookup(self, username, callback):
        if bytes(username, 'utf-8') not in list(self.dbm.keys()):
            # create a new account
            response = {
                'success': True,
                'username': username,
                'accountId': 0,
            }
            callback(response)
            return

        # account was found
        response = {
            'success': True,
            'username': username,
            'accountId': int(self.dbm[str(username)])
        }
        callback(response)

    def storeAccountID(self, username, accountId, callback):
        self.dbm[str(username)] = str(accountId)  # semidbm only allows strings.
        if getattr(self.dbm, 'sync', None):
            self.dbm.sync()
            callback(True)
        else:
            print('Unable to associate user %s with account %d!' % (username, accountId))
            callback(False)
