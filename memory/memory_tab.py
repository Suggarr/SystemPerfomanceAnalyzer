from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import psutil


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