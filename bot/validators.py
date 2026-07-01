
"""
Input validation for CLI-supplied order parameters.
"""

import re
import logging

logger = logging.getLogger("trading_bot")

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}

# More flexible pattern for USDT-M futures symbols
SYMBOL_PATTERN = re.compile(r"^[A-Za-z0-9]+USDT$")


class ValidationError(Exception):
    """Raised when user-supplied order parameters fail validation."""


def validate_symbol(symbol: str) -> str:
    symbol = (symbol or "").strip().upper()
    if not symbol:
        raise ValidationError("Symbol is required (e.g. BTCUSDT).")
    
    # Check if it ends with USDT
    if not symbol.endswith("USDT"):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Must end with USDT, e.g. BTCUSDT."
        )
    
    # Check if it contains only valid characters
    if not re.match(r"^[A-Z0-9]+USDT$", symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Use only letters and numbers, e.g. BTCUSDT."
        )
    
    logger.debug(f"Symbol validation passed: {symbol}")
    return symbol


def validate_side(side: str) -> str:
    side = (side or "").strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = (order_type or "").strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    
    # Check minimum quantity for BTCUSDT (0.001)
    if quantity < 0.001:
        logger.warning(f"Quantity {quantity} is very small. Minimum for BTCUSDT is 0.001.")
    
    return quantity


def validate_price(price, order_type: str, field_name: str = "price"):
    """Price is required for LIMIT and STOP_LIMIT orders; ignored for MARKET."""
    if order_type == "MARKET":
        return None
    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} is required and must be a number for {order_type} orders."
        )
    if price <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")
    return price


def validate_stop_price(stop_price, order_type: str):
    """stop_price is required only for STOP_LIMIT orders."""
    if order_type != "STOP_LIMIT":
        return None
    return validate_price(stop_price, "STOP_LIMIT", field_name="stop_price")


def validate_order_params(symbol, side, order_type, quantity, price=None, stop_price=None):
    """Validate a full order request at once; returns a normalized dict."""
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    stop_price = validate_stop_price(stop_price, order_type)

    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "stop_price": stop_price,
    }