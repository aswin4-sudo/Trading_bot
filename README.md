
# Trading Bot - Binance Futures Testnet

A simplified Python trading bot for Binance USDT-M Futures Testnet with clean architecture, proper logging, and error handling.

## Overview

This application provides a command-line interface to place MARKET, LIMIT, and STOP_LIMIT orders on Binance Futures Testnet. It features multiple interaction modes including CLI commands, an interactive menu, and a web-based UI.

## Features

- Place MARKET and LIMIT orders (BUY/SELL)
- STOP_LIMIT orders
- CLI interface with argparse
- Interactive menu system
- Web UI
- Auto-trading strategies (SMA, RSI, MACD, Price Drop)
- Comprehensive logging to file
- Input validation and error handling
- Structured code with separation of concerns

## Setup

### Prerequisites

- Python 3.8+
- Binance Futures Testnet account
- API credentials from [Binance Futures Testnet](https://testnet.binancefuture.com)

### Installation

```bash
# Clone or download the repository
cd trading_bot

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
BINANCE_API_KEY=testnet_api_key
BINANCE_API_SECRET=testnet_api_secret
```

## Usage

### 1. Manual Orders

#### MARKET Order (BUY)
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

#### MARKET Order (SELL)
```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

#### LIMIT Order (BUY)
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 60000
```

#### LIMIT Order (SELL)
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

#### STOP_LIMIT Order
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 67000 --stop-price 66500
```

### 2. Interactive Menu

```bash
python cli.py --interactive
```

This launches a user-friendly menu system:
- Place MARKET/LIMIT/STOP_LIMIT orders
- View order status
- Start auto-trading
- View logs

### 3. Web UI

```bash
python cli.py --web
```

Open `http://localhost:5000` in your browser to access:
- Live price updates
- Order placement form
- Account balance information
- Auto-trading controls

### 4. Auto-Trading

```bash
# Price Drop Strategy
python cli.py --auto --symbol BTCUSDT --strategy drop --interval 30

# SMA Crossover Strategy
python cli.py --auto --symbol BTCUSDT --strategy sma --interval 60

# RSI Strategy
python cli.py --auto --symbol BTCUSDT --strategy rsi --interval 60

# MACD Strategy
python cli.py --auto --symbol BTCUSDT --strategy macd --interval 60
```

## Sample Output

### Successful MARKET Order

```
--- Order Request Summary ---
  symbol: BTCUSDT
  side: BUY
  order_type: MARKET
  quantity: 0.001
--- Order Response ---
  orderId:     18298305876
  status:      NEW
  executedQty: 0.0000
--- RESULT: SUCCESS ---
```

### Successful LIMIT Order

```
--- Order Request Summary ---
  symbol: BTCUSDT
  side: SELL
  order_type: LIMIT
  quantity: 0.001
  price: 65000.0
--- Order Response ---
  orderId:     18223545909
  status:      NEW
  executedQty: 0.0000
--- RESULT: SUCCESS ---

## Error Handling

The bot handles:

- Invalid input (validation errors)
- API errors (Binance API exceptions)
- Network failures (connection/timeout)
- Missing credentials
- Malformed requests
- Unexpected exceptions

## Assumptions

1. API credentials are for Binance Futures Testnet only
2. Trading pairs must end with USDT (e.g., BTCUSDT, ETHUSDT)
3. Minimum quantity for BTCUSDT is 0.001
4. Testnet base URL: `https://testnet.binancefuture.com`

