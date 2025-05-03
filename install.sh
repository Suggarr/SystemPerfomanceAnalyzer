#!/bin/bash

set -e

VENV_DIR="venv"
INSTALL_DIR="/opt/system_performance_analyzer"
DESKTOP_FILE="$HOME/.local/share/applications/system_performance_analyzer.desktop"

install_system_packages() {
    echo "Установка необходимых системных библиотек..."
    sudo apt update
    sudo apt install -y \
        python3-venv python3-dev python3-pip python3-pyqt6 python3-psutil python3-matplotlib \
        cmake cpp g++ gcc dpkg dpkg-dev fdisk gdisk pciutils \
        pyqt5-dev-tools pyqt6-dev-tools \
        designer-qt6 libqt6svg6-dev libqt6opengl6-dev \
        python3-gi python3-gi-cairo python3-cairo python3-pyqt-distutils \
        libjpeg-dev libpng-dev python3-netifaces \
        time sysstat
}

copy_application() {
    echo "Копирование приложения и модулей в $INSTALL_DIR..."
    sudo mkdir -p "$INSTALL_DIR"

    if [[ ! -f "main.py" ]]; then
        echo "Ошибка: main.py не найден!" >&2
        exit 1
    fi
    sudo cp main.py "$INSTALL_DIR/"
    sudo chmod +x "$INSTALL_DIR/main.py"

    for dir in cpu memory process network disk; do
        if [[ -d "$dir" ]]; then
            sudo cp -r "$dir" "$INSTALL_DIR/"
        else
            echo "Папка $dir отсутствует, пропускаем."
        fi
    done

    if [[ ! -f "icon/icon.png" ]]; then
        echo "Ошибка: icon/icon.png не найден!" >&2
        exit 1
    fi
    sudo mkdir -p "$INSTALL_DIR/icon"
    sudo cp icon/icon.png "$INSTALL_DIR/icon/"
}

create_virtualenv() {
    echo "Создание виртуального окружения..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"

    if [[ ! -f "requirements.txt" ]]; then
        echo "Файл requirements.txt отсутствует!" >&2
        deactivate
        exit 1
    fi

    pip install --upgrade pip
    pip install -r requirements.txt

    deactivate
    sudo cp -r "$VENV_DIR" "$INSTALL_DIR/"
}

create_shortcut() {
    echo "Создание ярлыка для приложения..."

    # Проверяем, существует ли уже файл ярлыка
    if [[ -f "$DESKTOP_FILE" ]]; then
        echo "Ярлык уже существует, пропускаем создание."
        return
    fi

    mkdir -p "$(dirname "$DESKTOP_FILE")"

    cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=System Performance Analyzer
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/main.py
Icon=$INSTALL_DIR/icon/icon.png
Terminal=false
Categories=Utility;
EOF

    chmod +x "$DESKTOP_FILE"
}

create_terminal_command() {
    echo "Создание команды system_performance_analyzer в /usr/local/bin..."

    # Проверяем, существует ли уже команда
    if [[ -f "/usr/local/bin/system_performance_analyzer" ]]; then
        echo "Команда уже существует, пропускаем создание."
        return
    fi

    sudo tee /usr/local/bin/system_performance_analyzer > /dev/null <<EOF
#!/bin/bash
source "$INSTALL_DIR/venv/bin/activate"
python "$INSTALL_DIR/main.py"
EOF

    sudo chmod +x /usr/local/bin/system_performance_analyzer
}

main() {
    install_system_packages
    copy_application
    create_virtualenv
    create_shortcut
    create_terminal_command

    echo "Установка завершена!"
    echo "Запустите программу из меню или командой: system_performance_analyzer"
}

main
