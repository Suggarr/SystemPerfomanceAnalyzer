from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QWidget, QDialog, QTabWidget
)
from PySide6.QtGui import QAction
import psutil

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