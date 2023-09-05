from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidget, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication, QTimer
from src.api.ccxt_interface import CCXTInterface
from src.analysis.volume import VolumeAnalysis
import pyqtgraph as pg
import sys
import logging
import time
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScannerThread(QThread):
    update_alert_box = pyqtSignal(str)
    update_graph = pyqtSignal(dict, list, list)

    def __init__(self, window):
        super(ScannerThread, self).__init__()
        self.window = window

    def run(self):
        ccxt_interface = CCXTInterface()
        volume_analysis = VolumeAnalysis(self.window)
        if not ccxt_interface.initialize_exchange('binance'):
            logger.error("Failed to initialize exchange.")
            return
        all_symbols = list(ccxt_interface.exchange.markets.keys())
        symbols = [
            symbol for symbol in all_symbols if symbol.endswith('/USDT')]
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
        volume_analysis.analyze_multiple_symbols(ohlcv_dict)
        if len(volume_analysis.spikes_24h) > 0:
            self.update_alert_box.emit(
                f"Volume spike detected in the last 24 hours for {volume_analysis.spikes_24h}")
        else:
            self.update_alert_box.emit("No 24h volume spikes detected.")
        if len(volume_analysis.spikes_1h) > 0:
            self.update_alert_box.emit(
                f"Volume spike detected in the last hour for {volume_analysis.spikes_1h}")
        else:
            self.update_alert_box.emit("No 1h volume spikes detected.")

        self.update_graph.emit(
            ohlcv_dict, volume_analysis.spikes_24h, volume_analysis.spikes_1h)  # Emit lists


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Crypto Volume Scanner")
        layout = QVBoxLayout()

        # Add real-time graph
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setTitle("Real time Volume Spikes")
        layout.addWidget(self.graphWidget)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.symbol_list = QListWidget()
        self.alert_box = QTextEdit()
        self.alert_box.setReadOnly(True)
        self.alert_box.setText("Alerts will appear here.")
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.symbol_list)
        layout.addWidget(self.alert_box)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.scanner_thread = ScannerThread(self)
        self.scanner_thread.update_alert_box.connect(self.update_alert_box)
        self.scanner_thread.update_graph.connect(self.update_graph)
        self.start_button.clicked.connect(self.start_scanner_thread)
        self.stop_button.clicked.connect(self.stop_scanner_thread)
        self.stop_button.setEnabled(False)
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_scanner_thread)
        self.timer.setInterval(60000)

    def update_graph(self, ohlcv_dict, spikes_24h, spikes_1h):  # Lists as parameters
        self.graphWidget.clear()
        for symbol in spikes_24h:  # Loop through list
            ohlcv_df = ohlcv_dict.get(symbol, None)
            if ohlcv_df is not None:
                self.graphWidget.plot(ohlcv_df.index, ohlcv_df['volume'], pen=pg.mkPen(
                    color=(255, 0, 0), width=2), name=symbol)

        for symbol in spikes_1h:  # Loop through list
            ohlcv_df = ohlcv_dict.get(symbol, None)
            if ohlcv_df is not None:
                self.graphWidget.plot(ohlcv_df.index, ohlcv_df['volume'], pen=pg.mkPen(
                    color=(0, 255, 0), width=2), name=symbol)

    def start_scanner_thread(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.alert_box.append("Scanner started...")  # Changed to append
        self.scanner_thread.start()
        self.timer.start()

    def stop_scanner_thread(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.scanner_thread.quit()
        self.alert_box.setText("Scanner stopped.")
        self.timer.stop()

    def update_alert_box(self, text):
        self.alert_box.append(text)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
