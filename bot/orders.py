"""
Order placement logic: ties validated CLI input to the Binance client,
handles exceptions, and shapes a consistent result object for the CLI
layer to print.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException
from requests.exceptions import ConnectionError, Timeout, RequestException

from bot.client import BinanceFuturesTestnetClient
from bot.validators import ValidationError, validate_order_params

logger = logging.getLogger("trading_bot")


@dataclass
class OrderResult:
    success: bool
    request: dict
    response: Optional[dict] = None
    error: Optional[str] = None

    def summary(self) -> str:
        lines = ["--- Order Request Summary ---"]
        for k, v in self.request.items():
            if v is not None:
                lines.append(f"  {k}: {v}")

        if self.success and self.response:
            lines.append("--- Order Response ---")
            lines.append(f"  orderId:     {self.response.get('orderId')}")
            lines.append(f"  status:      {self.response.get('status')}")
            lines.append(f"  executedQty: {self.response.get('executedQty')}")
            avg_price = self.response.get("avgPrice")
            if avg_price is not None:
                lines.append(f"  avgPrice:    {avg_price}")
            lines.append("--- RESULT: SUCCESS ---")
        else:
            lines.append("--- Order Response ---")
            lines.append(f"  error: {self.error}")
            lines.append("--- RESULT: FAILED ---")

        return "\n".join(lines)


def place_order(
    client: BinanceFuturesTestnetClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity,
    price=None,
    stop_price=None,
) -> OrderResult:
    """
    Validate input, place the order via the Binance client, and return
    a normalized OrderResult. All exceptions are caught here so the CLI
    layer only ever needs to check `result.success`.
    """
    try:
        params = validate_order_params(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValidationError as exc:
        logger.error("Input validation failed: %s", exc)
        return OrderResult(success=False, request=locals().get("params", {
            "symbol": symbol, "side": side, "order_type": order_type,
            "quantity": quantity, "price": price, "stop_price": stop_price,
        }), error=f"Validation error: {exc}")

    request_summary = {
        "symbol": params["symbol"],
        "side": params["side"],
        "order_type": params["order_type"],
        "quantity": params["quantity"],
        "price": params["price"],
        "stop_price": params["stop_price"],
    }

    try:
        response = client.place_order(
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["order_type"],
            quantity=params["quantity"],
            price=params["price"],
            stop_price=params["stop_price"],
        )
        return OrderResult(success=True, request=request_summary, response=response)

    except (BinanceAPIException, BinanceOrderException) as exc:
        logger.error("Binance API rejected the order: %s", exc)
        return OrderResult(success=False, request=request_summary, error=f"API error: {exc}")

    except BinanceRequestException as exc:
        logger.error("Malformed request sent to Binance: %s", exc)
        return OrderResult(success=False, request=request_summary, error=f"Request error: {exc}")

    except (ConnectionError, Timeout) as exc:
        logger.error("Network failure while contacting Binance: %s", exc)
        return OrderResult(success=False, request=request_summary, error=f"Network error: {exc}")

    except RequestException as exc:
        logger.error("Unexpected HTTP error: %s", exc)
        return OrderResult(success=False, request=request_summary, error=f"HTTP error: {exc}")

    except Exception as exc:  # noqa: BLE001 - last-resort safety net, logged with full context
        logger.exception("Unexpected error while placing order")
        return OrderResult(success=False, request=request_summary, error=f"Unexpected error: {exc}")
