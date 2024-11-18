#!/bin/bash

# Mensaje de inicio
echo "Iniciando servicios Flask..."

# Navegar al directorio del proyecto
echo "Navegando al directorio del proyecto..."
cd ~/webserver || { echo "Directorio ~/webserver no encontrado. Abortando."; exit 1; }

# Iniciar el servidor webserver.py
echo "Iniciando webserver.py..."
nohup python3 webserver.py > webserver.log 2>&1 &
if [ $? -eq 0 ]; then
  echo "webserver.py iniciado correctamente. Logs en webserver.log"
else
  echo "Error al iniciar webserver.py."
fi

# Iniciar el servidor api.py
echo "Iniciando api.py..."
nohup python3 api.py > api.log 2>&1 &
if [ $? -eq 0 ]; then
  echo "api.py iniciado correctamente. Logs en api.log"
else
  echo "Error al iniciar api.py."
fi

# Confirmar procesos en ejecución
echo "Procesos en ejecución:"
ps aux | grep -E 'webserver.py|api.py' | grep -v grep

# Mensaje de finalización
echo "Todos los servicios han sido lanzados."