#!/bin/bash

# Caminho para o arquivo .env
ENV_FILE="/mnt/nfs/scraper_2025/.env"

# Obter o ID da rede Docker
NETWORK_ID=$(docker network ls --filter name=app_network --format "{{.ID}}")

# Verificar se a rede foi encontrada
if [ -z "$NETWORK_ID" ]; then
  echo "Erro: Rede Docker não encontrada." >&2
  exit 1
fi

# Obter o nome da interface de rede associada à rede Docker
INTERFACE_NAME="br-$NETWORK_ID"

# Verificar se a interface de rede existe
if ! ifconfig "$INTERFACE_NAME" > /dev/null 2>&1; then
  echo "Erro: Interface de rede '$INTERFACE_NAME' não encontrada." >&2
  exit 1
fi

# Verificar se a variável INTERFACE já existe no arquivo .env
if grep -q "^INTERFACE=" "$ENV_FILE"; then
  # Substituir o valor existente da variável INTERFACE
  sed -i -E "s/^INTERFACE=.*/INTERFACE=$INTERFACE_NAME/" "$ENV_FILE"
else
  # Adicionar a variável INTERFACE ao final do arquivo .env
  echo "INTERFACE=$INTERFACE_NAME" >> "$ENV_FILE"
fi

echo "Nome da interface de rede atualizado em $ENV_FILE: $INTERFACE_NAME"