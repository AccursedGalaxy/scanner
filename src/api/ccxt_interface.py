# This will be the ccxt interface of the scanner application
# it will be used to fetch ohlcv data and orderbook as well as other data from exchanges

import ccxt
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CCXTInterface:
    def __init__(self):
        self.exchange = None

    def initialize_exchange(self, exchange_name):
        try:
            self.exchange = getattr(ccxt, exchange_name)()
            self.exchange.load_markets()
            logger.info("Exchange initialized: {}".format(exchange_name))
        except Exception as e:
            logger.error(
                "Error initializing exchange: {}".format(exchange_name))
            logger.error(e)
            return False
        return True

    def check_symbol(self, symbol):
        if symbol in self.exchange.markets:
            return True
        return False

    def fetch_ohlcv(self, symbol, timeframe, since=None):
        ohlcv = []
        while True:
            try:
                new_data = self.exchange.fetch_ohlcv(symbol, timeframe, since)
                if len(new_data) == 0:
                    break
                ohlcv += new_data
                since = new_data[-1][0] + 1  # +1 to avoid duplicates
                logger.info(
                    f"Fetched {len(new_data)} for symbol: {symbol} total data points: {len(ohlcv)}")
            except Exception as e:
                logger.error(f"Failed to fetch ohlcv: {e}")
                break
        return ohlcv

    def convert_timestamp(self, ohlcv):
        df = pd.DataFrame(
            ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        logger.info(f"Converted ohlcv data to dataframe. Shape: {df.shape}")
        return df

    def fetch_and_convert_ohlcv(self, symbol, timeframe, since=1262304000000):
        ohlcv = self.fetch_ohlcv(symbol, timeframe, since)
        df = self.convert_timestamp(ohlcv)
        return df

    def fetch_ticker(self, symbol):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Failed to fetch ticker: {e}")
            return None

    def fetch_order_book(self, symbol, limit=5):
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            return order_book
        except Exception as e:
            logger.error(f"Failed to fetch order book: {e}")
            return None

    def fetch_trades(self, symbol, since=None, limit=50):
        try:
            trades = self.exchange.fetch_trades(symbol, since, limit)
            return trades
        except Exception as e:
            logger.error(f"Failed to fetch trades: {e}")
            return None
