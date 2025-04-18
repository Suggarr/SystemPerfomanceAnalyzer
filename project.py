# -*- coding: utf-8 -*-

import sys
import psutil
import GPUtil
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QWidget, QDialog, QTabWidget
)
from PySide6.QtGui import QAction
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ResourceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Loading...")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def update_info(self, info):
        self.label.setText(info)


class CPUResourceTab(ResourceTab):
    def __init__(self):
        super().__init__()
        self.cpu_usage = []
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_cpu_usage)
        self.timer.start(1000)

    def update_cpu_usage(self):
        usage = psutil.cpu_percent(interval=None)
        self.cpu_usage.append(usage)

        if len(self.cpu_usage) > 20:
            self.cpu_usage.pop(0)

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.cpu_usage, label='CPU Usage (%)')
        ax.set_ylim(0, 100)
        ax.set_title('CPU Usage Over Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Usage (%)')
        ax.legend()
        self.canvas.draw()


class MemoryResourceTab(ResourceTab):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_memory_info)
        self.timer.start(1000)

    def update_memory_info(self):
        memory = psutil.virtual_memory()
        info = f"Total: {memory.total / (1024 ** 2):.2f} MB\n" \
               f"Used: {memory.used / (1024 ** 2):.2f} MB\n" \
               f"Free: {memory.free / (1024 ** 2):.2f} MB\n" \
               f"Percentage: {memory.percent}%"
        self.update_info(info)


class DiskResourceTab(ResourceTab):
    def __init__(self, disk_name):
        super().__init__()
        self.disk_name = disk_name
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_disk_info)
        self.timer.start(1000)

    def update_disk_info(self):
        disk_usage = psutil.disk_usage(self.disk_name)
        info = f"Total: {disk_usage.total / (1024 ** 3):.2f} GB\n" \
               f"Used: {disk_usage.used / (1024 ** 3):.2f} GB\n" \
               f"Free: {disk_usage.free / (1024 ** 3):.2f} GB\n" \
               f"Percentage: {disk_usage.percent}%"
        self.update_info(info)


class NetworkResourceTab(ResourceTab):
    def __init__(self, interface_name):
        super().__init__()
        self.interface_name = interface_name
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_network_info)
        self.timer.start(1000)

    def update_network_info(self):
        net_io = psutil.net_io_counters(pernic=True)[self.interface_name]
        info = f"Bytes Sent: {net_io.bytes_sent / (1024 ** 2):.2f} MB\n" \
               f"Bytes Received: {net_io.bytes_recv / (1024 ** 2):.2f} MB"
        self.update_info(info)


class GPUResourceTab(ResourceTab):
    def __init__(self, gpu_id):
        super().__init__()
        self.gpu_id = gpu_id
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gpu_info)
        self.timer.start(1000)

    def update_gpu_info(self):
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            if gpu.id == self.gpu_id:
                info = f"GPU ID: {gpu.id}\n" \
                       f"Name: {gpu.name}\n" \
                       f"Load: {gpu.load * 100:.2f}%\n" \
                       f"Memory Total: {gpu.memoryTotal} MB\n" \
                       f"Memory Free: {gpu.memoryFree} MB\n" \
                       f"Memory Used: {gpu.memoryUsed} MB"
                break
        self.update_info(info)


class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.setup_table()
        self.update_processes()

    def setup_table(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["PID", "Name", "Status"])
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

    def update_processes(self):
        self.table.setRowCount(0)
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            self.add_process_to_table(proc)

    def add_process_to_table(self, proc):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(str(proc.info['pid'])))
        self.table.setItem(row_position, 1, QTableWidgetItem(proc.info['name']))
        self.table.setItem(row_position, 2, QTableWidgetItem(proc.info['status']))

    def show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if item:
            menu = QMenu(self)
            kill_action = QAction("Завершить процесс", self)
            kill_action.triggered.connect(lambda: self.kill_process(item))
            menu.addAction(kill_action)
            menu.exec_(self.table.viewport().mapToGlobal(pos))

    def kill_process(self, item):
        pid = int(self.table.item(item.row(), 0).text())
        try:
            p = psutil.Process(pid)
            p.terminate()  # Или p.kill() для принудительного завершения
            self.update_processes()  # Обновляем таблицу
        except Exception as e:
            print(f"Ошибка завершения процесса {pid}: {e}")


class Ui_Dialog(QDialog):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(691, 519)
        Dialog.setSizeGripEnabled(True)  # Позволяем изменять размер
        Dialog.setModal(False)

        self.gridLayoutWidget = QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, -1, 691, 521))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")

        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.tabWidget = QTabWidget(self.gridLayoutWidget)
        self.tabWidget.setObjectName("tabWidget")

        # Создание вкладки процессов
        self.process_tab = ProcessTab()
        self.tabWidget.addTab(self.process_tab, "Процессы")

        # Создание вкладки производительности
        self.performance_tab = QTabWidget()
        
        # Под-вкладки для ресурсов
        self.performance_tab.addTab(CPUResourceTab(), "CPU")
        self.performance_tab.addTab(MemoryResourceTab(), "Память")

        for partition in psutil.disk_partitions():
            self.performance_tab.addTab(DiskResourceTab(partition.mountpoint), partition.mountpoint)

        for interface in psutil.net_if_addrs():
            self.performance_tab.addTab(NetworkResourceTab(interface), interface)

        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            self.performance_tab.addTab(GPUResourceTab(gpu.id), gpu.name)

        self.tabWidget.addTab(self.performance_tab, "Производительность")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Resource Monitor"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())