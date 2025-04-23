from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import psutil
import subprocess


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