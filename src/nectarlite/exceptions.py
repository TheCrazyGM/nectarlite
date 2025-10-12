"""Nectarlite exceptions."""


class NectarliteException(Exception):
    """Base exception for all nectarlite-related errors."""

    pass


class NodeError(NectarliteException):
    """Raised when a Hive node returns an error."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class MissingKeyError(NectarliteException):
    """Raised when a required key is not provided."""

    pass


class InvalidKeyFormatError(NectarliteException):
    """Raised when a key is not in the correct format."""

    pass


class TransactionError(NectarliteException):
    """Raised for errors related to transaction building and signing."""

    pass
