"""Api class for making RPC calls to Hive nodes."""

import requests

from .exceptions import NodeError


class Api:
    """Api class for making RPC calls to Hive nodes."""

    def __init__(self, nodes, timeout=5):
        """Initialize the Api class.

        :param list nodes: A list of Hive node URLs or a single URL string.
        :param int timeout: The timeout for requests in seconds.
        """
        if isinstance(nodes, str):
            nodes = [nodes]
        elif not hasattr(nodes, "__iter__"):
            raise ValueError("nodes must be a string or iterable of URLs")

        self.nodes = list(nodes)
        self.timeout = timeout
        self._current_node_index = 0

    def _get_next_node(self):
        """Get the next available node."""
        self._current_node_index = (self._current_node_index + 1) % len(self.nodes)
        return self.nodes[self._current_node_index]

    def call(self, api, method, params=[]):
        """Make an RPC call to a Hive node.

        :param str api: The API to call (e.g., 'condenser_api').
        :param str method: The method to call (e.g., 'get_block').
        :param list params: The parameters for the method.
        """
        for _ in range(len(self.nodes)):
            node_url = self._get_next_node()
            payload = {
                "jsonrpc": "2.0",
                "method": f"{api}.{method}",
                "params": params,
                "id": 1,
            }
            try:
                response = requests.post(node_url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                if "error" in result:
                    raise NodeError(result["error"]["message"])
                return result["result"]
            except requests.exceptions.RequestException as e:
                print(f"Error calling {node_url}: {e}")
            except NodeError as e:
                print(f"Error calling {node_url}: {e}")

        raise NodeError("All nodes failed.")
