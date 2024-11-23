import tkinter as tk
from tkinter import ttk, messagebox
import requests

# Configuración de la API
API_BASE_URL = "http://127.0.0.1:5000"  # Cambia a la URL de tu backend

# Función para obtener la lista de usuarios desde la API
def fetch_users():
    try:
        response = requests.get(f"{API_BASE_URL}/api/users")  # Asegúrate de que este endpoint exista
        if response.status_code == 200:
            return response.json()  # Devuelve una lista de usuarios
        else:
            messagebox.showerror("Error", f"Error al obtener usuarios: {response.status_code}")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la API: {e}")
        return []

# Función para crear un nuevo sensor
def create_sensor():
    sensor_name = name_var.get().strip()
    sensor_type = type_var.get().strip()
    user_id = user_var.get()
    sensor_status = status_var.get()

    if not sensor_name or not sensor_type or not user_id or not sensor_status:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
        return

    # Datos para enviar a la API
    sensor_data = {
        "device_name": sensor_name,
        "device_type": sensor_type,
        "user_id": user_id,
        "status": sensor_status,
    }

    try:
        response = requests.post(f"{API_BASE_URL}/devices/add", json=sensor_data)
        if response.status_code == 201:
            messagebox.showinfo("Éxito", "Sensor creado exitosamente.")
            reset_form()
        else:
            error_message = response.json().get("message", "Error desconocido")
            messagebox.showerror("Error", f"No se pudo crear el sensor: {error_message}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la API: {e}")

# Función para reiniciar el formulario
def reset_form():
    name_var.set("")
    type_var.set("")
    user_var.set("")
    status_var.set("activo")

# Crear la ventana principal
app = tk.Tk()
app.title("Crear Sensor")
app.geometry("400x400")
app.resizable(False, False)

# Variables para los campos de entrada
name_var = tk.StringVar()
type_var = tk.StringVar()
user_var = tk.StringVar()
status_var = tk.StringVar(value="activo")

# Etiquetas y campos de entrada
ttk.Label(app, text="Nombre del Sensor:", font=("Arial", 12)).pack(pady=5)
ttk.Entry(app, textvariable=name_var, font=("Arial", 12), width=30).pack(pady=5)

ttk.Label(app, text="Tipo de Sensor:", font=("Arial", 12)).pack(pady=5)
ttk.Entry(app, textvariable=type_var, font=("Arial", 12), width=30).pack(pady=5)

ttk.Label(app, text="Usuario Asignado:", font=("Arial", 12)).pack(pady=5)
user_dropdown = ttk.Combobox(app, textvariable=user_var, font=("Arial", 12), width=28, state="readonly")
user_dropdown.pack(pady=5)

ttk.Label(app, text="Estado del Sensor:", font=("Arial", 12)).pack(pady=5)
ttk.Combobox(app, textvariable=status_var, font=("Arial", 12), width=28, state="readonly",
             values=["activo", "inactivo"]).pack(pady=5)

# Botones
ttk.Button(app, text="Crear Sensor", command=create_sensor).pack(pady=20)
ttk.Button(app, text="Reiniciar Formulario", command=reset_form).pack()

# Llenar el dropdown de usuarios al iniciar
users = fetch_users()
if users:
    user_dropdown["values"] = [f"{user['id']} - {user['username']}" for user in users]

# Ejecutar la aplicación
app.mainloop()
