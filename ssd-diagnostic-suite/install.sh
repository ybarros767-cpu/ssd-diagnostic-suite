#!/bin/bash

echo "Instalando SSD Diagnostic Suite..."

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    echo "Este script não deve ser executado como root!"
    echo "Por favor, execute sem sudo."
    exit 1
fi

# Verificar dependências do sistema
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo "Instalando $1..."
        sudo apt-get install -y $1
    fi
}

# Verificar e instalar Node.js
if ! command -v node &> /dev/null; then
    echo "Instalando Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Verificar e instalar Python 3 e pip
check_dependency python3
check_dependency python3-pip

# Instalar dependências do sistema
DEPS="smartmontools nvme-cli lshw hdparm usbutils pciutils e2fsprogs fio"
for dep in $DEPS; do
    check_dependency $dep
done

# Criar ambiente virtual Python
echo "Configurando ambiente Python..."
python3 -m venv backend/venv
source backend/venv/bin/activate

# Instalar dependências Python
echo "Instalando dependências Python..."
pip install -r backend/requirements.txt

# Instalar dependências Node.js
echo "Instalando dependências Node.js..."
npm install

# Build do frontend
echo "Compilando frontend..."
npm run build

# Criar atalho do desktop
echo "Criando atalho do desktop..."
cat > ~/.local/share/applications/ssd-diagnostic.desktop <<EOL
[Desktop Entry]
Name=SSD Diagnostic Suite
Comment=Diagnóstico avançado de SSDs
Exec=$(pwd)/start.sh
Icon=$(pwd)/public/disk.svg
Terminal=false
Type=Application
Categories=System;
EOL

# Criar script de inicialização
echo "Criando script de inicialização..."
cat > start.sh <<EOL
#!/bin/bash
cd "$(dirname "\$0")"
source backend/venv/bin/activate
npm run electron:dev
EOL
chmod +x start.sh

echo "Instalação concluída!"
echo "Para iniciar o programa, execute ./start.sh ou use o atalho criado no menu do sistema."