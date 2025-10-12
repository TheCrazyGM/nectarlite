from nectarlite import Account, Api

nodes = ["https://api.hive.blog", "https://api.openhive.network"]
api = Api(nodes)

account_name = "thecrazygm"
account = Account(account_name, api=api)
account.refresh()

print(f"Account Name: {account.name}")
print(f"Balance: {account['balance']}")
print(f"Vesting Shares: {account['vesting_shares']}")
for x in account:
    print(f"{x}: {account[x]}")
