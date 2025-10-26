#!/bin/bash

echo "Iniciando SSD Diagnostic Suite..."

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    echo "Este aplicativo não deve ser executado como root!"
    echo "Por favor, execute sem sudo."
    exit 1
fi

# Ativar ambiente virtual Python
source backend/venv/bin/activate

# Iniciar o backend Python
python3 backend/main.py &
BACKEND_PID=$!

# Aguardar o backend iniciar
sleep 2

# Iniciar o frontend
npm run electron:dev

# Ao encerrar, matar o processo do backend
kill $BACKEND_PID