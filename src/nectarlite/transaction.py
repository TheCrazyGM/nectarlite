"""Transaction class for creating and signing transactions."""

import json
from datetime import datetime, timedelta, timezone

from .amount import Amount
from .chain import HIVE_CHAIN_ID
from .crypto.ecdsa import sign
from .exceptions import TransactionError
from .types import Array, Bool, Int16, PointInTime, String, Uint16, Uint32, Varint

ops = {
    "vote": 0,
    "comment": 1,
    "transfer": 2,
    "comment_options": 19,
    "custom_json": 18,
}


class Operation:
    """Base class for all operations."""

    def __init__(self, op_name, params, api=None):
        self.op_name = op_name
        self.params = params
        self.api = api

    def to_dict(self):
        """Return the operation as a dictionary."""
        return [self.op_name, self.params]

    def __bytes__(self):
        """Return the binary representation of the operation."""
        op_id = ops.get(self.op_name)
        if op_id is None:
            raise TransactionError(f"Unknown operation: {self.op_name}")
        return bytes(Varint(op_id)) + self.serialize_params()

    def serialize_params(self):
        """Serialize the parameters of the operation."""
        raise NotImplementedError


class Transfer(Operation):
    """Transfer operation."""

    def __init__(self, to, amount, asset, memo="", frm=None, api=None):
        super().__init__(
            "transfer",
            {
                "from": frm,
                "to": to,
                "amount": amount,
                "asset": asset,
                "memo": memo,
            },
            api=api,
        )

    def serialize_params(self):
        return (
            bytes(String(self.params["from"]))
            + bytes(String(self.params["to"]))
            + bytes(Amount(self.params["amount"], self.params["asset"], api=self.api))
            + bytes(String(self.params["memo"]))
        )

    def to_dict(self):
        payload = self.params.copy()
        amount_value = payload.pop("amount")
        asset_symbol = payload.pop("asset")
        payload["amount"] = f"{amount_value} {asset_symbol}"
        return [self.op_name, payload]


class Vote(Operation):
    """Vote operation."""

    def __init__(self, voter, author, permlink, weight, api=None):
        super().__init__(
            "vote",
            {
                "voter": voter,
                "author": author,
                "permlink": permlink,
                "weight": weight,
            },
            api=api,
        )

    def serialize_params(self):
        return (
            bytes(String(self.params["voter"]))
            + bytes(String(self.params["author"]))
            + bytes(String(self.params["permlink"]))
            + bytes(Int16(self.params["weight"]))
        )


class CommentOperation(Operation):
    """Comment (a.k.a. post) operation."""

    def __init__(
        self,
        parent_author,
        parent_permlink,
        author,
        permlink,
        title,
        body,
        json_metadata,
        api=None,
    ):
        super().__init__(
            "comment",
            {
                "parent_author": parent_author,
                "parent_permlink": parent_permlink,
                "author": author,
                "permlink": permlink,
                "title": title,
                "body": body,
                "json_metadata": json_metadata,
            },
            api=api,
        )

    def serialize_params(self):
        return (
            bytes(String(self.params["parent_author"]))
            + bytes(String(self.params["parent_permlink"]))
            + bytes(String(self.params["author"]))
            + bytes(String(self.params["permlink"]))
            + bytes(String(self.params["title"]))
            + bytes(String(self.params["body"]))
            + bytes(String(self.params["json_metadata"]))
        )

    def to_dict(self):
        return [self.op_name, self.params.copy()]


class CommentOptionsOperation(Operation):
    """Comment options operation."""

    def __init__(
        self,
        author,
        permlink,
        max_accepted_payout,
        percent_hbd,
        allow_votes,
        allow_curation_rewards,
        extensions=None,
        api=None,
    ):
        super().__init__(
            "comment_options",
            {
                "author": author,
                "permlink": permlink,
                "max_accepted_payout": max_accepted_payout,
                "percent_hbd": percent_hbd,
                "allow_votes": allow_votes,
                "allow_curation_rewards": allow_curation_rewards,
                "extensions": extensions or [],
            },
            api=api,
        )

    def serialize_params(self):
        extensions = self.params["extensions"]
        serialized_extensions = []
        for ext in extensions:
            if hasattr(ext, "__bytes__"):
                serialized_extensions.append(ext)
            else:
                raise TransactionError(
                    "comment_options extensions must implement __bytes__()"
                )

        return (
            bytes(String(self.params["author"]))
            + bytes(String(self.params["permlink"]))
            + bytes(String(self.params["max_accepted_payout"]))
            + bytes(Uint16(self.params["percent_hbd"]))
            + bytes(Bool(self.params["allow_votes"]))
            + bytes(Bool(self.params["allow_curation_rewards"]))
            + bytes(Array(serialized_extensions))
        )

    def to_dict(self):
        return [self.op_name, self.params.copy()]


class CustomJson(Operation):
    """CustomJson operation."""

    def __init__(
        self, id, json_data, required_auths=[], required_posting_auths=[], api=None
    ):
        super().__init__(
            "custom_json",
            {
                "required_auths": required_auths,
                "required_posting_auths": required_posting_auths,
                "id": id,
                "json": json_data,
            },
            api=api,
        )

    def serialize_params(self):
        return (
            bytes(Array([String(auth) for auth in self.params["required_auths"]]))
            + bytes(
                Array([String(auth) for auth in self.params["required_posting_auths"]])
            )
            + bytes(String(self.params["id"]))
            + bytes(String(self.params["json"]))
        )


class Follow(Operation):
    """Follow operation for following, unfollowing, ignoring or unignoring an account."""

    def __init__(self, follower, following, what=["blog"], api=None):
        """Initialize a Follow operation.

        :param str follower: The account that is following.
        :param str following: The account to follow.
        :param list what: Action to perform ["blog"] for follow, [] for unfollow, ["ignore"] for ignore.
        :param Api api: An instance of the Api class.
        """
        self.follower = follower
        self.following = following
        self.what = what
        self.api = api

        # Create the JSON payload for the follow operation
        json_data = json.dumps(
            ["follow", {"follower": follower, "following": following, "what": what}]
        )

        # Create the underlying CustomJson operation
        self.custom_json = CustomJson(
            id="follow", json_data=json_data, required_posting_auths=[follower], api=api
        )

    def to_dict(self):
        """Return the operation as a dictionary."""
        return self.custom_json.to_dict()

    def __bytes__(self):
        """Return the binary representation of the operation."""
        return bytes(self.custom_json)


class Transaction:
    """Transaction class for creating and signing transactions."""

    def __init__(self, api=None, ref_block_num=None, ref_block_prefix=None):
        """Initialize the Transaction class.

        :param Api api: An instance of the Api class.
        :param int ref_block_num: The reference block number.
        :param int ref_block_prefix: The reference block prefix.
        """
        self.api = api
        self.ref_block_num = ref_block_num
        self.ref_block_prefix = ref_block_prefix
        self.ops = []
        self.signatures = []

    def append_op(self, op):
        """Append an operation to the transaction."""
        op.api = self.api
        self.ops.append(op)

    def sign(self, wif):
        """Sign the transaction with a private key in WIF format."""
        if not self.ref_block_num or not self.ref_block_prefix:
            if not self.api:
                raise TransactionError("API not configured to get block params.")
            self._set_block_params()

        tx_dict = self._construct_tx()
        tx_for_hex = dict(tx_dict)
        tx_for_hex.setdefault("signatures", [])

        if not self.api:
            raise TransactionError("API not configured to get transaction hex.")

        tx_hex = self.api.call("condenser_api", "get_transaction_hex", [tx_for_hex])
        if isinstance(tx_hex, dict):
            tx_hex = tx_hex.get("hex") or tx_hex.get("transaction_hex")
        if not isinstance(tx_hex, str):
            raise TransactionError("Unexpected response from get_transaction_hex")

        tx_hex = tx_hex.strip()

        if not tx_hex:
            raise TransactionError("Empty transaction hex returned")

        digest_hex = tx_hex[:-2] if len(tx_hex) > 2 else tx_hex

        message = bytes.fromhex(HIVE_CHAIN_ID + digest_hex)
        self.signatures.append(sign(message, wif))

    def broadcast(self):
        """Broadcast the transaction to the network."""
        if not self.api:
            raise TransactionError("API not configured to broadcast.")
        if not self.signatures:
            raise TransactionError("Transaction is not signed.")

        tx = self._construct_tx()
        tx["signatures"] = [s.hex() for s in self.signatures]
        try:
            response = self.api.call(
                "condenser_api", "broadcast_transaction_synchronous", [tx]
            )
        except Exception as exc:
            raise TransactionError(str(exc)) from exc
        return response

    def _set_block_params(self):
        """Get the reference block number and prefix from the blockchain."""
        props = self.api.call("condenser_api", "get_dynamic_global_properties", [])
        head_block_number = props["head_block_number"]
        self.ref_block_num = (head_block_number - 3) & 0xFFFF

        block_num = head_block_number - 2
        block_response = self.api.call(
            "block_api", "get_block", {"block_num": block_num}
        )
        block_data = (
            block_response.get("block")
            if isinstance(block_response, dict)
            else block_response
        )
        if not block_data or "previous" not in block_data:
            raise TransactionError("Unable to fetch reference block")

        previous_block_bytes = bytes.fromhex(block_data["previous"])
        self.ref_block_prefix = int.from_bytes(previous_block_bytes[4:8], "little")

        head_block_time = props["time"]
        expiration_dt = datetime.strptime(
            head_block_time, "%Y-%m-%dT%H:%M:%S"
        ) + timedelta(seconds=30)
        self.expiration_override = expiration_dt.strftime("%Y-%m-%dT%H:%M:%S")

    def _construct_tx(self):
        """Construct the transaction dictionary."""
        if hasattr(self, "expiration_override"):
            expiration = self.expiration_override
        else:
            expiration = (datetime.now(timezone.utc) + timedelta(minutes=5)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
        return {
            "ref_block_num": self.ref_block_num,
            "ref_block_prefix": self.ref_block_prefix,
            "expiration": expiration,
            "operations": [op.to_dict() for op in self.ops],
            "extensions": [],
        }

    def _serialize_tx(self):
        """Serialize the transaction to a hex string."""
        tx = self._construct_tx()
        return (
            bytes.fromhex(HIVE_CHAIN_ID)
            + bytes(Uint16(tx["ref_block_num"]))
            + bytes(Uint32(tx["ref_block_prefix"]))
            + bytes(PointInTime(tx["expiration"]))
            + bytes(Array(self.ops))
            + bytes(Array(tx["extensions"]))
        )
