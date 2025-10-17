#!/usr/bin/env python

"""Demonstrate composing a comment + comment_options transaction."""

import json

from nectarlite import Api, Transaction
from nectarlite.transaction import CommentOperation, CommentOptionsOperation


def main():
    api = Api(["https://api.hive.blog"])

    tx = Transaction(api=api)

    comment = CommentOperation(
        parent_author="",
        parent_permlink="hive-12345",
        author="alice",
        permlink="hello-hive",
        title="Hello Hive",
        body="This is a sample post body from Nectarlite.",
        json_metadata=json.dumps(
            {"tags": ["hive", "nectarlite"], "app": "nectarlite/0.1"}
        ),
    )

    options = CommentOptionsOperation(
        author="alice",
        permlink="hello-hive",
        max_accepted_payout="1000.000 HBD",
        percent_hbd=10000,
        allow_votes=True,
        allow_curation_rewards=True,
    )

    tx.append_op(comment)
    tx.append_op(options)

    print("Constructed transaction operations:")
    for op_name, payload in tx._construct_tx()["operations"]:
        print(f"- {op_name}: {payload}")


if __name__ == "__main__":
    main()
