from nectarlite import Account, Api


def main():
    api = Api(["https://api.hive.blog", "https://api.syncad.com"])
    account = Account("your_account_name", api=api)
    tx = account.follow("target_account")
    print("Follow operation created. Sign and broadcast when ready.")
    return tx


if __name__ == "__main__":
    main()
