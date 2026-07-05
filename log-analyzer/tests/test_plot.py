"""测试可视化模块"""

import pytest
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, '/Users/liuzimin/log-analyzer/src')

from log_analyzer.parser import LogLevel, LogEntry
from log_analyzer.plot import plot_level_distribution, plot_time_trend
from datetime import datetime


class TestPlotLevelDistribution:
    def test_plot_with_data(self):
        entries = [
            LogEntry(datetime.now(), LogLevel.INFO, "msg1", "raw1"),
            LogEntry(datetime.now(), LogLevel.INFO, "msg2", "raw2"),
            LogEntry(datetime.now(), LogLevel.ERROR, "msg3", "raw3"),
        ]

        # Mock plotext
        with patch('log_analyzer.plot.plt') as mock_plt:
            plot_level_distribution(entries, plot_type="bar", width=80, height=20)
            mock_plt.figure.assert_called_once()
            mock_plt.bar.assert_called_once()

    def test_plot_empty_data(self, capsys):
        with patch('log_analyzer.plot.plt') as mock_plt:
            plot_level_distribution([], plot_type="bar")
            # Should print error message
            captured = capsys.readouterr()
            assert "No data to plot" in captured.err

    def test_plot_pie_chart(self):
        entries = [
            LogEntry(datetime.now(), LogLevel.INFO, "msg1", "raw1"),
            LogEntry(datetime.now(), LogLevel.ERROR, "msg2", "raw2"),
        ]
        with patch('log_analyzer.plot.plt') as mock_plt:
            plot_level_distribution(entries, plot_type="pie", width=80, height=20)
            mock_plt.pie.assert_called_once()


class TestPlotTimeTrend:
    def test_plot_time_trend(self):
        entries = [
            LogEntry(datetime(2026, 6, 24, 10, 15, 32), LogLevel.INFO, "msg1", "raw1"),
            LogEntry(datetime(2026, 6, 24, 10, 20, 33), LogLevel.INFO, "msg2", "raw2"),
            LogEntry(datetime(2026, 6, 24, 11, 5, 34), LogLevel.ERROR, "msg3", "raw3"),
        ]
        with patch('log_analyzer.plot.plt') as mock_plt:
            plot_time_trend(entries, interval="hour", plot_type="line", width=80, height=20)
            mock_plt.figure.assert_called_once()
            mock_plt.plot.assert_called_once()

    def test_plot_time_trend_bar(self):
        entries = [
            LogEntry(datetime(2026, 6, 24, 10, 15, 32), LogLevel.INFO, "msg1", "raw1"),
        ]
        with patch('log_analyzer.plot.plt') as mock_plt:
            plot_time_trend(entries, interval="hour", plot_type="bar", width=80, height=20)
            mock_plt.bar.assert_called_once()
