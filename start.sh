#!/bin/bash
ollama serve &

echo "Esperando a que Ollama esté listo..."
until ollama list > /dev/null 2>&1; do
  sleep 2
done
echo "Ollama listo"

echo "Descargando embeddinggemma:300m..."
ollama pull embeddinggemma:300m
echo "embeddinggemma:300m OK"

echo "Descargando qwen3:4b..."
ollama pull qwen3:4b
echo "qwen3:4b OK"

echo "Iniciando Streamlit..."
streamlit run app.py --server.port=7860 --server.address=0.0.0.0
