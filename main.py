from src.api.ccxt_interface import CCXTInterface
from src.analysis.volume import VolumeAnalysis
import sys
import logging
import time
import threading

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

    # List of symbols and timeframes to analyze
    symbols = ['BTC/USDT', 'ETH/USDT']
    timeframe = '1h'  # Fetching 1-hour data to calculate both daily and hourly volumes

    ohlcv_dict = {}

    for symbol in symbols:
        if ccxt_interface.check_symbol(symbol):
            ohlcv_df = ccxt_interface.fetch_and_convert_ohlcv(
                symbol, timeframe)
            ohlcv_dict[symbol] = ohlcv_df
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
