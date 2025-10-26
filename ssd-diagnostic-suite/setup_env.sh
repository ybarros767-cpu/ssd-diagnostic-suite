#!/bin/bash

echo "Configurando ambiente do SSD Diagnostic Suite..."

# Diretório do projeto
PROJECT_DIR="$(dirname "$(readlink -f "$0")")"
BACKEND_DIR="$PROJECT_DIR/backend"
ENV_FILE="$BACKEND_DIR/.env"

# Função para solicitar a chave da API OpenAI
setup_openai_key() {
    echo
    echo "Configuração da API OpenAI"
    echo "========================="
    echo "Para usar recursos de IA avançada, é necessária uma chave da API OpenAI."
    echo "Você pode obtê-la em: https://platform.openai.com/account/api-keys"
    echo
    read -p "Digite sua chave da API OpenAI: " api_key
    echo

    # Validar a chave (formato básico)
    if [[ ! $api_key =~ ^sk-[A-Za-z0-9]{48}$ ]]; then
        echo "AVISO: O formato da chave parece incorreto. Deve começar com 'sk-' seguido por 48 caracteres."
        read -p "Deseja continuar mesmo assim? (s/N) " confirm
        if [[ ! $confirm =~ ^[Ss]$ ]]; then
            echo "Configuração cancelada."
            exit 1
        fi
    fi

    # Criar ou atualizar o arquivo .env
    if [ -f "$ENV_FILE" ]; then
        # Atualizar chave existente
        sed -i "s/^OPENAI_API_KEY=.*/OPENAI_API_KEY=$api_key/" "$ENV_FILE"
    else
        # Criar novo arquivo .env
        cp "$BACKEND_DIR/.env.example" "$ENV_FILE"
        sed -i "s/^OPENAI_API_KEY=.*/OPENAI_API_KEY=$api_key/" "$ENV_FILE"
    fi

    echo "Chave da API configurada com sucesso!"
}

# Criar arquivo .env se não existir
if [ ! -f "$ENV_FILE" ]; then
    cp "$BACKEND_DIR/.env.example" "$ENV_FILE"
fi

# Verificar se a chave da API está configurada
if grep -q "OPENAI_API_KEY=your-api-key-here" "$ENV_FILE"; then
    setup_openai_key
else
    echo "Uma chave da API OpenAI já está configurada."
    read -p "Deseja reconfigurá-la? (s/N) " reconfigure
    if [[ $reconfigure =~ ^[Ss]$ ]]; then
        setup_openai_key
    fi
fi

echo
echo "Configuração concluída!"
echo "Para iniciar o programa, execute: npm run electron:dev"
