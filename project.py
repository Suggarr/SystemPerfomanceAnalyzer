# -*- coding: utf-8 -*-
import socket
import sys
import psutil
import time
import subprocess
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QWidget, QDialog, QTabWidget
)
from os import popen
from PySide6.QtGui import QAction, QIcon
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class CPUResourceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.cpu_usage = [0] * 60  # 60 последних секунд

        # CPU Info Labels
        self.model_label = QLabel("Модель: ")
        self.cores_label = QLabel("Ядра: ")
        self.virtualization_label = QLabel("Виртуализация: ")
        self.sockets_label = QLabel("Сокеты: ")
        self.l1d_label = QLabel("L1d Cache: ")
        self.l1i_label = QLabel("L1i Cache: ")
        self.l2_label = QLabel("L2 Cache: ")
        self.l3_label = QLabel("L3 Cache: ")

        self.layout.addWidget(self.model_label)
        self.layout.addWidget(self.cores_label)
        self.layout.addWidget(self.virtualization_label)
        self.layout.addWidget(self.sockets_label)
        self.layout.addWidget(self.l1d_label)
        self.layout.addWidget(self.l1i_label)
        self.layout.addWidget(self.l2_label)
        self.layout.addWidget(self.l3_label)

        # График
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_cpu_usage)
        self.timer.start(1000)

        self.update_cpu_info()

    def update_cpu_info(self):
        cpu_count = psutil.cpu_count(logical=False)
        model_name = "Не удалось получить модель"
        sockets = "Неизвестно"
        virtualization = "Не поддерживается"
        l1d_cache = l1i_cache = l2_cache = l3_cache = "Нет данных"

        try:
            output = subprocess.check_output(['lscpu'], universal_newlines=True, env={'LC_ALL': 'C'})
            for line in output.splitlines():
                if "Model name:" in line:
                    model_name = line.split(":")[1].strip()
                elif "Socket(s):" in line:
                    sockets = line.split(":")[1].strip()
                elif "Virtualization type:" in line:
                    virtualization = line.split(":")[1].strip()
                elif "L1d cache:" in line:
                    l1d_cache = line.split(":")[1].strip()
                elif "L1i cache:" in line:
                    l1i_cache = line.split(":")[1].strip()
                elif "L2 cache:" in line:
                    l2_cache = line.split(":")[1].strip()
                elif "L3 cache:" in line:
                    l3_cache = line.split(":")[1].strip()
        except Exception as e:
            model_name = f"Ошибка: {e}"

        self.model_label.setText(f"Модель: {model_name}")
        self.cores_label.setText(f"Количество ядер: {cpu_count}")
        self.virtualization_label.setText(f"Тип виртуализации: {virtualization}")
        self.sockets_label.setText(f"Сокеты: {sockets}")
        self.l1d_label.setText(f"Кэш L1d: {l1d_cache}")
        self.l1i_label.setText(f"Кэш L1i: {l1i_cache}")
        self.l2_label.setText(f"Кэш L2: {l2_cache}")
        self.l3_label.setText(f"Кэш L3: {l3_cache}")

    def update_cpu_usage(self):
        usage = psutil.cpu_percent(interval=None)

        # Удаляем старое значение, добавляем новое
        self.cpu_usage.pop(0)
        self.cpu_usage.append(usage)

        self.update_graph()

    def update_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')

        ax.fill_between(range(len(self.cpu_usage)), self.cpu_usage, color='lightgreen', alpha=0.5)
        ax.plot(self.cpu_usage, label='Использование CPU (%)', color='green')

        ax.set_ylim(0, 100)
        ax.set_xlim(0, len(self.cpu_usage) - 1)
        ax.set_title('Использование CPU')
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Использование (%)')
        ax.set_xticks(range(0, len(self.cpu_usage), 10))
        ax.set_xticklabels(["1 мин", "50 сек", "40 сек", "30 сек", "20 сек", "10 сек"])
        ax.legend()
        ax.grid(True)
        self.canvas.draw()


class MemoryResourceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.memory_usage = [0] * 60  # храним последние 60 точек
        self.time_labels = [str(i) for i in range(60)]  # метки времени для оси X

        self.memory_info_label = QLabel("Информация о памяти:")
        self.layout.addWidget(self.memory_info_label)

        self.total_label = QLabel("Всего: ")
        self.used_label = QLabel("Используется: ")
        self.available_label = QLabel("Доступно: ")
        self.cached_label = QLabel("Кешировано: ")

        self.layout.addWidget(self.total_label)
        self.layout.addWidget(self.used_label)
        self.layout.addWidget(self.available_label)
        self.layout.addWidget(self.cached_label)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_memory_info)
        self.timer.start(1000)

        self.update_memory_info()

    def update_memory_info(self):
        memory = psutil.virtual_memory()

        # Обновляем данные: удаляем старую точку, добавляем новую
        self.memory_usage.pop(0)
        self.memory_usage.append(memory.percent)

        self.total_label.setText(f"Всего: {memory.total / (1024 ** 2):.2f} MB")
        self.used_label.setText(f"Используется: {memory.used / (1024 ** 2):.2f} MB")
        self.available_label.setText(f"Доступно: {memory.available / (1024 ** 2):.2f} MB")
        self.cached_label.setText(f"Кешировано: {memory.cached / (1024 ** 2):.2f} MB")

        self.update_graph()

    def update_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')

        ax.fill_between(range(len(self.memory_usage)), self.memory_usage, color='lightblue', alpha=0.5)
        ax.plot(self.memory_usage, label='Использование памяти (%)', color='blue')

        ax.set_ylim(0, 100)
        ax.set_xlim(0, len(self.memory_usage) - 1)
        ax.set_title('Использование памяти')
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Использование (%)')
        ax.set_xticks(range(0, len(self.memory_usage), 10))
        ax.set_xticklabels(["1 мин", "50 сек", "40 сек", "30 сек", "20 сек", "10 сек"])
        ax.legend()
        ax.grid(True)
        self.canvas.draw()


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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(700, 600)
        Dialog.setSizeGripEnabled(True)
        Dialog.setModal(False)

        self.layout = QVBoxLayout(Dialog)
        self.tabWidget = QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Основные вкладки
        self.create_process_tab()
        self.create_performance_tabs()

        # Добавляем главный QTabWidget в диалог
        self.layout.addWidget(self.tabWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def create_process_tab(self):
        """Создание вкладки 'Процессы'."""
        self.process_tab = ProcessTab()
        self.tabWidget.addTab(self.process_tab, "Процессы")

    def create_performance_tabs(self):
        """Создание вкладок для производительности."""
        self.performance_tab = QTabWidget()
        self.performance_tab.addTab(CPUResourceTab(), "CPU")
        self.performance_tab.addTab(MemoryResourceTab(), "Память")
        self.performance_tab.addTab(DiskResourceTab(), "Диск")

        # Добавляем вкладки сети внутри вкладки 'Производительность'
        self.add_network_tabs()

        self.tabWidget.addTab(self.performance_tab, "Производительность")

    def add_network_tabs(self):
        """Добавление вкладок для сетевых адаптеров."""
        active_adapters = [
            name for name, stats in psutil.net_if_stats().items() if name != "lo" and stats.isup
        ]

        if not active_adapters:
            print("Net: No active network adapters found")
            return

        for adapter_name in active_adapters:
            network_tab = NetworkResourceTab(parent=self.performance_tab)
            network_tab.set_interface_name(adapter_name)  # Устанавливаем имя через метод
            self.performance_tab.addTab(network_tab, f"Сеть ({adapter_name})")

    def retranslateUi(self, Dialog):
        """Установка заголовка окна."""
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Resource Monitor"))


class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.selected_pid = None 

        self.setup_table()
        self.update_processes()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_processes)
        self.timer.start(1500)

        self.selected_pid = None  # Запоминаем PID выделенного процесса

    def setup_table(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Process", "PID", "CPU Usage (%)", "Memory Usage (%)", "User"])
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 150)

        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.itemSelectionChanged.connect(self.handle_selection_change)  # Событие выбора строки

    def handle_selection_change(self):
        """Обрабатывает изменение выделения строки."""
        current_row = self.table.currentRow()
        if current_row != -1:  # Проверяем, что строка выделена
            pid_item = self.table.item(current_row, 1)  # PID находится во втором столбце
            if pid_item:
                self.selected_pid = int(pid_item.text())  # Сохраняем PID выбранного процесса
        else:
            self.selected_pid = None  # Если ничего не выделено, сбрасываем PID

    def show_context_menu(self, pos):
        """Отображает контекстное меню."""
        if self.selected_pid is not None:  # Проверяем, что выбран процесс
            menu = QMenu(self)
            kill_action = QAction("Завершить процесс", self)
            kill_action.triggered.connect(self.kill_selected_process)
            menu.addAction(kill_action)
            menu.exec_(self.table.viewport().mapToGlobal(pos))

    def kill_selected_process(self):
        """Завершает выбранный процесс с подтверждением."""
        if self.selected_pid is not None:
            # Получим имя процесса для показа в окне
            process_name = None
            try:
                process_name = psutil.Process(self.selected_pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Неизвестный процесс"
            
            # Окно подтверждения
            confirmation = QtWidgets.QMessageBox()
            confirmation.setIcon(QtWidgets.QMessageBox.Warning)
            confirmation.setWindowTitle("Подтверждение завершения")
            confirmation.setText(f"Вы действительно хотите завершить процесс `{process_name}` (PID: {self.selected_pid})?")
            confirmation.setInformativeText("Внимание: завершение процесса может привести к нестабильной работе системы.")
            confirmation.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            confirmation.setDefaultButton(QtWidgets.QMessageBox.No)
            
            # Если пользователь выбрал "Да", завершаем процесс
            if confirmation.exec() == QtWidgets.QMessageBox.Yes:
                try:
                    p = psutil.Process(self.selected_pid)
                    p.terminate()
                    self.update_processes()  # Обновляем таблицу после завершения процесса
                except Exception as e:
                    error_message = QtWidgets.QMessageBox()
                    error_message.setIcon(QtWidgets.QMessageBox.Critical)
                    error_message.setWindowTitle("Ошибка")
                    error_message.setText(f"Не удалось завершить процесс `{process_name}` (PID: {self.selected_pid}).")
                    error_message.setInformativeText(str(e))
                    error_message.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    error_message.exec()

    def update_processes(self):
        """Обновляет список процессов в таблице."""
        # Сохраняем текущий выбранный PID (если есть)
        previously_selected_pid = self.selected_pid

        self.table.setRowCount(0)
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            try:
                processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda p: p.cpu_percent(), reverse=True)

        for proc in processes:
            try:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                # Заполняем строку
                self.table.setItem(row_position, 0, QTableWidgetItem(proc.info['name']))
                self.table.setItem(row_position, 1, QTableWidgetItem(str(proc.info['pid'])))
                logical_cpus = psutil.cpu_count(logical=True)
                normalized_cpu = proc.info['cpu_percent'] / logical_cpus
                self.table.setItem(row_position, 2, QTableWidgetItem(f"{normalized_cpu:.2f}%"))
                self.table.setItem(row_position, 3, QTableWidgetItem(f"{proc.info['memory_percent']:.2f}%"))
                self.table.setItem(row_position, 4, QTableWidgetItem(proc.info['username']))

                # Восстанавливаем выделение, если PID совпадает
                if proc.info['pid'] == previously_selected_pid:
                    self.table.selectRow(row_position)  # Выделяем строку
                    self.selected_pid = previously_selected_pid  # Сохраняем PID

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

class DiskResourceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.disk_list = []
        self.disk_size = []
        self.disk_type = []
        self.disk_active_array = []
        self.disk_read_array = []
        self.disk_write_array = []
        self.num_of_disks = 0
        self.disk_state1 = []
        self.disk_state2 = []
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(QLabel("Информация о диске:"))
        self.disk_name_label = QLabel("Название диска: ")
        self.layout.addWidget(self.disk_name_label)
        self.disk_capacity_label = QLabel("Емкость: ")
        self.layout.addWidget(self.disk_capacity_label)
        self.disk_type_label = QLabel("Тип диска: ")
        self.layout.addWidget(self.disk_type_label)
        self.layout.addWidget(self.canvas)

        self.timer = QTimer()
        self.timer.timeout.connect(self.disk_tab_update)
        self.timer.start(1000)  # Update every 1000 ms

        self.disk_init()  # Initialize disks

    def disk_init(self):
        """Initialization of the Disk Components."""
        # Getting the name and size of the disks using shell command
        try:
            p = popen('lsblk -d | grep -e ^NAME -e disk')
            partitions = p.readlines()
            p.close()
            for parts in partitions:
                tempparts = parts.split()
                print(tempparts)
                if 'NAME' not in tempparts[0] and 'zram' not in tempparts[0]:
                    self.disk_list.append(tempparts[0])
                    self.disk_size.append(tempparts[3])
                    # Determine disk type
                    if 'sd' in tempparts[0]:  # Simplified check for SSD
                        self.disk_type.append('SSD' if 'SSD' in tempparts else 'HDD')

            self.num_of_disks = len(self.disk_list)
            self.disk_active_array = [[0] * 60 for _ in range(self.num_of_disks)]
            self.disk_read_array = [[0] * 60 for _ in range(self.num_of_disks)]
            self.disk_write_array = [[0] * 60 for _ in range(self.num_of_disks)]
            self.disk_state1 = [None] * self.num_of_disks

            # Get initial disk I/O state
            disk_temp = psutil.disk_io_counters(perdisk=True)
            for i, disk in enumerate(self.disk_list):
                self.disk_state1[i] = disk_temp[disk]

        except Exception as e:
            print(f"Failed to get Disks: {e}")

    def disk_tab_update(self):
        """Function to periodically update DISKs statistics."""
        disk_temp = psutil.disk_io_counters(perdisk=True)

        # Updating disk statistics
        for i in range(self.num_of_disks):
            try:
                current_disk = self.disk_list[i]
                self.disk_state2 = disk_temp[current_disk]

                # Calculate differences
                disk_diff = [
                    self.disk_state2.read_bytes - self.disk_state1[i].read_bytes,
                    self.disk_state2.write_bytes - self.disk_state1[i].write_bytes
                ]

                # Update active utilization percentage
                active_percentage = (disk_diff[0] + disk_diff[1]) / 1024  # KB/s total read + write
                if active_percentage > 100:
                    active_percentage = 100

                # Update labels
                self.disk_name_label.setText(f"Название диска: {current_disk}")
                self.disk_capacity_label.setText(f"Емкость: {self.disk_size[i]}")
                self.disk_type_label.setText(f"Тип диска: {'SSD' if active_percentage < 100 else 'HDD'}")
                self.disk_active_array[i].pop(0)
                self.disk_active_array[i].append(active_percentage)

                self.disk_read_array[i].pop(0)
                self.disk_read_array[i].append(disk_diff[0] / 1024)  # Convert to KB/s

                self.disk_write_array[i].pop(0)
                self.disk_write_array[i].append(disk_diff[1] / 1024)

                # Update graph
                self.update_graph(i)

                # Update previous state
                self.disk_state1[i] = self.disk_state2

            except Exception as e:
                print(f'Error updating disk {current_disk}: {e}')

    def update_graph(self, index):
        """Обновление графика для указанного диска."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')

        ax.fill_between(range(len(self.disk_read_array[index])), self.disk_read_array[index], color='lightgreen', alpha=0.5, label='Чтение (KB/s)')
        ax.plot(self.disk_read_array[index], label='Чтение (KB/s)', color='green')
        ax.plot(self.disk_write_array[index], label='Запись (KB/s)', color='red')

        # Задание пределов Y оси для корректной визуализации
        ax.set_ylim(0, max(max(self.disk_read_array[index], default=0), max(self.disk_write_array[index], default=0)) * 1.1)
        ax.set_xlim(0, len(self.disk_read_array[index]) - 1)

        # Настройка оси X: справа налево (от старых к новым)
        ax.set_xticks(range(0, 60, 10))
        ax.set_xticklabels(["1 мин", "50 сек", "40 сек", "30 сек", "20 сек", "10 сек"])
        # Настройка заголовков и легенды
        ax.set_title('Скорость чтения и записи диска')
        ax.set_xlabel('Время (секунды)')
        ax.set_ylabel('Скорость (KB/s)')
        ax.legend()
        ax.grid(True)

        # Отображение обновленного графика
        self.canvas.draw()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.showMaximized()  
    sys.exit(app.exec())