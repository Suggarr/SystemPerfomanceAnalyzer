# -*- coding: utf-8 -*-

import sys
import psutil
import platform
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QWidget, QDialog, QTabWidget
)
from PySide6.QtGui import QAction, QIcon
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


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

        # Получение информации о кэше
        # cache_info = self.get_cache_info()

        # Получение температуры
        # temp_info = self.get_cpu_temperature()

        self.model_label.setText(f"Модель: {model_name}")
        self.speed_label.setText(f"Макс. скорость: {cpu_freq.max} GHz")
        self.cores_label.setText(f"Ядра: {cpu_count}")
        self.threads_label.setText(f"Логические процессоры: {logical_count}")
        self.virtualization_label.setText(f"Виртуализация: {virtualization}")
        # self.cache_label.setText(f"Кэш: {cache_info}")
        # self.temp_label.setText(f"Температура: {temp_info}")

    # def get_cache_info(self):
    #     # Здесь можно реализовать получение информации о кэше
    #     return "Неизвестно"  # Замените на фактическую реализацию

    # def get_cpu_temperature(self):
    #     # Здесь можно реализовать получение температуры процессора
    #     return "Неизвестно"  # Замените на фактическую реализацию

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
        self.timer.start(2000)  # Update every 2 seconds

    def setup_table(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Icon", "PID", "Name", "CPU Usage (%)", "Memory Usage (%)", "User"])
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

    def update_processes(self):
        self.table.setRowCount(0)
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent', 'exe']):
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

                # Retrieve icon
                icon = self.get_process_icon(proc.info['exe'])
                icon_item = QTableWidgetItem()  # Create a QTableWidgetItem
                icon_item.setIcon(icon)  # Set the icon
                icon_item.setFlags(Qt.ItemIsEnabled)  # Make the icon item non-editable
                self.table.setItem(row_position, 0, icon_item)

                self.table.setItem(row_position, 1, QTableWidgetItem(str(proc.info['pid'])))
                self.table.setItem(row_position, 2, QTableWidgetItem(proc.info['name']))
                self.table.setItem(row_position, 3, QTableWidgetItem(f"{proc.info['cpu_percent']}%"))
                self.table.setItem(row_position, 4, QTableWidgetItem(f"{proc.info['memory_percent']:.2f}%"))
                self.table.setItem(row_position, 5, QTableWidgetItem(proc.info['username']))

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def get_process_icon(self, exe_path):
        # Get the icon for the process executable
        try:
            if exe_path:
                return QIcon(exe_path)  # Return the icon from the executable path
        except Exception as e:
            print(f"Could not retrieve icon for {exe_path}: {e}")
        return QIcon()  # Return a default icon if there's an error

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
            p.terminate()  # Or p.kill() for forced termination
            self.update_processes()  # Refresh the table
        except Exception as e:
            print(f"Ошибка завершения процесса {pid}: {e}")


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(700, 519)  # Установите желаемый размер окна
        Dialog.setSizeGripEnabled(True)  # Позволить изменение размера
        Dialog.setModal(False)

        self.layout = QVBoxLayout(Dialog)  # Используем QVBoxLayout для главного окна
        self.tabWidget = QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Создание вкладок
        self.process_tab = ProcessTab()
        self.tabWidget.addTab(self.process_tab, "Процессы")
        
        self.performance_tab = QTabWidget()
        self.performance_tab.addTab(CPUResourceTab(), "CPU")
        self.performance_tab.addTab(MemoryResourceTab(), "Память")
        
        self.tabWidget.addTab(self.performance_tab, "Производительность")
        
        self.layout.addWidget(self.tabWidget)  # Добавляем QTabWidget в основной layout

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Resource Monitor"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.showMaximized()  
    sys.exit(app.exec())