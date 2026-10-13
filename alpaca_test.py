"""Test the Alpaca paper-trading connection and buy 1 share of AAPL.

Usage:
    export APCA_API_KEY_ID=...
    export APCA_API_SECRET_KEY=...
    python alpaca_test.py            # check account + place order
    python alpaca_test.py --check    # check account only
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ.get("APCA_API_BASE_URL", "https://paper-api.alpaca.markets/v2")


def request(method, path, body=None):
    headers = {
        "APCA-API-KEY-ID": os.environ["APCA_API_KEY_ID"],
        "APCA-API-SECRET-KEY": os.environ["APCA_API_SECRET_KEY"],
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} failed: {e.code} {e.read().decode()}")


def main():
    account = request("GET", "/account")
    print(f"Connected. Account {account['account_number']} status={account['status']} "
          f"cash={account['cash']} buying_power={account['buying_power']}")

    clock = request("GET", "/clock")
    print(f"Market open: {clock['is_open']} (next open {clock['next_open']})")

    if "--check" in sys.argv:
        return

    order = request("POST", "/orders", {
        "symbol": "AAPL",
        "qty": "1",
        "side": "buy",
        "type": "market",
        "time_in_force": "day",
    })
    print(f"Order submitted: id={order['id']} status={order['status']}")
    if not clock["is_open"]:
        print("Market is closed; the order will fill when it next opens.")


if __name__ == "__main__":
    main()
