import sys
import psutil
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QWidget, QDialog, QTabWidget
)
from os import popen
from PySide6.QtCore import QTimer, Qt
from cpu.cpu_tab import CPUResourceTab
from memory.memory_tab import MemoryResourceTab
from process.process_tab import ProcessTab
from network.network_tab import NetworkResourceTab
from disk.disk_tab import DiskResourceTab
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


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
        self.performance_tab.addTab(CPUResourceTab(), "Процессор")
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
        Dialog.setWindowTitle(_translate("Dialog", "Системный анализатор производительности"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.showMaximized()
    sys.exit(app.exec())