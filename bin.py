import pandas as pd
import os
import binance
import datetime

window = int(os.environ.get('RSI_WINDOW'))
# Binance API credentials (use your own)
api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_API_SECRET')

# Initialize Binance client
client = binance.Client(api_key, api_secret)

# Get top 50 coins
top_coins = client.get_ticker()

for coin in top_coins:
    coin['quoteVolume'] = float(coin['quoteVolume'])
    coin['volume'] = float(coin['volume'])
    coin['lastPrice'] = float(coin['lastPrice'])

filtered_coins = pd.read_excel('Top81.xlsx', header=None)
filtered_coins = filtered_coins[0].tolist()
filtered_coins = [coin.replace('/', '') for coin in filtered_coins]

top_coins = [coin for coin in top_coins if coin['symbol'] in filtered_coins]

print(f"Filtered coins: {len(filtered_coins)} | Coins Found: {len(top_coins)} | Not found: {len(filtered_coins) - len(top_coins)}")

def get_percentage_change(data, interval):
    """Calculate percentage change over a given interval."""
    close_prices = [float(item[4]) for item in data]  # Closing prices
    current_price = close_prices[-1]
    previous_price = close_prices[0]
    percentage_change = ((current_price - previous_price) / previous_price) * 100
    return percentage_change

def fetch_and_calculate(symbol):
    """Fetch historical data and calculate percentage changes for different intervals."""
    intervals = {
        '1D': '1d',
        '1H': '1h',
        '30M': '30m',
        '4H': '4h'
    }

    changes = {}

    for label, interval in intervals.items():
        if interval == '1d':
            data = client.get_historical_klines(symbol, interval)
        elif interval == '1h':
            data = client.get_historical_klines(symbol, interval)
        elif interval == '30m':
            data = client.get_historical_klines(symbol, interval)
        elif interval == '4h':
            data = client.get_historical_klines(symbol, interval)
        
        changes[label] = calculate_rsi(data, window)
    
    return changes

def calculate_rsi(klines, window):
    """Calculate the RSI for given price data and window"""

    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
                                     'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                     'taker_buy_quote_asset_volume', 'ignore'])

    # Convert the 'close' column to float
    data['close'] = data['close'].astype(float)

    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# Define time frames
time_frames = {'1d': '1D', '1h': '1H', '30m': '30M', '15m': '15M'}

# Initialize an empty list to store results
results = []

# Get current time
current_time = datetime.datetime.utcnow().strftime('%H:%M')

# Loop through each coin and check RSI for each time frame
for coin in top_coins:
    symbol = coin['symbol']
    if not symbol.endswith('USDT'):
        continue

    rate = float(coin['lastPrice'])
    change = fetch_and_calculate(symbol)
    result = {
        'Date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
        'Symbol': symbol,
        'Rate': rate,
        'Time': current_time,
        **change,
        **coin
    }
    results.append(result)

# Convert results to DataFrame
df = pd.DataFrame(results)

current_time_stamp = datetime.datetime.utcnow().strftime('%Y-%m-%d|%H:%M')

df.to_excel(f"{current_time_stamp}.xlsx", index=False)

print(f"{current_time_stamp}.xlsx")