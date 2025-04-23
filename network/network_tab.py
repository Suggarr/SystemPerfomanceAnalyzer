import psutil
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QWidget, QDialog, QTabWidget
)
import time
import socket
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class NetworkResourceTab(QWidget):
    def __init__(self, parent=None, interface_name=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.interface_name = interface_name
        self.netReceiveArray = [0] * 60  # История скоростей получения (60 точек для 6 колонок)
        self.netSendArray = [0] * 60  # История скоростей отправки

        # Таймер для обновления данных
        self.timer = QTimer(self)
        self.net_state1 = None
        self.net_state2 = None
        self.t1 = None
        self.t2 = None

        self.setup_ui()
        self.initialize_network_data()

    def set_interface_name(self, interface_name):
        """Метод для установки имени интерфейса."""
        self.interface_name = interface_name
        self.adapter_name_label.setText(f"Имя адаптера: {self.interface_name}") 
        self.initialize_network_data()

    def setup_ui(self):
        """Установка базовых элементов интерфейса."""
        self.adapter_name_label = QLabel("Имя адаптера: Неизвестно")
        self.adapter_type_label = QLabel("Тип адаптера: Неизвестно")
        self.ipv4_label = QLabel("IPv4: Неизвестно")
        self.ipv6_label = QLabel("IPv6: Неизвестно")
        self.speed_send_label = QLabel("Скорость отправки: 0 КБ/с")
        self.speed_recv_label = QLabel("Скорость получения: 0 КБ/с")

        # Добавляем элементы в макет
        self.layout.addWidget(self.adapter_name_label)
        self.layout.addWidget(self.adapter_type_label)
        self.layout.addWidget(self.ipv4_label)
        self.layout.addWidget(self.ipv6_label)
        self.layout.addWidget(self.speed_send_label)
        self.layout.addWidget(self.speed_recv_label)

        # Настройка графика
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def initialize_network_data(self):
        """Инициализация сетевых данных для выбранного интерфейса."""
        if not self.interface_name:
            return

        # Обновляем информацию об адаптере
        self.update_adapter_info()

        # Инициализация для таймера
        self.net_state1 = psutil.net_io_counters(pernic=True).get(self.interface_name, None)
        self.t1 = time.time()
        self.timer.timeout.connect(self.update_network_info)
        self.timer.start(1500)

    def update_adapter_info(self):
        """Обновление информации об адаптере."""
        stats = psutil.net_if_stats().get(self.interface_name, None)

        # Тип адаптера
        if stats:
            if "eth" in self.interface_name.lower() or "en" in self.interface_name.lower():
                self.adapter_type_label.setText("Тип адаптера: Ethernet")
            elif "wlan" in self.interface_name.lower() or "wi-fi" in self.interface_name.lower():
                self.adapter_type_label.setText("Тип адаптера: WiFi")
            else:
                self.adapter_type_label.setText("Тип адаптера: Неизвестно")

        # Адреса IPv4 и IPv6
        addresses = psutil.net_if_addrs().get(self.interface_name, [])
        ipv4 = next((addr.address for addr in addresses if addr.family == socket.AF_INET), "Неизвестно")
        ipv6 = next((addr.address for addr in addresses if addr.family == socket.AF_INET6), "Неизвестно")
        self.ipv4_label.setText(f"IPv4: {ipv4}")
        self.ipv6_label.setText(f"IPv6: {ipv6}")

    def update_network_info(self):
        """Обновление информации о сетевых скоростях."""
        if not self.interface_name:
            return

        self.net_state2 = psutil.net_io_counters(pernic=True).get(self.interface_name, None)
        self.t2 = time.time()

        if self.net_state1 and self.net_state2:
            time_diff = self.t2 - self.t1
            send_speed = (self.net_state2.bytes_sent - self.net_state1.bytes_sent) / time_diff / 1024  # КБ/с
            recv_speed = (self.net_state2.bytes_recv - self.net_state1.bytes_recv) / time_diff / 1024  # КБ/с

            # Обновление данных для графика
            self.netSendArray.pop(0)
            self.netSendArray.append(send_speed)

            self.netReceiveArray.pop(0)
            self.netReceiveArray.append(recv_speed)

            # Обновление меток
            self.speed_send_label.setText(f"Скорость отправки: {send_speed:.2f} КБ/с")
            self.speed_recv_label.setText(f"Скорость получения: {recv_speed:.2f} КБ/с")

            self.update_graph()

        self.net_state1 = self.net_state2
        self.t1 = self.t2

    def update_graph(self):
        """Обновление графика сетевых скоростей."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')

        # Графики для отправки и получения данных
        ax.plot(self.netSendArray, label="Отправка (КБ/с)", color="blue", linestyle="--")
        ax.plot(self.netReceiveArray, label="Получение (КБ/с)", color="green", linestyle="-")

        ax.fill_between(range(len(self.netSendArray)), self.netSendArray, color="blue", alpha=0.3)
        ax.fill_between(range(len(self.netReceiveArray)), self.netReceiveArray, color="green", alpha=0.3)

        # Ограничения и сетка
        max_speed = max(max(self.netSendArray), max(self.netReceiveArray), 1)
        ax.set_ylim(0, max_speed * 1.2)
        ax.set_xlim(0, len(self.netSendArray) - 1)

        # Настройка оси X: справа налево (от старых к новым)
        ax.set_xticks(range(0, 60, 10))
        ax.set_xticklabels(["1 мин", "50 сек", "40 сек", "30 сек", "20 сек", "10 сек"])

        # Подписи
        ax.set_title(f"Сетевой трафик — {self.interface_name}")
        ax.set_xlabel("Время (сек)")
        ax.set_ylabel("Скорость (КБ/с)")

        ax.legend()
        ax.grid(True)
        self.canvas.draw()