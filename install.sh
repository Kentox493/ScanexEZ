#!/bin/bash

# Pastikan script dijalankan dengan hak akses root atau sudo
if [ "$EUID" -ne 0 ]; then 
  echo -e "\e[31mPlease run as root (use sudo).\e[0m"
  exit 1
fi

# Fungsi untuk menampilkan animasi pemuatan
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    echo -n " "
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    echo " "
}

# Fungsi untuk menghitung waktu eksekusi
start_time=$(date +%s)
timer() {
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo -e "\e[32mCompleted in $elapsed seconds.\e[0m"
}

# Fungsi untuk menampilkan banner
print_banner() {
  echo -e "\e[36m"
  echo "========================================================"
  echo "      Universal Vulnerability Scanning Tools Setup"
  echo "========================================================"
  echo -e "\e[0m"
}

# Fungsi untuk Arch Linux
install_arch() {
  echo "[*] Detected Arch Linux system."
  pacman -Syu &
  spinner $!
  pacman -S git python python-virtualenv curl zaproxy go || { echo "Package installation failed"; exit 1; }
  setup_virtualenv
  common_install
}

# Fungsi untuk Debian/Ubuntu
install_debian() {
  echo "[*] Detected Debian/Ubuntu system."
  apt update && apt upgrade -y &
  spinner $!
  apt install -y git python3 python3-venv python3-pip curl openjdk-11-jdk zaproxy golang || { echo "Package installation failed"; exit 1; }
  setup_virtualenv
  common_install
}

# Fungsi untuk Fedora
install_fedora() {
  echo "[*] Detected Fedora system."
  dnf install -y python3 python3-virtualenv python3-pip git curl java-11-openjdk zaproxy golang &
  spinner $!
  setup_virtualenv
  common_install
}

# Fungsi untuk CentOS/RHEL
install_centos() {
  echo "[*] Detected CentOS/RHEL system."
  yum install -y epel-release &
  spinner $!
  yum install -y python3 python3-virtualenv python3-pip git curl java-11-openjdk zaproxy golang || { echo "Package installation failed"; exit 1; }
  setup_virtualenv
  common_install
}

# Fungsi untuk openSUSE
install_opensuse() {
  echo "[*] Detected openSUSE system."
  zypper refresh &
  spinner $!
  zypper install -y python3 python3-virtualenv python3-pip git curl java-11-openjdk zaproxy go || { echo "Package installation failed"; exit 1; }
  setup_virtualenv
  common_install
}

# Fungsi untuk menyiapkan virtual environment
setup_virtualenv() {
  echo "[*] Setting up Python virtual environment..."
  mkdir -p /opt/venvs
  python3 -m venv /opt/venvs/ScanexEZ
  chown -R $USER:$USER /opt/venvs/ScanexEZ
  chmod -R 755 /opt/venvs/ScanexEZ
  source /opt/venvs/ScanexEZ/bin/activate
  echo "[*] Virtual environment activated."
}

# Fungsi untuk mengosongkan atau memperbarui direktori
prepare_directory() {
  local dir=$1
  if [ -d "$dir" ]; then
    echo "[*] $dir already exists. Cleaning up..."
    rm -rf "$dir"
  fi
  mkdir -p "$dir"
  chown -R $USER:$USER "$dir"
  chmod -R 755 "$dir"
}

# Fungsi untuk memberikan izin eksekusi pada semua file
apply_permissions() {
  local dir=$1
  echo "[*] Applying execute permissions to all files in $dir..."
  find "$dir" -type f -exec chmod +x {} \;
}

# Fungsi untuk menginstal tools dan membuat symlink
common_install() {
  echo "[*] Installing tools in background..."
  (
    prepare_directory /opt/sqlmap
    git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap
    apply_permissions /opt/sqlmap
    ln -sf /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap

    go install github.com/hahwul/dalfox/v2@latest
    ln -sf ~/go/bin/dalfox /usr/local/bin/dalfox

    prepare_directory /opt/LFImap
    pip install lfimap

    prepare_directory /opt/XSRFProbe
    pip install xsrfprobe

    prepare_directory /opt/OpenRedireX
    git clone https://github.com/devanshbatham/OpenRedireX.git /opt/OpenRedireX
    cd /opt/OpenRedireX && sudo ./setup.sh
    apply_permissions /opt/OpenRedireX
    ln -sf /opt/OpenRedireX/openredirex.py /usr/local/bin/openredirex

  ) &
  spinner $!
}

# Deteksi distribusi Linux
print_banner
if [ -f /etc/arch-release ]; then
  install_arch
elif [ -f /etc/debian_version ]; then
  install_debian
elif [ -f /etc/fedora-release ]; then
  install_fedora
elif [ -f /etc/centos-release ]; then
  install_centos
elif [ -f /etc/os-release ] && grep -qi "opensuse" /etc/os-release; then
  install_opensuse
else
  echo -e "\e[31mUnsupported Linux distribution.\e[0m"
  exit 1
fi

timer
