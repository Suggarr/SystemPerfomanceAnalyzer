# -*- coding: utf-8 -*-

import sys
import psutil
import platform
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QWidget, QDialog, QTabWidget
)
from gi.repository import Gio
from os import popen
from PySide6.QtGui import QAction, QIcon
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

gio_apps = Gio.AppInfo.get_all()
theme_icon_list = ['utilities-system-monitor', 'application-x-executable', 'system-run', 'system-task']

class CPUResourceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.cpu_usage = []

        # CPU Info Labels
        self.model_label = QLabel("Модель: ")
        self.speed_label = QLabel("Макс. скорость: ")
        self.cores_label = QLabel("Ядра: ")
        self.threads_label = QLabel("Логические процессоры: ")
        self.virtualization_label = QLabel("Виртуализация: ")
        self.cache_label = QLabel("Кэш: ")
        self.temp_label = QLabel("Температура: ")

        self.layout.addWidget(self.model_label)
        self.layout.addWidget(self.speed_label)
        self.layout.addWidget(self.cores_label)
        self.layout.addWidget(self.threads_label)
        self.layout.addWidget(self.virtualization_label)
        # self.layout.addWidget(self.cache_label)
        # self.layout.addWidget(self.temp_label)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_cpu_usage)
        self.timer.start(500)

        self.update_cpu_info()  # Получаем информацию о процессоре

    def update_cpu_info(self):
        # Получаем информацию о процессоре
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count(logical=False)
        logical_count = psutil.cpu_count(logical=True)

        # Получение модели процессора
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if "model name" in line:
                        model_name = line.split(':')[1].strip()
                        break
        except:
            model_name = "Не удалось получить модель"

        # Проверка поддержки виртуализации
        virtualization = "Не поддерживается"
        try:
            with open('/proc/cpuinfo', 'r') as f:
                if "vmx" in f.read() or "svm" in f.read():
                    virtualization = "Поддерживается"
        except:
            pass

        self.model_label.setText(f"Модель: {model_name}")
        self.speed_label.setText(f"Макс. скорость: {cpu_freq.max} GHz")
        self.cores_label.setText(f"Ядра: {cpu_count}")
        self.threads_label.setText(f"Логические процессоры: {logical_count}")
        self.virtualization_label.setText(f"Виртуализация: {virtualization}")

    def update_cpu_usage(self):
        usage = psutil.cpu_percent(interval=None)
        self.cpu_usage.append(usage)

        if len(self.cpu_usage) > 20:
            self.cpu_usage.pop(0)

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.fill_between(range(len(self.cpu_usage)), self.cpu_usage, color='blue', alpha=0.5)
        ax.plot(self.cpu_usage, label='CPU Usage (%)', color='blue')
        ax.set_ylim(0, 100)
        ax.set_title('Использование CPU со временем')
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Использование (%)')
        ax.legend()
        ax.grid(True)
        self.canvas.draw()


class MemoryResourceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.memory_usage = []
        self.time_points = []  # Track time points for the x-axis

        # Текстовые поля для информации о памяти
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
        self.timer.start(500)

        self.update_memory_info()  # Получаем информацию о памяти

    def update_memory_info(self):
        memory = psutil.virtual_memory()
        self.memory_usage.append(memory.percent)
        self.time_points.append(len(self.memory_usage) * 0.5)  # Increment time by 0.5 seconds

        # Обновляем текстовые поля
        self.total_label.setText(f"Всего: {memory.total / (1024 ** 2):.2f} MB")
        self.used_label.setText(f"Используется: {memory.used / (1024 ** 2):.2f} MB")
        self.available_label.setText(f"Доступно: {memory.available / (1024 ** 2):.2f} MB")
        self.cached_label.setText(f"Кешировано: {memory.cached / (1024 ** 2):.2f} MB")

        self.update_graph()

    def update_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')  # Устанавливаем цвет фона графика
        ax.fill_between(self.time_points, self.memory_usage, color='lightblue', alpha=0.5)
        ax.plot(self.time_points, self.memory_usage, label='Использование памяти (%)', color='lightblue')
        ax.set_ylim(0, 100)
        ax.set_title('Использование памяти со временем')
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Использование (%)')
        ax.legend()
        ax.grid(True)  # Включаем сетку
        self.canvas.draw()


class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.setup_table()
        self.update_processes()

        # Timer to update processes periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_processes)
        self.timer.start(1500)  # Update every 1 second

    def setup_table(self):
        self.table.setColumnCount(5)  # We now have 5 columns
        self.table.setHorizontalHeaderLabels(["Process", "PID", "CPU Usage (%)", "Memory Usage (%)", "User"])
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setColumnWidth(0, 180)  # Width for icon and name
        self.table.setColumnWidth(1, 80)   # Width for PID
        self.table.setColumnWidth(2, 150)  # Width for CPU Usage
        self.table.setColumnWidth(3, 150)  # Width for Memory Usage
        self.table.setColumnWidth(4, 150)  # Width for User

        # Set the selection behavior to select full rows
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if item:
            menu = QMenu(self)
            kill_action = QAction("Завершить процесс", self)
            kill_action.triggered.connect(lambda: self.kill_process(item))
            menu.addAction(kill_action)
            menu.exec_(self.table.viewport().mapToGlobal(pos))

    def kill_process(self, item):
        pid = int(self.table.item(item.row(), 1).text())
        try:
            p = psutil.Process(pid)
            p.terminate()  # Or use p.kill() for forced termination
            self.update_processes()  # Refresh the table
        except Exception as e:
            print(f"Ошибка завершения процесса {pid}: {e}")
    
    def update_processes(self):
        self.table.setRowCount(0)
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            try:
                processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort processes by CPU usage in descending order
        processes.sort(key=lambda p: p.cpu_percent(), reverse=True)

        for proc in processes:
            try:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                # Retrieve icon and process name
                icon = self.get_process_icon(proc)
                icon_item = QTableWidgetItem(proc.info['name'])
                icon_item.setIcon(icon)  # Set the icon
                icon_item.setFlags(Qt.ItemIsEnabled)  # Make the icon item non-editable
                self.table.setItem(row_position, 0, icon_item)

                self.table.setItem(row_position, 1, QTableWidgetItem(str(proc.info['pid'])))
                logical_cpus = psutil.cpu_count(logical=True)
                normalized_cpu = proc.info['cpu_percent'] / logical_cpus
                self.table.setItem(row_position, 2, QTableWidgetItem(f"{normalized_cpu:.2f}%"))
                self.table.setItem(row_position, 3, QTableWidgetItem(f"{proc.info['memory_percent']:.2f}%"))
                self.table.setItem(row_position, 4, QTableWidgetItem(proc.info['username']))

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def get_process_icon(self, process):
        """Retrieve the icon for a given process."""
        pname = process.name().lower()  # Приводим имя процесса к нижнему регистру
        default_icon = QIcon.fromTheme('application-x-executable')  # Иконка по умолчанию

        # Check against known applications in gio
        for app in gio_apps:
            app_name = app.get_display_name().lower()
            gicon = app.get_icon()

            if gicon and pname in app_name:
                return QIcon.fromTheme(app.get_id())  # Возвращаем иконку приложения

        # Check against theme icons
        for icon in theme_icon_list:
            if pname in icon.lower():  # Сравниваем название процесса с темами иконок
                return QIcon.fromTheme(icon)

        # Return default icon if no match was found
        return default_icon

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(700, 600)  # Increased size for the new tab
        Dialog.setSizeGripEnabled(True)
        Dialog.setModal(False)

        self.layout = QVBoxLayout(Dialog)
        self.tabWidget = QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Create tabs
        self.process_tab = ProcessTab()
        self.tabWidget.addTab(self.process_tab, "Процессы")

        self.performance_tab = QTabWidget()
        self.performance_tab.addTab(CPUResourceTab(), "CPU")
        self.performance_tab.addTab(MemoryResourceTab(), "Память")
        self.performance_tab.addTab(DiskResourceTab(), "Диск")  # Add new DiskResourceTab

        self.tabWidget.addTab(self.performance_tab, "Производительность")

        self.layout.addWidget(self.tabWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Resource Monitor"))

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
        self.timer.start(100)  # Update every 100 ms

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
                if 'NAME' not in tempparts[0] and 'zram' not in tempparts[0]:
                    self.disk_list.append(tempparts[0])
                    self.disk_size.append(tempparts[3])
                    # Determine disk type
                    if 'sd' in tempparts[0]:  # Simplified check for SSD
                        self.disk_type.append('SSD' if 'SSD' in tempparts else 'HDD')

            self.num_of_disks = len(self.disk_list)
            self.disk_active_array = [[0] * 100 for _ in range(self.num_of_disks)]
            self.disk_read_array = [[0] * 100 for _ in range(self.num_of_disks)]
            self.disk_write_array = [[0] * 100 for _ in range(self.num_of_disks)]
            self.disk_state1 = [None] * self.num_of_disks

            # Get initial disk I/O state
            disk_temp = psutil.disk_io_counters(perdisk=True)
            for i, disk in enumerate(self.disk_list):
                self.disk_state1[i] = disk_temp[disk]

        except Exception as e:
            print(f"Failed to get Disks: {e}")

    def disk_tab_update(self):
        """Function to periodically update DISKs statistics."""
        disk_usage = psutil.disk_usage('/')
        disk_temp = psutil.disk_io_counters(perdisk=True)

        # Updating disk statistics
        for i in range(self.num_of_disks):
            try:
                current_disk = self.disk_list[i]
                self.disk_state2 = disk_temp[current_disk]

                # Calculate differences
                disk_diff = [
                    self.disk_state2.read_bytes - self.disk_state1[i].read_bytes,
                    self.disk_state2.write_bytes - self.disk_state1[i].write_bytes,
                    self.disk_state2.busy_time - self.disk_state1[i].busy_time
                ]

                # Update active utilization percentage
                active_percentage = int(disk_diff[2] / (0.1 * 100))  # Assuming 100 ms intervals
                if active_percentage > 100:
                    active_percentage = 100

                # Update labels
                self.disk_name_label.setText(f"Название диска: {current_disk}")
                self.disk_capacity_label.setText(f"Емкость: {self.disk_size[i]}")
                self.disk_type_label.setText(f"Тип диска: {'SSD' if disk_usage.total < 1e12 else 'HDD'}")
                self.disk_active_array[i].pop(0)
                self.disk_active_array[i].append(active_percentage)

                self.disk_read_array[i].pop(0)
                self.disk_read_array[i].append(disk_diff[0] / 1024)  # Convert to KB

                self.disk_write_array[i].pop(0)
                self.disk_write_array[i].append(disk_diff[1] / 1024)

                # Update graph
                self.update_graph(i)

                # Update previous state
                self.disk_state1[i] = self.disk_state2

            except Exception as e:
                print(f'Error updating disk {current_disk}: {e}')

    def update_graph(self, index):
        """Update the graph for the specified disk."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.fill_between(range(len(self.disk_read_array[index])), self.disk_read_array[index], color='lightgreen', alpha=0.5, label='Чтение (KB/s)')
        ax.plot(self.disk_read_array[index], label='Чтение (KB/s)', color='green')
        ax.plot(self.disk_write_array[index], label='Запись (KB/s)', color='red')

        ax.set_ylim(0, max(max(self.disk_read_array[index], default=0), max(self.disk_write_array[index], default=0)) * 1.1)
        ax.set_title('Скорость чтения и записи диска')
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Скорость (KB/s)')
        ax.legend()
        ax.grid(True)
        self.canvas.draw()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.showMaximized()  
    sys.exit(app.exec())