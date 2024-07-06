"""
Indyfficient Auto-Clicker
Author: Andrew Polmans
Version: 1.0
Last Updated: July 5 2024

This script creates a GUI for an auto-clicker application using PyQt5.
It allows users to set click intervals, durations, types, and counts.

This software is intended for educational and personal use only.
Use responsibly and in compliance with all applicable laws and regulations.

This is free, open-source software. No warranty is provided.
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QButtonGroup, QGroupBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator, QIcon, QPixmap, QPainter, QColor
import pyautogui
import time
import keyboard
import traceback
import hashlib

def create_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setPen(QColor(0, 0, 0))
    painter.setBrush(QColor(0, 120, 215))  # A nice blue color
    painter.drawEllipse(2, 2, 60, 60)
    painter.setPen(QColor(255, 255, 255))
    painter.setFont(QFont('unispace', 35, QFont.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, 'I')
    painter.end()
    return QIcon(pixmap)

class ClickerThread(QThread):
    def __init__(self, interval, duration, click_type, click_count):
        super().__init__()
        self.interval = interval
        self.duration = duration
        self.click_type = click_type
        self.click_count = click_count
        self.running = False
        self.clicks_performed = 0

    def run(self):
        self.running = True
        self.clicks_performed = 0
        
        while self.running and (self.click_count == 0 or self.clicks_performed < self.click_count):
            if self.click_type == 'left':
                pyautogui.mouseDown(button='left')
                time.sleep(self.duration)
                pyautogui.mouseUp(button='left')
            else:
                pyautogui.mouseDown(button='right')
                time.sleep(self.duration)
                pyautogui.mouseUp(button='right')
            
            self.clicks_performed += 1
            if self.click_count > 0 and self.clicks_performed >= self.click_count:
                break
            
            time.sleep(max(0, self.interval - self.duration))

class AutoClicker(QWidget):
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.clicker_thread = None
        keyboard.on_press_key('f6', self.on_f6_press)
        self.error_signal.connect(self.show_error)

    def initUI(self):
        self.setWindowIcon(create_icon())
        layout = QVBoxLayout()

        self.error_label = QLabel('')
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)

        # Title
        title_label = QLabel('Indyfficient Auto-Clicker')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Interval
        interval_group = QGroupBox("Click Interval")
        interval_layout = QHBoxLayout()
        
        self.interval_hours = QLineEdit('0')
        self.interval_hours.setValidator(QIntValidator(0, 23))
        interval_layout.addWidget(QLabel('Hours:'))
        interval_layout.addWidget(self.interval_hours)
        
        self.interval_minutes = QLineEdit('0')
        self.interval_minutes.setValidator(QIntValidator(0, 59))
        interval_layout.addWidget(QLabel('Minutes:'))
        interval_layout.addWidget(self.interval_minutes)
        
        self.interval_seconds = QLineEdit('1')
        self.interval_seconds.setValidator(QIntValidator(0, 59))
        interval_layout.addWidget(QLabel('Seconds:'))
        interval_layout.addWidget(self.interval_seconds)
        
        self.interval_milliseconds = QLineEdit('0')
        self.interval_milliseconds.setValidator(QIntValidator(0, 999))
        interval_layout.addWidget(QLabel('Milliseconds:'))
        interval_layout.addWidget(self.interval_milliseconds)
        
        interval_group.setLayout(interval_layout)
        layout.addWidget(interval_group)

        # Duration
        duration_group = QGroupBox("Click Duration (should not exceed Click Interval)")
        duration_layout = QHBoxLayout()
        
        self.duration_hours = QLineEdit('0')
        self.duration_hours.setValidator(QIntValidator(0, 23))
        duration_layout.addWidget(QLabel('Hours:'))
        duration_layout.addWidget(self.duration_hours)
        
        self.duration_minutes = QLineEdit('0')
        self.duration_minutes.setValidator(QIntValidator(0, 59))
        duration_layout.addWidget(QLabel('Minutes:'))
        duration_layout.addWidget(self.duration_minutes)
        
        self.duration_seconds = QLineEdit('0')
        self.duration_seconds.setValidator(QIntValidator(0, 59))
        duration_layout.addWidget(QLabel('Seconds:'))
        duration_layout.addWidget(self.duration_seconds)
        
        self.duration_milliseconds = QLineEdit('100')
        self.duration_milliseconds.setValidator(QIntValidator(0, 999))
        duration_layout.addWidget(QLabel('Milliseconds:'))
        duration_layout.addWidget(self.duration_milliseconds)
        
        duration_group.setLayout(duration_layout)
        layout.addWidget(duration_group)

        # Click Type and Click Count
        type_count_layout = QHBoxLayout()

        # Click Type
        click_type_group = QGroupBox("Click Type")
        click_type_layout = QVBoxLayout()
        self.left_click_radio = QRadioButton('Left Click')
        self.right_click_radio = QRadioButton('Right Click')
        self.click_type_group = QButtonGroup()
        self.click_type_group.addButton(self.left_click_radio)
        self.click_type_group.addButton(self.right_click_radio)
        self.left_click_radio.setChecked(True)
        click_type_layout.addWidget(self.left_click_radio)
        click_type_layout.addWidget(self.right_click_radio)
        click_type_group.setLayout(click_type_layout)
        type_count_layout.addWidget(click_type_group)

        # Click Count
        count_group = QGroupBox("Click Count")
        count_layout = QVBoxLayout()
        
        self.click_until_stopped_radio = QRadioButton('Click until Stopped')
        self.set_click_count_radio = QRadioButton('Set Click Count')
        self.click_count_group = QButtonGroup()
        self.click_count_group.addButton(self.click_until_stopped_radio)
        self.click_count_group.addButton(self.set_click_count_radio)
        self.click_until_stopped_radio.setChecked(True)
        
        count_layout.addWidget(self.click_until_stopped_radio)
        count_layout.addWidget(self.set_click_count_radio)
        
        self.count_input = QLineEdit('1')
        self.count_input.setValidator(QIntValidator(1, 1000000))
        self.count_input.setEnabled(False)
        count_input_layout = QHBoxLayout()
        count_input_layout.addWidget(QLabel('Number of Clicks:'))
        count_input_layout.addWidget(self.count_input)
        count_layout.addLayout(count_input_layout)
        
        count_group.setLayout(count_layout)
        type_count_layout.addWidget(count_group)

        layout.addLayout(type_count_layout)

        # Connect radio buttons to enable/disable count input
        self.click_until_stopped_radio.toggled.connect(self.toggle_count_input)
        self.set_click_count_radio.toggled.connect(self.toggle_count_input)

        # Status
        self.status_label = QLabel('Press F6 to start/stop')
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.setWindowTitle('Indyfficient Auto-Clicker')
        self.setGeometry(300, 300, 500, 400)

    def toggle_count_input(self):
        self.count_input.setEnabled(self.set_click_count_radio.isChecked())

    def on_f6_press(self, e):
        self.toggle_clicker()

    def toggle_clicker(self):
        if self.clicker_thread and self.clicker_thread.running:
            self.stop_clicker()
        else:
            self.start_clicker()

    def calculate_time(self, hours, minutes, seconds, milliseconds):
        return (int(hours) * 3600 +
                int(minutes) * 60 +
                int(seconds) +
                int(milliseconds) / 1000)

    def start_clicker(self):
        try:
            print("Starting clicker...")  # Debug print
            interval = self.calculate_time(self.interval_hours.text(),
                                           self.interval_minutes.text(),
                                           self.interval_seconds.text(),
                                           self.interval_milliseconds.text())
            
            duration = self.calculate_time(self.duration_hours.text(),
                                           self.duration_minutes.text(),
                                           self.duration_seconds.text(),
                                           self.duration_milliseconds.text())
            
            print(f"Interval: {interval}, Duration: {duration}")  # Debug print

            if duration > interval:
                self.show_error("Duration cannot exceed interval. Please adjust your input.")
                return

            if self.click_until_stopped_radio.isChecked():
                click_count = 0
            else:
                click_count = int(self.count_input.text())

            click_type = 'left' if self.left_click_radio.isChecked() else 'right'

            print(f"Click count: {click_count}, Click type: {click_type}")  # Debug print

            self.clicker_thread = ClickerThread(interval, duration, click_type, click_count)
            self.clicker_thread.start()
            self.status_label.setText('Auto Clicker is running. Press F6 to stop.')
            self.error_label.setText('')  # Clear any previous error messages
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}\nPlease check your inputs and try again."
            print(f"Error in start_clicker: {error_msg}")  # Debug print
            print(traceback.format_exc())  # Print full traceback
            self.error_signal.emit(error_msg)

    def stop_clicker(self):
        try:
            print("Stopping clicker...")  # Debug print
            if self.clicker_thread:
                self.clicker_thread.running = False
                self.clicker_thread.wait()
                self.status_label.setText('Auto Clicker stopped. Press F6 to start.')
                self.error_label.setText('')  # Clear any previous error messages
        except Exception as e:
            error_msg = f"An error occurred while stopping: {str(e)}"
            print(f"Error in stop_clicker: {error_msg}")  # Debug print
            print(traceback.format_exc())  # Print full traceback
            self.error_signal.emit(error_msg)

    def closeEvent(self, event):
        try:
            print("Closing application...")  # Debug print
            self.stop_clicker()
            keyboard.unhook_all()
            event.accept()
        except Exception as e:
            error_msg = f"An error occurred while closing: {str(e)}"
            print(f"Error in closeEvent: {error_msg}")  # Debug print
            print(traceback.format_exc())  # Print full traceback
            event.accept()  # Force close even if an error occurs

    def show_error(self, message):
        print(f"Showing error: {message}")  # Debug print
        self.error_label.setText(message)
        self.status_label.setText('Error occurred. Check inputs and try again.')

# Simple function to generate a "signature" for the script
def generate_signature():
    try:
        # When running as a script
        with open(__file__, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        # When running as a PyInstaller bundle
        try:
            with open(sys.executable, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            return f"Unable to generate signature: {str(e)}"

if __name__ == '__main__':
    # Print the script's "signature"
    print(f"Script Signature: {generate_signature()}")
    app = QApplication(sys.argv)
    ex = AutoClicker()
    ex.show()
    sys.exit(app.exec_())
