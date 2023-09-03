from src.api.ccxt_interface import CCXTInterface
from src.analysis.volume import VolumeAnalysis
import sys
import logging
import time
import threading
from datetime import datetime, timedelta

# Add the 'src' directory to the sys.path list
sys.path.append('./src')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to display a loading spinner
def loading_spinner():
    spinner = "|/-\\"
    idx = 0
    while True:
        print(f"\rLoading... {spinner[idx % len(spinner)]}", end="")
        idx += 1
        time.sleep(0.1)


def main():
    # Start the loading spinner in a separate thread
    spinner_thread = threading.Thread(target=loading_spinner)
    spinner_thread.daemon = True
    spinner_thread.start()

    # Initialize CCXT Interface and Volume Analysis
    ccxt_interface = CCXTInterface()
    volume_analysis = VolumeAnalysis()

    # Initialize the exchange
    if not ccxt_interface.initialize_exchange('binance'):
        logger.error("Failed to initialize exchange.")
        return

    # Fetch all available symbols from the exchange and filter for "/USDT"
    all_symbols = list(ccxt_interface.exchange.markets.keys())
    symbols = [symbol for symbol in all_symbols if symbol.endswith('/USDT')]

    # Calculate the timestamp for the last 30 days
    since_time = datetime.utcnow() - timedelta(days=30)
    since_timestamp = int(time.mktime(since_time.timetuple()) * 1000)

    ohlcv_dict = {}

    for symbol in symbols:
        if ccxt_interface.check_symbol(symbol):
            try:
                ohlcv_df = ccxt_interface.fetch_and_convert_ohlcv(
                    symbol, '1h', since=since_timestamp)
                ohlcv_dict[symbol] = ohlcv_df
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {e}")
        else:
            logger.warning(f"Symbol {symbol} not found on the exchange.")

    # Stop the spinner thread
    spinner_thread.join(timeout=0.1)

    # Perform volume analysis
    print("\rPerforming volume analysis... ", end="")
    volume_analysis.analyze_multiple_symbols(ohlcv_dict)
    print("Done.")


if __name__ == "__main__":
    main()
