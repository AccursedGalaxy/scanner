# in this file we will analyse the volume of the ohlcv data we fetch via the CCXTInterface
# we will look at the average volume per day, and the average volume per hour
# we will also look at the volume of the last 24 hours

# We will check if the volume of the last 24 hours is higher than the average volume per day(1.5x)
# We will check if the volume of the last hour is higher than the average volume per hour(2x)

# We will do this for multiple symbols.

import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VolumeAnalysis:
    def __init__(self):
        pass

    def average_volume_per_day(self, ohlcv_df):
        daily_volume = ohlcv_df.resample('D').sum()['volume']
        avg_daily_volume = daily_volume.mean()
        return avg_daily_volume

    def average_volume_per_hour(self, ohlcv_df):
        hourly_volume = ohlcv_df.resample('H').sum()['volume']
        avg_hourly_volume = hourly_volume.mean()
        return avg_hourly_volume

    def last_24_hours_volume(self, ohlcv_df):
        last_24_hours = datetime.now() - timedelta(days=1)
        last_24_hours_volume = ohlcv_df.loc[ohlcv_df.index >= last_24_hours].sum()[
            'volume']
        return last_24_hours_volume

    def last_hour_volume(self, ohlcv_df):
        last_hour = datetime.now() - timedelta(hours=1)
        last_hour_volume = ohlcv_df.loc[ohlcv_df.index >= last_hour].sum()[
            'volume']
        return last_hour_volume

    def check_volume_spike_24h(self, ohlcv_df):
        avg_daily_volume = self.average_volume_per_day(ohlcv_df)
        last_24h_volume = self.last_24_hours_volume(ohlcv_df)
        if last_24h_volume > 1.5 * avg_daily_volume:
            logger.info("Volume spike detected in the last 24 hours.")
            return True
        return False

    def check_volume_spike_1h(self, ohlcv_df):
        avg_hourly_volume = self.average_volume_per_hour(ohlcv_df)
        last_hour_volume = self.last_hour_volume(ohlcv_df)
        if last_hour_volume > 2 * avg_hourly_volume:
            logger.info("Volume spike detected in the last hour.")
            return True
        return False

    def analyze_multiple_symbols(self, ohlcv_dict):
        for symbol, ohlcv_df in ohlcv_dict.items():
            logger.info(f"Analyzing volume for {symbol}")
            self.check_volume_spike_24h(ohlcv_df)
            self.check_volume_spike_1h(ohlcv_df)
