"""Convenience helpers for common read-only Hive RPC calls."""

import logging
from typing import Any, Dict, Iterable, List, Optional

from .api import Api
from .exceptions import NodeError


log = logging.getLogger(__name__)


class _LazyResource:
    """Base helper that lazily fetches JSON data on attribute access."""

    def __init__(self, api: Api):
        self.api = api
        self._data: Any = None

    def _fetch(self) -> Any:  # pragma: no cover - overridden in subclasses
        raise NotImplementedError

    def refresh(self) -> "_LazyResource":
        log.debug("Refreshing resource %s.", self.__class__.__name__)
        self._data = self._fetch()
        return self

    def _ensure(self) -> Any:
        if self._data is None:
            self.refresh()
        return self._data

    def as_dict(self) -> Dict[str, Any]:
        data = self._ensure()
        if isinstance(data, dict):
            return dict(data)
        raise TypeError("Resource payload is not a mapping")

    def __getattr__(self, item: str) -> Any:
        if item in {"api", "_data"}:
            return super().__getattribute__(item)
        data = self._ensure()
        if isinstance(data, dict) and item in data:
            return data[item]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{item}'")

    def __getitem__(self, item: str) -> Any:
        data = self._ensure()
        if isinstance(data, dict):
            return data[item]
        raise TypeError("Resource payload does not support indexing")


class DynamicGlobalProperties(_LazyResource):
    """Wrapper for ``condenser_api.get_dynamic_global_properties``."""

    def _fetch(self) -> Dict[str, Any]:
        log.debug("Fetching dynamic global properties.")
        try:
            return self.api.call("condenser_api", "get_dynamic_global_properties", [])
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            log.error("Failed to fetch dynamic global properties: %s", exc)
            raise NodeError(str(exc)) from exc


class ChainProperties(_LazyResource):
    """Wrapper for ``condenser_api.get_chain_properties``."""

    def _fetch(self) -> Dict[str, Any]:
        log.debug("Fetching chain properties.")
        try:
            return self.api.call("condenser_api", "get_chain_properties", [])
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            log.error("Failed to fetch chain properties: %s", exc)
            raise NodeError(str(exc)) from exc


class WitnessSchedule(_LazyResource):
    """Wrapper for ``condenser_api.get_witness_schedule``."""

    def _fetch(self) -> Dict[str, Any]:
        log.debug("Fetching witness schedule.")
        try:
            return self.api.call("condenser_api", "get_witness_schedule", [])
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            log.error("Failed to fetch witness schedule: %s", exc)
            raise NodeError(str(exc)) from exc


class FeedHistory(_LazyResource):
    """Wrapper for ``condenser_api.get_feed_history``."""

    def _fetch(self) -> Dict[str, Any]:
        log.debug("Fetching feed history.")
        try:
            return self.api.call("condenser_api", "get_feed_history", [])
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            log.error("Failed to fetch feed history: %s", exc)
            raise NodeError(str(exc)) from exc


class RewardFunds(_LazyResource):
    """Wrapper for ``database_api.get_reward_funds``."""

    _FALLBACK_FUNDS = ("post", "comment")

    def _fetch(self) -> List[Dict[str, Any]]:
        log.debug("Fetching reward funds information.")
        funds = self._fetch_database_reward_funds()
        if funds:
            return funds
        return self._fetch_condenser_reward_funds()

    def _fetch_database_reward_funds(self) -> List[Dict[str, Any]]:
        log.debug("Fetching reward funds via database_api.")
        try:
            response = self.api.call("database_api", "get_reward_funds", {})
        except NodeError:
            return []

        if isinstance(response, dict):
            funds = response.get("funds")
            if isinstance(funds, list):
                return funds
            return []
        if isinstance(response, list):
            return response
        return []

    def _fetch_condenser_reward_funds(self) -> List[Dict[str, Any]]:
        log.debug("Fetching reward funds via condenser fallback.")
        results: List[Dict[str, Any]] = []
        for name in self._FALLBACK_FUNDS:
            try:
                response = self.api.call("condenser_api", "get_reward_fund", [name])
            except NodeError:
                # condenser endpoint unavailable across nodes
                log.warning(
                    "Condenser reward fund endpoint unavailable while fetching '%s'.",
                    name,
                )
                return results
            except Exception:
                log.debug("Skipping reward fund '%s' due to unexpected response.", name)
                continue

            normalized = self._normalize_fund_response(response, name)
            if normalized:
                results.append(normalized)
        return results

    @staticmethod
    def _normalize_fund_response(response: Any, name: str) -> Optional[Dict[str, Any]]:
        if isinstance(response, dict):
            fund = dict(response)
            fund.setdefault("name", name)
            return fund
        if isinstance(response, list):
            # Some nodes may return [fund_dict]
            if response and isinstance(response[0], dict):
                fund = dict(response[0])
                fund.setdefault("name", name)
                return fund
        if isinstance(response, str):
            return {"name": name, "reward_balance": response}
        return None

    def _ensure(self) -> List[Dict[str, Any]]:
        if self._data is None:
            self.refresh()
        return self._data

    def as_list(self) -> List[Dict[str, Any]]:
        return list(self._ensure())

    def find(self, name: str) -> Optional[Dict[str, Any]]:
        for fund in self._ensure():
            if isinstance(fund, dict) and fund.get("name") == name:
                return fund
        return None


class MedianHistoryPrice(_LazyResource):
    """Wrapper for ``condenser_api.get_current_median_history_price``."""

    def _fetch(self) -> Dict[str, Any]:
        try:
            return self.api.call(
                "condenser_api", "get_current_median_history_price", []
            )
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            raise NodeError(str(exc)) from exc


def get_block(api: Api, block_num: int) -> Optional[Dict[str, Any]]:
    """Return the block payload for ``block_num`` using ``block_api.get_block``."""

    log.debug("Fetching block %s.", block_num)
    try:
        response = api.call("block_api", "get_block", {"block_num": block_num})
    except Exception as exc:  # noqa: BLE001 - surface as NodeError
        if isinstance(exc, NodeError):
            raise
        log.error("Failed to fetch block %s: %s", block_num, exc)
        raise NodeError(str(exc)) from exc
    if isinstance(response, dict):
        return response.get("block") or response.get("result")
    return None


def get_ops_in_block(
    api: Api,
    block_num: int,
    virtual_only: bool = False,
) -> List[Any]:
    """Return operations for a block via ``condenser_api.get_ops_in_block``."""

    log.debug("Fetching ops in block %s (virtual_only=%s).", block_num, virtual_only)
    try:
        response = api.call(
            "condenser_api",
            "get_ops_in_block",
            [block_num, virtual_only],
        )
    except Exception as exc:  # noqa: BLE001 - surface as NodeError
        if isinstance(exc, NodeError):
            raise
        log.error("Failed to fetch ops for block %s: %s", block_num, exc)
        raise NodeError(str(exc)) from exc
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        return response.get("ops", [])
    return []


def get_account_history(
    api: Api,
    account: str,
    start: int = -1,
    limit: int = 100,
) -> List[Any]:
    """Return account history using ``condenser_api.get_account_history``."""

    log.debug(
        "Fetching account history for '%s' starting at %s (limit=%s).",
        account,
        start,
        limit,
    )
    try:
        response = api.call(
            "condenser_api", "get_account_history", [account, start, limit]
        )
    except Exception as exc:  # noqa: BLE001 - surface as NodeError
        if isinstance(exc, NodeError):
            raise
        log.error("Failed to fetch account history for '%s': %s", account, exc)
        raise NodeError(str(exc)) from exc
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        return response.get("history", [])
    return []


def get_rc_accounts(api: Api, accounts: Iterable[str]) -> List[Dict[str, Any]]:
    """Return RC metrics for the provided ``accounts`` using ``rc_api.find_rc_accounts``."""

    account_list = list(accounts)
    log.debug("Fetching RC accounts for %s.", account_list)
    try:
        response = api.call("rc_api", "find_rc_accounts", {"accounts": account_list})
    except Exception as exc:  # noqa: BLE001 - surface as NodeError
        if isinstance(exc, NodeError):
            raise
        log.error("Failed to fetch RC accounts: %s", exc)
        raise NodeError(str(exc)) from exc
    if isinstance(response, dict):
        return response.get("rc_accounts") or response.get("result") or []
    if isinstance(response, list):
        return response
    return []


def get_market_ticker(api: Api) -> Dict[str, Any]:
    """Return the market ticker via ``market_history_api.get_ticker``."""

    log.debug("Fetching market ticker.")
    try:
        response = api.call("market_history_api", "get_ticker", {})
    except NodeError:
        log.warning("Failed to fetch market ticker due to node error.")
        return {}
    return response or {}


def get_market_volume(api: Api) -> Dict[str, Any]:
    """Return 24h volume via ``market_history_api.get_volume""."""

    log.debug("Fetching market volume.")
    try:
        response = api.call("market_history_api", "get_volume", {})
    except NodeError:
        log.warning("Failed to fetch market volume due to node error.")
        return {}
    return response or {}


def get_ranked_posts(
    api: Api,
    sort: str = "trending",
    tag: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Fetch ranked posts using ``bridge.get_ranked_posts``."""

    payload = {"sort": sort, "limit": limit}
    if tag:
        payload["tag"] = tag
    log.debug("Fetching ranked posts with payload %s.", payload)
    try:
        response = api.call("bridge", "get_ranked_posts", payload)
    except Exception as exc:  # noqa: BLE001 - surface as NodeError
        if isinstance(exc, NodeError):
            raise
        log.error("Failed to fetch ranked posts: %s", exc)
        raise NodeError(str(exc)) from exc
    if isinstance(response, dict):
        return response.get("result") or response.get("posts") or []
    if isinstance(response, list):
        return response
    return []


__all__ = [
    "DynamicGlobalProperties",
    "ChainProperties",
    "WitnessSchedule",
    "FeedHistory",
    "RewardFunds",
    "MedianHistoryPrice",
    "get_block",
    "get_ops_in_block",
    "get_account_history",
    "get_rc_accounts",
    "get_market_ticker",
    "get_market_volume",
    "get_ranked_posts",
]
