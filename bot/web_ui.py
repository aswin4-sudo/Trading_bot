# bot/web_ui.py
"""
Lightweight Web UI for the trading bot.
Provides a graphical interface accessible from a browser.
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
import logging
import threading
from datetime import datetime

logger = logging.getLogger("trading_bot")

# Global client reference
client = None
app = Flask(__name__)

# Add the root directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@app.route('/')
def index():
    """Home page with order form."""
    return render_template('index.html')


@app.route('/api/place_order', methods=['POST'])
def place_order_api():
    """API endpoint for placing orders."""
    try:
        data = request.json
        
        from bot.orders import place_order
        
        # Get price and stop_price as float or None
        price = float(data.get('price')) if data.get('price') and data.get('price') != '' else None
        stop_price = float(data.get('stop_price')) if data.get('stop_price') and data.get('stop_price') != '' else None
        
        result = place_order(
            client=client,
            symbol=data.get('symbol', 'BTCUSDT').upper(),
            side=data.get('side', 'BUY').upper(),
            order_type=data.get('order_type', 'MARKET').upper(),
            quantity=float(data.get('quantity', 0.001)),
            price=price,
            stop_price=stop_price
        )
        
        return jsonify({
            'success': result.success,
            'orderId': result.response.get('orderId') if result.success and result.response else None,
            'status': result.response.get('status') if result.success and result.response else None,
            'executedQty': result.response.get('executedQty') if result.success and result.response else None,
            'avgPrice': result.response.get('avgPrice') if result.success and result.response else None,
            'error': result.error,
            'summary': result.summary()
        })
        
    except Exception as e:
        logger.error(f"Web API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/price/<symbol>')
def get_price(symbol):
    """Get current price for a symbol."""
    try:
        if not client:
            return jsonify({'error': 'Client not initialized'})
        
        ticker = client.client.futures_symbol_ticker(symbol=symbol.upper())
        return jsonify({
            'symbol': symbol.upper(),
            'price': ticker['price'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Price API error: {e}")
        return jsonify({'error': str(e)})


@app.route('/api/account')
def get_account():
    """Get account information."""
    try:
        if not client:
            return jsonify({'error': 'Client not initialized'})
        
        account = client.client.futures_account()
        return jsonify({
            'success': True,
            'canTrade': account.get('canTrade'),
            'totalWalletBalance': account.get('totalWalletBalance'),
            'totalUnrealizedProfit': account.get('totalUnrealizedProfit')
        })
    except Exception as e:
        logger.error(f"Account API error: {e}")
        return jsonify({'error': str(e)})


@app.route('/api/start_auto', methods=['POST'])
def start_auto_trading_api():
    """Start auto-trading from web UI."""
    try:
        data = request.json
        symbol = data.get('symbol', 'BTCUSDT').upper()
        strategy = data.get('strategy', 'drop')
        interval = int(data.get('interval', 60))
        amount = float(data.get('amount', 0.001))
        
        # Import the run_auto_trading function from cli.py (in root)
        # Since cli.py is in the root, we need to import it differently
        import importlib.util
        import sys
        
        # Get the root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cli_path = os.path.join(root_dir, 'cli.py')
        
        # Load cli.py as a module
        spec = importlib.util.spec_from_file_location("cli", cli_path)
        cli_module = importlib.util.module_from_spec(spec)
        sys.modules["cli"] = cli_module
        spec.loader.exec_module(cli_module)
        
        # Get the run_auto_trading function
        run_auto_trading = cli_module.run_auto_trading
        
        # Start auto-trading in a thread
        def run_auto():
            try:
                run_auto_trading(client, symbol, strategy, interval, amount)
            except Exception as e:
                logger.error(f"Auto-trading thread error: {e}")
        
        thread = threading.Thread(target=run_auto, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Auto-trading started with {strategy} strategy',
            'symbol': symbol,
            'strategy': strategy,
            'interval': interval,
            'amount': amount
        })
        
    except Exception as e:
        logger.error(f"Auto-trading API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


def start_web_ui(binance_client, host='127.0.0.1', port=5000):
    """Start the web UI."""
    global client
    client = binance_client
    
    # Create templates folder if it doesn't exist
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    html_path = os.path.join(template_dir, 'index.html')
    if not os.path.exists(html_path):
        create_html_template(template_dir)
    
    print(f"\n🌐 Web UI starting at http://{host}:{port}")
    print("📊 Open this URL in your browser")
    print("⚠️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(host=host, port=port, debug=False)


def create_html_template(template_dir):
    """Create the HTML template for the web UI."""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Trading Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e17;
            color: #e0e0e0;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: #161b22;
            padding: 20px 30px;
            border-radius: 12px;
            border: 1px solid #30363d;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 28px;
            background: linear-gradient(90deg, #f7931a, #ff6b35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header .status { color: #8b949e; font-size: 14px; }
        .header .status .online { color: #3fb950; }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
        }
        .card h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #f0f6fc;
        }
        .form-group {
            margin-bottom: 12px;
        }
        .form-group label {
            display: block;
            font-size: 13px;
            color: #8b949e;
            margin-bottom: 4px;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 8px 12px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #e0e0e0;
            font-size: 14px;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #f7931a;
        }
        .btn {
            padding: 10px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            width: 100%;
        }
        .btn-primary {
            background: linear-gradient(90deg, #f7931a, #ff6b35);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(247, 147, 26, 0.3);
        }
        .btn-success {
            background: #238636;
            color: white;
        }
        .btn-success:hover {
            background: #2ea043;
        }
        .btn-danger {
            background: #da3633;
            color: white;
        }
        .result-box {
            margin-top: 15px;
            padding: 15px;
            background: #0d1117;
            border-radius: 6px;
            border-left: 4px solid #f7931a;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }
        .result-box.success { border-left-color: #3fb950; }
        .result-box.error { border-left-color: #f85149; }
        .result-box.hidden { display: none; }
        .price-display {
            text-align: center;
            padding: 20px;
            background: #0d1117;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .price-display .price {
            font-size: 36px;
            font-weight: bold;
            color: #3fb950;
        }
        .price-display .label {
            font-size: 14px;
            color: #8b949e;
        }
        .order-type-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
        }
        .order-type-tabs button {
            padding: 8px 16px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #8b949e;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }
        .order-type-tabs button.active {
            background: #f7931a;
            color: white;
            border-color: #f7931a;
        }
        .order-type-tabs button:hover {
            border-color: #f7931a;
        }
        .hidden { display: none !important; }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            background: #238636;
            color: white;
        }
        hr {
            border: none;
            border-top: 1px solid #30363d;
            margin: 15px 0;
        }
        .account-info p {
            margin: 5px 0;
            color: #e0e0e0;
        }
        .account-info .label-text {
            color: #8b949e;
        }
        #auto-status {
            margin-top: 10px;
            font-size: 13px;
            color: #8b949e;
        }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .header { flex-direction: column; text-align: center; gap: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🚀 Trading Bot</h1>
            <div class="status">
                <span class="online">●</span> Online
                <span style="margin-left: 15px;">⚡ Binance Futures Testnet</span>
                <span style="margin-left: 15px;" id="time-display"></span>
            </div>
        </div>

        <!-- Price Display -->
        <div class="card" style="margin-bottom: 20px;">
            <div class="price-display">
                <div class="label" id="price-label">BTCUSDT Price</div>
                <div class="price" id="price-display">$0.00</div>
            </div>
        </div>

        <!-- Main Grid -->
        <div class="grid">
            <!-- Order Form -->
            <div class="card">
                <h2>📊 Place Order</h2>
                
                <div class="order-type-tabs">
                    <button class="active" data-type="MARKET">MARKET</button>
                    <button data-type="LIMIT">LIMIT</button>
                    <button data-type="STOP_LIMIT">STOP_LIMIT</button>
                </div>

                <form id="order-form">
                    <div class="form-group">
                        <label>Symbol</label>
                        <input type="text" id="symbol" value="BTCUSDT">
                    </div>
                    <div class="form-group">
                        <label>Side</label>
                        <select id="side">
                            <option value="BUY">BUY</option>
                            <option value="SELL">SELL</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Quantity</label>
                        <input type="number" id="quantity" value="0.001" step="0.001" min="0.001">
                    </div>
                    <div class="form-group" id="price-group">
                        <label>Price</label>
                        <input type="number" id="price" placeholder="Enter limit price (e.g., 65000)">
                    </div>
                    <div class="form-group hidden" id="stop-price-group">
                        <label>Stop Price</label>
                        <input type="number" id="stop_price" placeholder="Enter stop price (e.g., 66000)">
                    </div>
                    <button type="submit" class="btn btn-primary">Place Order</button>
                </form>

                <div id="order-result" class="result-box hidden"></div>
            </div>

            <!-- Account & Auto-Trading -->
            <div class="card">
                <h2>💼 Account</h2>
                <div id="account-info" class="account-info">
                    <p>Loading account info...</p>
                </div>
                <hr>
                
                <h2>🤖 Auto-Trading</h2>
                <div class="form-group">
                    <label>Strategy</label>
                    <select id="auto-strategy">
                        <option value="drop">Price Drop</option>
                        <option value="sma">SMA Crossover</option>
                        <option value="rsi">RSI Strategy</option>
                        <option value="macd">MACD Strategy</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Interval (seconds)</label>
                    <input type="number" id="auto-interval" value="60">
                </div>
                <div class="form-group">
                    <label>Amount</label>
                    <input type="number" id="auto-amount" value="0.001" step="0.001">
                </div>
                <button id="start-auto-btn" class="btn btn-success">▶ Start Auto-Trading</button>
                <div id="auto-status"></div>
            </div>
        </div>
    </div>

    <script>
        // Order type tabs
        const tabs = document.querySelectorAll('.order-type-tabs button');
        let currentOrderType = 'MARKET';

        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                currentOrderType = this.dataset.type;
                
                document.getElementById('price-group').classList.toggle('hidden', currentOrderType === 'MARKET');
                document.getElementById('stop-price-group').classList.toggle('hidden', currentOrderType !== 'STOP_LIMIT');
            });
        });

        // Update time
        function updateTime() {
            document.getElementById('time-display').textContent = new Date().toLocaleTimeString();
        }
        setInterval(updateTime, 1000);
        updateTime();

        // Update price
        function updatePrice() {
            const symbol = document.getElementById('symbol').value || 'BTCUSDT';
            fetch(`/api/price/${symbol}`)
                .then(response => response.json())
                .then(data => {
                    if (data.price) {
                        const price = parseFloat(data.price);
                        document.getElementById('price-display').textContent = `$${price.toFixed(2)}`;
                        document.getElementById('price-label').textContent = `${symbol} Price`;
                    }
                })
                .catch(() => {
                    document.getElementById('price-display').textContent = 'Error loading price';
                });
        }
        setInterval(updatePrice, 5000);
        updatePrice();

        // Load account info
        function loadAccount() {
            fetch('/api/account')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('account-info').innerHTML = `
                            <p><span class="label-text">💰 Balance:</span> $${parseFloat(data.totalWalletBalance || 0).toFixed(2)}</p>
                            <p><span class="label-text">📈 P&L:</span> $${parseFloat(data.totalUnrealizedProfit || 0).toFixed(2)}</p>
                            <p><span class="label-text">📊 Status:</span> ${data.canTrade ? '✅ Trading Enabled' : '❌ Trading Disabled'}</p>
                        `;
                    }
                })
                .catch(() => {
                    document.getElementById('account-info').innerHTML = '<p style="color: #8b949e;">Account info unavailable</p>';
                });
        }
        loadAccount();

        // Place order
        document.getElementById('order-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const resultDiv = document.getElementById('order-result');
            resultDiv.className = 'result-box';
            resultDiv.textContent = '⏳ Placing order...';
            resultDiv.classList.remove('hidden');

            const data = {
                symbol: document.getElementById('symbol').value,
                side: document.getElementById('side').value,
                order_type: currentOrderType,
                quantity: document.getElementById('quantity').value,
                price: document.getElementById('price').value,
                stop_price: document.getElementById('stop_price').value
            };

            fetch('/api/place_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    resultDiv.className = 'result-box success';
                    resultDiv.textContent = data.summary || '✅ Order placed successfully!';
                } else {
                    resultDiv.className = 'result-box error';
                    resultDiv.textContent = `❌ Error: ${data.error || 'Order failed'}`;
                }
            })
            .catch(error => {
                resultDiv.className = 'result-box error';
                resultDiv.textContent = `❌ Error: ${error.message}`;
            });
        });

        // Start auto-trading
        document.getElementById('start-auto-btn').addEventListener('click', function() {
            const btn = this;
            const statusDiv = document.getElementById('auto-status');
            
            const data = {
                symbol: document.getElementById('symbol').value,
                strategy: document.getElementById('auto-strategy').value,
                interval: parseInt(document.getElementById('auto-interval').value),
                amount: parseFloat(document.getElementById('auto-amount').value)
            };

            btn.disabled = true;
            btn.textContent = '⏳ Starting...';
            statusDiv.textContent = 'Starting auto-trading...';

            fetch('/api/start_auto', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    statusDiv.innerHTML = `
                        ✅ Auto-trading started!<br>
                        📊 Strategy: ${data.strategy}<br>
                        ⏱️ Interval: ${data.interval}s<br>
                        💰 Amount: ${data.amount}<br>
                        <span style="color: #d29922;">⚠️ Check terminal for output</span>
                    `;
                    btn.textContent = '▶ Running...';
                } else {
                    statusDiv.textContent = `❌ Error: ${data.error}`;
                    btn.disabled = false;
                    btn.textContent = '▶ Start Auto-Trading';
                }
            })
            .catch(error => {
                statusDiv.textContent = `❌ Error: ${error.message}`;
                btn.disabled = false;
                btn.textContent = '▶ Start Auto-Trading';
            });
        });
    </script>
</body>
</html>'''
    
    with open(os.path.join(template_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)