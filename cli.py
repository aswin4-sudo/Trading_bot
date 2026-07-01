#!/usr/bin/env python3
"""
CLI entry point for the Simplified Trading Bot.

Examples
--------
Market order:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

Limit order:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000

Stop-limit order:
    python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.01 \
        --price 64000 --stop-price 64500

Auto-trading:
    python cli.py --auto --symbol BTCUSDT --strategy sma

Interactive Menu:
    python cli.py --interactive

Web UI:
    python cli.py --web
"""

import argparse
import os
import sys
import time
import logging
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Also try to load with explicit path (just in case)
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Try both naming conventions (API_KEY vs BINANCE_API_KEY)
if os.getenv('API_KEY') and not os.getenv('BINANCE_API_KEY'):
    os.environ['BINANCE_API_KEY'] = os.getenv('API_KEY')
if os.getenv('API_SECRET') and not os.getenv('BINANCE_API_SECRET'):
    os.environ['BINANCE_API_SECRET'] = os.getenv('API_SECRET')

from bot.client import BinanceFuturesTestnetClient
from bot.logging_config import setup_logging
from bot.orders import place_order


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Place MARKET / LIMIT / STOP_LIMIT orders on Binance USDT-M Futures Testnet.",
    )
    
    # Required order parameters
    parser.add_argument("--symbol", required=False, default="BTCUSDT", help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=False, choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    parser.add_argument(
        "--type", dest="order_type", required=False,
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=False, help="Order quantity")
    parser.add_argument("--price", default=None, help="Limit price (required for LIMIT / STOP_LIMIT)")
    parser.add_argument("--stop-price", dest="stop_price", default=None, help="Stop trigger price (required for STOP_LIMIT)")
    
    # API credentials
    parser.add_argument("--api-key", default=os.environ.get("BINANCE_API_KEY"), help="Binance Testnet API key (or set BINANCE_API_KEY)")
    parser.add_argument("--api-secret", default=os.environ.get("BINANCE_API_SECRET"), help="Binance Testnet API secret (or set BINANCE_API_SECRET)")
    parser.add_argument("--log-file", default=None, help="Override path to the log file")
    
    # Interactive menu
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive menu mode"
    )
    
    #  WEB UI ARGUMENTS 
    parser.add_argument(
        "--web",
        action="store_true",
        help="Start web UI"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for web UI (default: 5000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for web UI (default: 127.0.0.1)"
    )
    
    # Auto-trading arguments
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run in automated mode with strategy"
    )
    parser.add_argument(
        "--strategy",
        choices=["sma", "rsi", "macd", "drop"],
        default="sma",
        help="Strategy to use in auto mode"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds for auto mode (default: 60)"
    )
    parser.add_argument(
        "--amount",
        type=float,
        default=0.001,
        help="Quantity to trade in auto mode (default: 0.001)"
    )
    
    return parser


def run_auto_trading(client, symbol, strategy_name, interval=60, amount=0.001):
    """
    Run automated trading with strategy.
    
    Args:
        client: Binance client
        symbol: Trading pair (e.g., BTCUSDT)
        strategy_name: Strategy to use ('sma', 'rsi', 'macd', 'drop')
        interval: Check interval in seconds
        amount: Quantity to trade
    """
    logger = logging.getLogger("trading_bot")
    
    logger.info(f"Starting automated trading for {symbol}")
    print(f"\n🤖 Auto-trading started for {symbol}")
    print(f"📊 Strategy: {strategy_name.upper()}")
    print(f"⏱️  Check interval: {interval} seconds")
    print(f"💰 Trade amount: {amount}")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Strategy loop
        while True:
            try:
                print(f"\n⏰ Checking at {time.strftime('%H:%M:%S')}")
                
                # Get current price
                ticker = client.client.futures_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                print(f"💰 Current {symbol} price: ${current_price:,.2f}")
                
                # Execute strategy based on selection
                if strategy_name == "drop":
                    signal = check_price_drop_strategy(client, symbol)
                elif strategy_name == "sma":
                    signal = check_sma_strategy(client, symbol)
                elif strategy_name == "rsi":
                    signal = check_rsi_strategy(client, symbol)
                elif strategy_name == "macd":
                    signal = check_macd_strategy(client, symbol)
                else:
                    signal = "HOLD"
                
                # Execute trade if signal is BUY or SELL
                if signal == "BUY":
                    print(f"📈 SIGNAL: BUY at ${current_price:,.2f}")
                    result = place_order(
                        client=client,
                        symbol=symbol,
                        side="BUY",
                        order_type="MARKET",
                        quantity=amount
                    )
                    print(result.summary())
                    
                elif signal == "SELL":
                    print(f"📉 SIGNAL: SELL at ${current_price:,.2f}")
                    result = place_order(
                        client=client,
                        symbol=symbol,
                        side="SELL",
                        order_type="MARKET",
                        quantity=amount
                    )
                    print(result.summary())
                    
                else:
                    print(f"⏸️  SIGNAL: HOLD - No action taken")
                
                # Wait before next check
                time.sleep(interval)
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Strategy error: {e}")
                print(f"❌ Error: {e}")
                time.sleep(interval)
                
    except KeyboardInterrupt:
        logger.info("Auto-trading stopped by user")
        print("\n🛑 Auto-trading stopped by user")
        print("📊 Summary: Check logs/trading_bot.log for details")


def check_price_drop_strategy(client, symbol, drop_threshold=0.0005):
    """
    Strategy: Buy when price drops by threshold percentage.
    
    Args:
        client: Binance client
        symbol: Trading pair
        drop_threshold: Percentage drop to trigger buy (0.0005 = 0.05%)
    
    Returns:
        "BUY" if price dropped, "HOLD" otherwise
    """
    try:
        # Get last 10 minutes of prices
        candles = client.client.futures_klines(
            symbol=symbol,
            interval="1m",
            limit=10
        )
        
        prices = [float(c[4]) for c in candles]  # Closing prices
        current_price = prices[-1]
        max_price = max(prices)
        
        if max_price > 0:
            drop = (max_price - current_price) / max_price
            
            if drop >= drop_threshold:
                return "BUY"
        
        return "HOLD"
        
    except Exception as e:
        logging.getLogger("trading_bot").error(f"Drop strategy error: {e}")
        return "HOLD"


def check_sma_strategy(client, symbol, fast_period=10, slow_period=30):
    """
    Strategy: Buy/Sell based on Moving Average crossover.
    
    Args:
        client: Binance client
        symbol: Trading pair
        fast_period: Fast moving average period
        slow_period: Slow moving average period
    
    Returns:
        "BUY" if fast MA crosses above slow MA, "SELL" if crosses below
    """
    try:
        # Get candles for slow period
        candles = client.client.futures_klines(
            symbol=symbol,
            interval="1m",
            limit=slow_period + 10
        )
        
        prices = [float(c[4]) for c in candles]
        
        # Calculate moving averages
        fast_ma = sum(prices[-fast_period:]) / fast_period
        slow_ma = sum(prices[-slow_period:]) / slow_period
        prev_fast = sum(prices[-fast_period-1:-1]) / fast_period
        prev_slow = sum(prices[-slow_period-1:-1]) / slow_period
        
        # Check for crossover
        if prev_fast <= prev_slow and fast_ma > slow_ma:
            return "BUY"
        elif prev_fast >= prev_slow and fast_ma < slow_ma:
            return "SELL"
        
        return "HOLD"
        
    except Exception as e:
        logging.getLogger("trading_bot").error(f"SMA strategy error: {e}")
        return "HOLD"


def check_rsi_strategy(client, symbol, period=14, oversold=30, overbought=70):
    """
    Strategy: Buy when RSI is oversold, sell when overbought.
    
    Args:
        client: Binance client
        symbol: Trading pair
        period: RSI period
        oversold: Oversold threshold
        overbought: Overbought threshold
    
    Returns:
        "BUY" if RSI < oversold, "SELL" if RSI > overbought
    """
    try:
        # Get candles
        candles = client.client.futures_klines(
            symbol=symbol,
            interval="1m",
            limit=period + 1
        )
        
        prices = [float(c[4]) for c in candles]
        
        # Calculate RSI
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change >= 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        if rsi < oversold:
            return "BUY"
        elif rsi > overbought:
            return "SELL"
        
        return "HOLD"
        
    except Exception as e:
        logging.getLogger("trading_bot").error(f"RSI strategy error: {e}")
        return "HOLD"


def check_macd_strategy(client, symbol, fast=12, slow=26, signal=9):
    """
    Strategy: Buy/Sell based on MACD crossover.
    
    Args:
        client: Binance client
        symbol: Trading pair
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
    
    Returns:
        "BUY" if MACD crosses above signal, "SELL" if crosses below
    """
    try:
        # Get candles
        candles = client.client.futures_klines(
            symbol=symbol,
            interval="1m",
            limit=slow + signal + 10
        )
        
        prices = [float(c[4]) for c in candles]
        
        # Calculate EMAs
        def ema(data, period):
            multiplier = 2 / (period + 1)
            ema_values = [data[0]]
            for price in data[1:]:
                ema_values.append((price * multiplier) + (ema_values[-1] * (1 - multiplier)))
            return ema_values
        
        # Calculate MACD
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        
        macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
        signal_line = ema(macd_line, signal)
        
        # Check crossover
        if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
            return "BUY"
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
            return "SELL"
        
        return "HOLD"
        
    except Exception as e:
        logging.getLogger("trading_bot").error(f"MACD strategy error: {e}")
        return "HOLD"


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logger = setup_logging(log_file=args.log_file) if args.log_file else setup_logging()

    if not args.api_key or not args.api_secret:
        logger.error("Missing API credentials.")
        print("ERROR: Missing API credentials. Set BINANCE_API_KEY / BINANCE_API_SECRET or pass --api-key/--api-secret.")
        print("\n💡 TIP: You can also pass keys directly:")
        print("  python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001")
        return 1

    try:
        client = BinanceFuturesTestnetClient(args.api_key, args.api_secret)
    except ValueError as exc:
        logger.error("Client initialization failed: %s", exc)
        print(f"ERROR: {exc}")
        return 1

    # 🆕 WEB UI MODE - ADD THIS!
    if args.web:
        from bot.web_ui import start_web_ui
        start_web_ui(client, host=args.host, port=args.port)
        return 0

    # Check if running in interactive mode
    if args.interactive:
        from bot.interactive import interactive_menu
        interactive_menu(client)
        return 0

    # Check if running in auto mode
    if args.auto:
        run_auto_trading(
            client=client,
            symbol=args.symbol,
            strategy_name=args.strategy,
            interval=args.interval,
            amount=args.quantity or 0.001
        )
        return 0
    
    # Manual mode (Original behavior)
    # Validate required arguments for manual mode
    if not args.side:
        print("ERROR: --side is required for manual orders")
        return 1
    if not args.order_type:
        print("ERROR: --type is required for manual orders")
        return 1
    if not args.quantity:
        print("ERROR: --quantity is required for manual orders")
        return 1

    result = place_order(
        client=client,
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
        stop_price=args.stop_price,
    )

    print(result.summary())
    return 0 if result.success else 2


if __name__ == "__main__":
    sys.exit(main())