"""Example script showing how to retrieve account reputation, voting power, and RC information."""

from nectarlite import Account, Api


def main():
    api = Api(["https://api.hive.blog", "https://api.syncad.com"])
    account = Account("thecrazygm", api=api)

    print(f"Account: {account.name}")

    reputation = account.reputation
    print(f"Reputation: {reputation}")

    vp = account.voting_power
    print(f"Voting Power: {vp:.2f}%")

    rc_percent = account.rc
    if rc_percent is None:
        print("Resource Credits: unavailable")
    else:
        print(f"Resource Credits: {rc_percent:.2f}%")

    rc_details = account.rc_info
    if rc_details:
        print("RC details:")
        for key, value in rc_details.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
