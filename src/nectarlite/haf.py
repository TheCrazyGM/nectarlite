# -*- coding: utf-8 -*-
import json
import logging
from typing import Any, Dict, Optional

import requests

log = logging.getLogger(__name__)


class HAF(object):
    """Hive Account Feed (HAF) API client for accessing Hive blockchain endpoints."""

    DEFAULT_APIS = ["https://api.hive.blog", "https://api.syncad.com"]

    def __init__(self, api: Optional[str] = None, timeout: Optional[float] = None):
        """
        Initialize the HAF client.

        Parameters:
            api (str, optional): Base API URL. If None, uses the first available default API.
            timeout (float, optional): Timeout for requests in seconds.
        """
        self.api = api or self.DEFAULT_APIS[0]
        self._timeout = float(timeout) if timeout else 30.0

        if not self.api.startswith(("http://", "https://")):
            raise ValueError(
                f"Invalid API URL: {self.api}. Must start with http:// or https://"
            )

        self.api = self.api.rstrip("/")

        log.debug(f"Initialized HAF client with API: {self.api}")

    def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Any:
        url = f"{self.api}/{endpoint}"

        headers = kwargs.pop("headers", {})
        headers.setdefault("accept", "application/json")
        headers.setdefault("User-Agent", "nectarlite/0.0.1")

        log.debug(f"Making {method} request to: {url}")

        try:
            timeout = kwargs.pop("timeout", self._timeout)
            response = requests.request(
                method, url, headers=headers, timeout=timeout, **kwargs
            )
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            log.error(f"Request failed for {url}: {e}")
            raise
        except json.JSONDecodeError as e:
            log.error(f"Invalid JSON response from {url}: {e}")
            raise ValueError(f"Invalid JSON response from API: {e}")

    def reputation(self, account: str) -> Optional[Dict[str, Any]]:
        if not account or not isinstance(account, str):
            raise ValueError("Account name must be a non-empty string")

        try:
            endpoint = f"reputation-api/accounts/{account}/reputation"
            response = self._make_request(endpoint)

            # Handle cases where the API returns a raw integer
            if isinstance(response, int):
                response = {"reputation": response, "account": account}

            log.debug(f"Retrieved reputation for account: {account}")
            return response

        except requests.RequestException as e:
            log.warning(f"Failed to retrieve reputation for account {account}: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error retrieving reputation for {account}: {e}")
            return None

    def get_account_balances(self, account: str) -> Optional[Dict[str, Any]]:
        if not account or not isinstance(account, str):
            raise ValueError("Account name must be a non-empty string")

        try:
            endpoint = f"balance-api/accounts/{account}/balances"
            response = self._make_request(endpoint)

            log.debug(f"Retrieved balances for account: {account}")
            return response

        except requests.RequestException as e:
            log.warning(f"Failed to retrieve balances for account {account}: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error retrieving balances for {account}: {e}")
            return None
