# Crypto Volume Analysis

## Overview

This project aims to analyze the trading volume of various cryptocurrency pairs on exchanges. It uses the CCXT library to fetch historical OHLCV (Open/High/Low/Close/Volume) data and performs volume analysis to detect spikes or unusual activities.

## Features

- Fetches OHLCV data from multiple exchanges via the CCXT library.
- Calculates average daily and hourly volumes.
- Detects volume spikes in the last 24 hours and the last hour.
- Supports analysis for multiple trading pairs.
- Provides a terminal-based loading spinner for better user experience.

## Requirements

- Python 3.x
- CCXT library
- Pandas

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/CryptoVolumeAnalysis.git
    ```

2. Navigate to the project directory:

    ```bash
    cd CryptoVolumeAnalysis
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the main script:

    ```bash
    python main.py
    ```

2. The script will initialize the Binance exchange by default and fetch OHLCV data for all available trading pairs.

3. The volume analysis will be performed, and any detected volume spikes will be logged.

## Customization

- To analyze a different exchange, modify the `initialize_exchange('binance')` line in the `main()` function.
- To analyze specific trading pairs, modify the `symbols` list in the `main()` function.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
