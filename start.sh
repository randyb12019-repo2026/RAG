#!/bin/bash
ollama serve &

echo "Esperando a que Ollama esté listo..."
until ollama list > /dev/null 2>&1; do
  sleep 2
done
echo "Ollama listo"

streamlit run app.py --server.port=7860 --server.address=0.0.0.0
