// Obtener elementos del DOM
const sensorSelect = document.getElementById('sensorSelect');
const tempCtx = document.getElementById('temperatureChart').getContext('2d');
const type1Ctx = document.getElementById('type1Chart').getContext('2d');
const loadingSpinner = document.getElementById('loadingSpinner');
const lastTemperature = document.getElementById('lastTemperature');
const lastType1 = document.getElementById('lastType1');

// Variables globales
let temperatureData = [];
let type1Data = [];
let timestamps = [];

// Inicializar gráficos
const temperatureChart = new Chart(tempCtx, {
  type: 'line',
  data: { labels: [], datasets: [{ label: 'Temperatura (°C)', data: [], borderColor: 'red', tension: 0.4 }] },
  options: { responsive: true },
});

const type1Chart = new Chart(type1Ctx, {
  type: 'line',
  data: { labels: [], datasets: [{ label: 'Tipo 1', data: [], borderColor: 'blue', tension: 0.4 }] },
  options: { responsive: true },
});

// Función genérica para realizar solicitudes API con token JWT
async function apiRequest(url, method = "GET", body = null) {
  const token = localStorage.getItem("access_token");

  if (!token) {
      console.error("Token JWT faltante. Redirigiendo al login...");
      window.location.href = "/";
      return null;
  }

  try {
      const headers = {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
      };

      console.log(`Enviando solicitud a ${url} con token:`, token);

      const options = { method, headers };
      if (body) {
          options.body = JSON.stringify(body);
      }

      const response = await fetch(url, options);

      if (response.status === 401) {
          console.warn("Token inválido o expirado. Redirigiendo al login...");
          localStorage.removeItem("access_token");
          window.location.href = "/";
          return null;
      }

      if (!response.ok) {
          console.error(`Error en la solicitud (${response.status}):`, await response.text());
          return null;
      }

      return await response.json();
  } catch (error) {
      console.error("Error al conectar con la API:", error);
      return null;
  }
}

// Cargar datos iniciales del dashboard
async function loadDashboard() {
  const sensors = await apiRequest("/dashboard");

  if (sensors) {
      console.log("Datos del dashboard:", sensors);
      fetchSensors();
  } else {
      console.error("No se pudieron cargar los datos del dashboard.");
  }
}

// Obtener lista de sensores
async function fetchSensors() {
  const sensors = await apiRequest("/api/sensors");

  if (sensors && Array.isArray(sensors)) {
      sensors.forEach(sensor => {
          const option = document.createElement('option');
          option.value = sensor.id;
          option.textContent = `${sensor.name} (ID: ${sensor.id})`;
          sensorSelect.appendChild(option);
      });
  } else {
      console.error("No se pudieron cargar los sensores.");
  }
}

// Actualizar gráficos
async function updateCharts(sensorId) {
  if (!sensorId) return;

  loadingSpinner.style.display = 'block';

  try {
      const data = await apiRequest(`/api/data?sensor_id=${sensorId}`);

      if (data && Array.isArray(data)) {
          // Actualizar datos
          timestamps = data.map(d => d.timestamp);
          temperatureData = data.map(d => d.temperature);
          type1Data = data.map(d => d.type1);

          // Actualizar gráficos
          temperatureChart.data.labels = timestamps;
          temperatureChart.data.datasets[0].data = temperatureData;
          temperatureChart.update();

          type1Chart.data.labels = timestamps;
          type1Chart.data.datasets[0].data = type1Data;
          type1Chart.update();

          // Actualizar etiquetas y cajas de datos
          lastTemperature.textContent = `${temperatureData[0]} °C`;
          lastType1.textContent = `${type1Data[0]}`;
      } else {
          console.error("No se encontraron datos para el sensor seleccionado.");
      }
  } catch (error) {
      console.error("Error actualizando gráficos:", error);
  } finally {
      loadingSpinner.style.display = 'none';
  }
}

// Cambiar sensor
sensorSelect.addEventListener('change', () => {
  const sensorId = sensorSelect.value;
  updateCharts(sensorId);
});

// Ejecutar cuando la página se cargue
window.onload = loadDashboard;
