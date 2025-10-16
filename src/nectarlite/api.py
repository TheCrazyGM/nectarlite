"""HTTP clients for interacting with Hive nodes."""

import logging
import threading
from typing import Iterable, List, Sequence

import httpx

from .exceptions import NodeError

log = logging.getLogger(__name__)


def _normalize_nodes(nodes: Sequence[str] | str) -> List[str]:
    if isinstance(nodes, str):
        return [nodes]
    if not hasattr(nodes, "__iter__"):
        raise ValueError("nodes must be a string or iterable of URLs")
    return list(nodes)


class Api:
    """Synchronous HTTP JSON-RPC client using ``httpx``."""

    def __init__(self, nodes: Sequence[str] | str, timeout: float = 5) -> None:
        self.nodes = _normalize_nodes(nodes)
        self.timeout = timeout
        self._current_node_index = -1
        self._lock = threading.Lock()
        self._client = httpx.Client(timeout=timeout)
        self.is_async = False

    def _get_next_node(self) -> str:
        with self._lock:
            self._current_node_index = (self._current_node_index + 1) % len(self.nodes)
            return self.nodes[self._current_node_index]

    def _build_payload(self, api: str, method: str, params: Iterable | None) -> dict:
        return {
            "jsonrpc": "2.0",
            "method": f"{api}.{method}",
            "params": list(params or []),
            "id": 1,
        }

    def call(self, api: str, method: str, params: Iterable | None = None):
        """Make an RPC call to a Hive node."""

        for _ in range(len(self.nodes)):
            node_url = self._get_next_node()
            payload = self._build_payload(api, method, params)
            try:
                response = self._client.post(node_url, json=payload)
                response.raise_for_status()
                result = response.json()
                if "error" in result:
                    raise NodeError(result["error"]["message"])
                return result.get("result")
            except httpx.HTTPError as exc:
                log.error("Error calling %s: %s", node_url, exc)
            except NodeError as exc:
                log.error("Node error from %s: %s", node_url, exc)

        raise NodeError("All nodes failed.")

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Api":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


class AsyncApi:
    """Async HTTP JSON-RPC client backed by ``httpx.AsyncClient``."""

    def __init__(self, nodes: Sequence[str] | str, timeout: float = 5) -> None:
        self.nodes = _normalize_nodes(nodes)
        self.timeout = timeout
        self._current_node_index = -1
        self._lock = threading.Lock()
        self._client = httpx.AsyncClient(timeout=timeout)
        self.is_async = True

    def _get_next_node(self) -> str:
        with self._lock:
            self._current_node_index = (self._current_node_index + 1) % len(self.nodes)
            return self.nodes[self._current_node_index]

    def _build_payload(self, api: str, method: str, params: Iterable | None) -> dict:
        return {
            "jsonrpc": "2.0",
            "method": f"{api}.{method}",
            "params": list(params or []),
            "id": 1,
        }

    async def call(self, api: str, method: str, params: Iterable | None = None):
        """Asynchronously make an RPC call to a Hive node."""

        for _ in range(len(self.nodes)):
            node_url = self._get_next_node()
            payload = self._build_payload(api, method, params)
            try:
                response = await self._client.post(node_url, json=payload)
                response.raise_for_status()
                result = response.json()
                if "error" in result:
                    raise NodeError(result["error"]["message"])
                return result.get("result")
            except httpx.HTTPError as exc:
                log.error("Error calling %s: %s", node_url, exc)
            except NodeError as exc:
                log.error("Node error from %s: %s", node_url, exc)

        raise NodeError("All nodes failed.")

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncApi":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()
