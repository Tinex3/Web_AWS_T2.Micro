#!/bin/bash

# Mensaje de inicio
echo "Iniciando servicios Flask con entorno virtual..."

# Navegar al directorio del proyecto
echo "Navegando al directorio del proyecto..."
cd ~/App || { echo "Directorio ~/App no encontrado. Abortando."; exit 1; }

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
  echo "El entorno virtual no se encuentra en ~/App/venv. Creándolo..."
  python3 -m venv venv || { echo "Error al crear el entorno virtual. Abortando."; exit 1; }
fi

# Activar el entorno virtual
echo "Activando el entorno virtual..."
source venv/bin/activate || { echo "Error al activar el entorno virtual. Abortando."; exit 1; }

# Instalar dependencias (opcional)
echo "Instalando dependencias desde requirements.txt (si existe)..."
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt || { echo "Error al instalar dependencias. Abortando."; deactivate; exit 1; }
fi

# Iniciar el servidor App.py
echo "Iniciando App.py..."
nohup python3 App.py > App.log 2>&1 &
if [ $? -eq 0 ]; then
  echo "App.py iniciado correctamente. Logs en App.log"
else
  echo "Error al iniciar App.py."
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
ps aux | grep -E 'App.py|api.py' | grep -v grep

# Desactivar el entorno virtual
echo "Desactivando el entorno virtual..."
deactivate

# Mensaje de finalización
echo "Todos los servicios han sido lanzados."

