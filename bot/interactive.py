
"""
Interactive CLI menu for the trading bot.
Provides a user-friendly menu system for placing orders.
"""

import os
import sys
import logging
from datetime import datetime

logger = logging.getLogger("trading_bot")


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("  🚀 TRADING BOT - Binance Futures Testnet")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)


def print_menu():
    """Print the main menu."""
    print("\n📋 MAIN MENU")
    print("-" * 60)
    print("  1. 📈 Place MARKET Order")
    print("  2. 📊 Place LIMIT Order")
    print("  3. 🎯 Place STOP_LIMIT Order")
    print("  4. 📋 View Order Status")
    print("  5. 🔄 Start Auto-Trading")
    print("  6. 📝 View Logs")
    print("  7. ❌ Exit")
    print("-" * 60)


def get_user_input(prompt, default=None, input_type=str):
    """Get validated user input."""
    while True:
        try:
            if default is not None:
                user_input = input(f"{prompt} [{default}]: ") or str(default)
            else:
                user_input = input(f"{prompt}: ")
            
            if not user_input and default is None:
                print("❌ Input required. Please try again.")
                continue
            
            if input_type == float:
                return float(user_input)
            elif input_type == int:
                return int(user_input)
            elif input_type == bool:
                return user_input.lower() in ['y', 'yes', 'true', '1']
            else:
                return user_input.strip().upper()
                
        except ValueError:
            print(f"❌ Invalid input. Please enter a valid {input_type.__name__}.")


def interactive_menu(client):
    """Run the interactive menu."""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = get_user_input("\n👉 Select option", default="", input_type=int)
        
        if choice == 1:
            place_market_order_menu(client)
        elif choice == 2:
            place_limit_order_menu(client)
        elif choice == 3:
            place_stop_limit_order_menu(client)
        elif choice == 4:
            view_order_status_menu(client)
        elif choice == 5:
            start_auto_trading_menu(client)
        elif choice == 6:
            view_logs_menu()
        elif choice == 7:
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid option. Press Enter to continue...")
            input()


def place_market_order_menu(client):
    """Interactive menu for MARKET orders."""
    clear_screen()
    print_header()
    print("\n📈 PLACE MARKET ORDER")
    print("-" * 60)
    
    # Get order details
    symbol = get_user_input("Symbol (e.g., BTCUSDT)", "BTCUSDT")
    side = get_user_input("Side (BUY/SELL)", "BUY")
    quantity = get_user_input("Quantity", "0.001", float)
    
    # Show summary
    print("\n📋 ORDER SUMMARY")
    print("-" * 60)
    print(f"  Symbol:   {symbol}")
    print(f"  Side:     {side}")
    print(f"  Type:     MARKET")
    print(f"  Quantity: {quantity}")
    print("-" * 60)
    
    confirm = get_user_input("\nConfirm order? (y/n)", "n", bool)
    
    if confirm:
        from bot.orders import place_order
        result = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=quantity
        )
        print("\n" + result.summary())
    else:
        print("\n❌ Order cancelled")
    
    input("\nPress Enter to continue...")


def place_limit_order_menu(client):
    """Interactive menu for LIMIT orders."""
    clear_screen()
    print_header()
    print("\n📊 PLACE LIMIT ORDER")
    print("-" * 60)
    
    # Get order details
    symbol = get_user_input("Symbol (e.g., BTCUSDT)", "BTCUSDT")
    side = get_user_input("Side (BUY/SELL)", "BUY")
    quantity = get_user_input("Quantity", "0.001", float)
    price = get_user_input("Price (e.g., 65000)", None, float)
    
    # Show summary
    print("\n📋 ORDER SUMMARY")
    print("-" * 60)
    print(f"  Symbol:   {symbol}")
    print(f"  Side:     {side}")
    print(f"  Type:     LIMIT")
    print(f"  Quantity: {quantity}")
    print(f"  Price:    ${price:,.2f}" if price else "  Price:    Not set")
    print("-" * 60)
    
    confirm = get_user_input("\nConfirm order? (y/n)", "n", bool)
    
    if confirm:
        from bot.orders import place_order
        result = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type="LIMIT",
            quantity=quantity,
            price=price
        )
        print("\n" + result.summary())
    else:
        print("\n❌ Order cancelled")
    
    input("\nPress Enter to continue...")


def place_stop_limit_order_menu(client):
    """Interactive menu for STOP_LIMIT orders."""
    clear_screen()
    print_header()
    print("\n🎯 PLACE STOP_LIMIT ORDER")
    print("-" * 60)
    
    # Get order details
    symbol = get_user_input("Symbol (e.g., BTCUSDT)", "BTCUSDT")
    side = get_user_input("Side (BUY/SELL)", "BUY")
    quantity = get_user_input("Quantity", "0.001", float)
    price = get_user_input("Limit Price (e.g., 67000)", None, float)
    stop_price = get_user_input("Stop Price (e.g., 66500)", None, float)
    
    # Show summary
    print("\n📋 ORDER SUMMARY")
    print("-" * 60)
    print(f"  Symbol:      {symbol}")
    print(f"  Side:        {side}")
    print(f"  Type:        STOP_LIMIT")
    print(f"  Quantity:    {quantity}")
    print(f"  Limit Price: ${price:,.2f}" if price else "  Limit Price: Not set")
    print(f"  Stop Price:  ${stop_price:,.2f}" if stop_price else "  Stop Price: Not set")
    print("-" * 60)
    
    confirm = get_user_input("\nConfirm order? (y/n)", "n", bool)
    
    if confirm:
        from bot.orders import place_order
        result = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type="STOP_LIMIT",
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        print("\n" + result.summary())
    else:
        print("\n❌ Order cancelled")
    
    input("\nPress Enter to continue...")


def view_order_status_menu(client):
    """View order status."""
    clear_screen()
    print_header()
    print("\n📋 VIEW ORDER STATUS")
    print("-" * 60)
    
    symbol = get_user_input("Symbol (e.g., BTCUSDT)", "BTCUSDT")
    order_id = get_user_input("Order ID", None, int)
    
    try:
        status = client.get_order_status(symbol, order_id)
        print("\n📊 ORDER STATUS")
        print("-" * 60)
        for key, value in status.items():
            print(f"  {key}: {value}")
        print("-" * 60)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")


def start_auto_trading_menu(client):
    """Start auto-trading from menu."""
    clear_screen()
    print_header()
    print("\n🔄 START AUTO-TRADING")
    print("-" * 60)
    
    symbol = get_user_input("Symbol (e.g., BTCUSDT)", "BTCUSDT")
    
    print("\n📊 Select Strategy:")
    print("  1. DROP (Buy when price drops)")
    print("  2. SMA (Moving Average Crossover)")
    print("  3. RSI (Oversold/Overbought)")
    print("  4. MACD (MACD Crossover)")
    
    strategy_choice = get_user_input("Strategy", "1", int)
    
    strategies = {
        1: "drop",
        2: "sma",
        3: "rsi",
        4: "macd"
    }
    
    strategy = strategies.get(strategy_choice, "drop")
    interval = get_user_input("Check interval (seconds)", "60", int)
    amount = get_user_input("Trade amount", "0.001", float)
    
    print(f"\n✅ Starting auto-trading with {strategy.upper()} strategy...")
    print("Press Ctrl+C to stop\n")
    
    # Import and run auto-trading from cli
    # We need to use the run_auto_trading function from cli.py
    # But to avoid circular imports, we'll use a direct call
    try:
        # Import the function from cli.py
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from cli import run_auto_trading
        run_auto_trading(client, symbol, strategy, interval, amount)
    except KeyboardInterrupt:
        print("\n🛑 Auto-trading stopped")
    except Exception as e:
        print(f"❌ Error starting auto-trading: {e}")
    
    input("\nPress Enter to continue...")


def view_logs_menu():
    """View recent logs."""
    clear_screen()
    print_header()
    print("\n📝 VIEW LOGS")
    print("-" * 60)
    
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "trading_bot.log")
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Show last 30 lines
                print("\n📄 Last 30 log entries:\n")
                for line in lines[-30:]:
                    print(line.strip())
        else:
            print("❌ Log file not found. Run some orders first!")
    except Exception as e:
        print(f"❌ Error reading logs: {e}")
    
    input("\nPress Enter to continue...")