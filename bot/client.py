"""
Thin wrapper around python-binance's Client, scoped to USDT-M Futures
Testnet. Isolating this here means orders.py / cli.py never talk to the
Binance SDK directly, which keeps the API layer swappable and testable.
"""

import logging
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

logger = logging.getLogger("trading_bot")

FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceFuturesTestnetClient:
    """Wraps python-binance's Client, pinned to the Futures Testnet endpoint."""

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required.")

        # python-binance's `testnet=True` flag points both spot and futures
        # REST calls at the respective testnet hosts. We additionally set
        # FUTURES_URL explicitly so the base URL matches the task spec even
        # if the library's default changes in a future version.
        self.client = Client(api_key, api_secret, testnet=True)
        self.client.FUTURES_URL = FUTURES_TESTNET_BASE_URL + "/fapi"

        logger.debug("Initialized Binance Futures Testnet client (base_url=%s)", FUTURES_TESTNET_BASE_URL)

    def ping(self) -> bool:
        """Basic connectivity/auth check against the futures testnet."""
        try:
            self.client.futures_ping()
            account = self.client.futures_account()
            logger.debug("Connectivity check OK. Account can_trade=%s", account.get("canTrade"))
            return True
        except (BinanceAPIException, BinanceRequestException) as exc:
            logger.error("Connectivity/auth check failed: %s", exc)
            return False

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> dict:
        """
        Place an order on USDT-M Futures Testnet.

        Raises BinanceAPIException / BinanceOrderException / BinanceRequestException
        on failure; callers (orders.py) are responsible for catching and logging.
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT" if order_type == "STOP_LIMIT" else order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force
        elif order_type == "STOP_LIMIT":
            # Binance futures stop-limit uses type=STOP with price + stopPrice
            params["type"] = "STOP"
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = time_in_force

        logger.info("Sending order request: %s", params)
        logger.debug("Raw request payload: %s", params)

        response = self.client.futures_create_order(**params)

        logger.info(
            "Order response: orderId=%s status=%s executedQty=%s avgPrice=%s",
            response.get("orderId"),
            response.get("status"),
            response.get("executedQty"),
            response.get("avgPrice"),
        )
        logger.debug("Raw response payload: %s", response)

        return response

    def get_order_status(self, symbol: str, order_id: int) -> dict:
        """Fetch the latest status of a previously placed order."""
        logger.debug("Querying order status: symbol=%s order_id=%s", symbol, order_id)
        response = self.client.futures_get_order(symbol=symbol, orderId=order_id)
        logger.debug("Order status response: %s", response)
        return response
