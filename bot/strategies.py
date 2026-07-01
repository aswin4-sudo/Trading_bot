
"""
Automated trading strategies.
"""
import time
import logging
from datetime import datetime

logger = logging.getLogger("trading_bot")

class TradingStrategy:
    def __init__(self, client, symbol="BTCUSDT"):
        self.client = client
        self.symbol = symbol
        self.position = None  # None = no position, "BUY" = long, "SELL" = short
        
    def get_price(self):
        """Get current price from Binance."""
        try:
            ticker = self.client.client.futures_symbol_ticker(symbol=self.symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Failed to get price: {e}")
            return None
    
    def simple_moving_average_strategy(self):
        """
        Simple strategy:
        - If price > 50-period average → BUY
        - If price < 50-period average → SELL
        """
        # Get last 50 candles
        candles = self.client.client.futures_klines(
            symbol=self.symbol,
            interval="1m",
            limit=50
        )
        
        # Calculate average
        closes = [float(c[4]) for c in candles]
        avg = sum(closes) / len(closes)
        current_price = self.get_price()
        
        if current_price > avg:
            return "BUY"
        elif current_price < avg:
            return "SELL"
        else:
            return "HOLD"
    
    def run_strategy(self):
        """Run the automated strategy."""
        while True:
            try:
                signal = self.simple_moving_average_strategy()
                current_price = self.get_price()
                
                logger.info(f"Price: {current_price}, Signal: {signal}")
                
                if signal == "BUY" and self.position != "BUY":
                    # Place BUY order
                    self.client.place_order(
                        symbol=self.symbol,
                        side="BUY",
                        order_type="MARKET",
                        quantity=0.001
                    )
                    self.position = "BUY"
                    logger.info(f"✅ AUTO-BUY at {current_price}")
                    
                elif signal == "SELL" and self.position != "SELL":
                    # Place SELL order
                    self.client.place_order(
                        symbol=self.symbol,
                        side="SELL",
                        order_type="MARKET",
                        quantity=0.001
                    )
                    self.position = "SELL"
                    logger.info(f"✅ AUTO-SELL at {current_price}")
                
                # Wait 1 minute before checking again
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Strategy error: {e}")
                time.sleep(60)