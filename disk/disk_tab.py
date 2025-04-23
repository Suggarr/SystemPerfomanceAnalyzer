from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QWidget, QDialog, QTabWidget
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from os import popen
import psutil

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
