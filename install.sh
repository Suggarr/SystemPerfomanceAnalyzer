#!/bin/bash

# Имя виртуального окружения
VENV_DIR="venv"

# Функция для установки системных пакетов
install_system_packages() {
    echo "Установка необходимых системных библиотек..."
    sudo apt update
    sudo apt install -y python3-pyqt6 python3-psutil python3-matplotlib python3-pip cmake cpp designer-qt6 fdisk g++ dpkg dpkg-dev gcc gdisk pciutils pyqt5-dev-tools pyqt6-dev-tools python3 python3.12 python3-cairo python3-dev python3-gi python3-gi-cairo python3-pip python3-pip-whl python3-pyqt-distutils python3-pyqt6 python3-venv time sysstat libqt6svg6-dev libqt6opengl6-dev libjpeg-dev libpng-dev python3-netifaces
}

# Функция для создания виртуального окружения
create_virtualenv() {
    echo "Создание виртуального окружения..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"

    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "Файл requirements.txt отсутствует. Проверьте перед установкой."
        exit 1
    fi
}

create_shortcut() {
    echo "Создание ярлыка для приложения..."

    # Убедитесь, что директория для ярлыков существует
    if [ ! -d "$HOME/.local/share/applications" ]; then
        mkdir -p "$HOME/.local/share/applications"
    fi

    # Создайте ярлык
    cat <<EOF > "$HOME/.local/share/applications/system_performance_analyzer.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=System Performance Analyzer
Exec=$(pwd)/$VENV_DIR/bin/python /opt/system_performance_analyzer/main.py
Icon=/opt/system_performance_analyzer/icon/icon.png
Terminal=false
Categories=Utility;
EOF

    chmod +x "$HOME/.local/share/applications/system_performance_analyzer.desktop"
}

# Функция для копирования приложения и папок с модулями
copy_application() {
    echo "Копирование приложения и модулей в /opt/system_performance_analyzer..."

    # Создаем целевую директорию
    sudo mkdir -p /opt/system_performance_analyzer

    # Копируем основное приложение
    if [ -f "main.py" ]; then
        sudo cp main.py /opt/system_performance_analyzer/
        sudo chmod +x /opt/system_performance_analyzer/main.py
    else
        echo "Ошибка: Файл main.py отсутствует!"
        exit 1
    fi

    # Копируем папки с модулями
    for dir in cpu memory process network disk; do
        if [ -d "$dir" ]; then
            sudo cp -r "$dir" /opt/system_performance_analyzer/
        else
            echo "Внимание: Папка $dir отсутствует, пропускаем."
        fi
    done

    # Копируем иконку
    if [ -f "icon/icon.png" ]; then
        sudo mkdir -p /opt/system_performance_analyzer/icon
        sudo cp icon/icon.png /opt/system_performance_analyzer/icon/
    else
        echo "Ошибка: Файл icon/icon.png отсутствует!"
        exit 1
    fi
}

# Основной запуск скрипта
install_system_packages
copy_application
create_virtualenv
create_shortcut

echo "Установка завершена!"