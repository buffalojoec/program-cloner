from base64 import b64decode
from dataclasses import dataclass
from typing import Any, Generator, Iterable, Optional, Tuple

import itertools
import requests
import sys
import time

ELF_MAGIC = b"\x7fELF"

class RPCError(Exception):
    """
    JSON-RPC 2.0 error.
    https://www.jsonrpc.org/specification#error_object
    """
    def __init__(self, code: int, message: str = "", data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

    @staticmethod
    def from_json(obj: Optional[dict]) -> Optional["RPCError"]:
        if obj is None:
            return None
        return RPCError(
            code=obj["code"], message=obj.get("message"), data=obj.get("data")
        )


@dataclass
class RPCResponse:
    """
    JSON-RPC 2.0 result.
    https://www.jsonrpc.org/specification#response_object
    """
    id: int
    result: Optional[Any] = None
    error: Optional[RPCError] = None

    def is_error(self) -> bool:
        return self.error is not None

    def raise_for_result(self):
        if self.error is not None:
            raise self.error

    @staticmethod
    def from_json(obj: dict) -> "RPCResponse":
        return RPCResponse(
            id=obj["id"],
            result=obj.get("result"),
            error=RPCError.from_json(obj.get("error")),
        )


class RPCClient:
    """
    JSON-RPC 2.0 HTTP client
    """
    def __init__(self, url: str):
        self.session = requests.Session()
        self.counter = 0
        self.url = url

    def request(self, method: str, *params) -> Any:
        """
        Sends an RPC request and returns the result, or raises an error.
        """
        res = self.request_response(method, *params)
        res.raise_for_result()
        return res.result

    def request_response(self, method: str, *params) -> RPCResponse:
        """
        Sends an RPC request and returns the response object.
        """
        request = {
            "jsonrpc": "2.0",
            "id": self.nonce(),
            "method": method,
            "params": list(params),
        }
        res = self.session.post(self.url, json=request)
        res.raise_for_status()
        return RPCResponse.from_json(res.json())

    def nonce(self) -> int:
        """
        Increments the request ID nonce.
        """
        self.counter += 1
        return self.counter


class SolanaRPC(RPCClient):
    """
    Solana JSON-RPC Wrapper.
    https://solana.com/docs/rpc
    """
    def get_version(self) -> dict:
        return self.request("getVersion")
    
    def get_multiple_programs(
        self,
        pubkeys: Iterable[str],
        rate_limit_buffer,
        offset: int = 0,
    ) -> Generator[Tuple[str, bytes], None, None]:
        batch = 100
        pubkeys = iter(pubkeys) # Program Data keys
        while True:
            chunk = list(itertools.islice(pubkeys, batch))
            if len(chunk) == 0:
                break
            for (program_id, elf) in self._get_multiple_programs_batch(chunk, offset):
                if elf[:4] != ELF_MAGIC:
                    print(f"WARN: {program_id} is not a valid ELF", sys.stderr)
                yield (program_id, elf)
            time.sleep(rate_limit_buffer)

    def _get_multiple_programs_batch(
        self, pubkeys: Iterable[str], offset: int = 0
    ) -> Generator[Tuple[str, bytes], None, None]:
        data_slice = {"offset": offset, "length": 1 << 31}
        result = self.request("getMultipleAccounts", pubkeys, {"dataSlice": data_slice})
        for idx, item in enumerate(result["value"]):
            if item is None:
                print(f"WARN: {pubkeys[idx]} not found!", sys.stderr)
                continue
            data = b64decode(item["data"][0])
            yield (pubkeys[idx], data)
    
    def get_program_account_keys(
        self, pubkey: str, filters: list
    ) -> Generator[str, None, None]:
        opts = {
            "encoding": "base64",
            "dataSlice": {"offset": 0, "length": 0},
            "filters": filters,
        }
        accounts = self.request("getProgramAccounts", pubkey, opts)
        for account in accounts:
            yield account["pubkey"]
    
    def get_last_slot_for_address(self, address: str) -> int:
        res = self.request(
            "getSignaturesForAddress",
            address,
            {
                "commitment": "confirmed",
                "limit": 1
            }
        )
        print(res)
        if len(res) == 0:
            print("Slot: 0")
            return 0
        print(f"Slot: {res[0]['slot']}")
        return res[0]["slot"]