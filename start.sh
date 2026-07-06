#!/bin/bash
mkdir -p /data/ollama/models

ollama serve &

echo "Esperando a que Ollama esté listo..."
until ollama list > /dev/null 2>&1; do
  sleep 2
done
echo "Ollama listo"

pull_if_missing() {
  local model=$1
  if ollama list 2>/dev/null | grep -q "$model"; then
    echo "$model ya descargado"
  else
    echo "Descargando $model..."
    ollama pull "$model"
    echo "$model OK"
  fi
}

pull_if_missing embeddinggemma:300m
pull_if_missing qwen2.5:1.5b

echo "Iniciando Streamlit..."
streamlit run app.py --server.port=7860 --server.address=0.0.0.0
