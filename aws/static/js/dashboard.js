const sensorSelect = document.getElementById('sensorSelect');
const tempCtx = document.getElementById('temperatureChart').getContext('2d');
const type1Ctx = document.getElementById('type1Chart').getContext('2d');
const loadingSpinner = document.getElementById('loadingSpinner');
const lastTemperature = document.getElementById('lastTemperature');
const lastType1 = document.getElementById('lastType1');
const type1Label = document.getElementById('type1Label');
const type1GraphLabel = document.getElementById('type1GraphLabel');

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

// Obtener lista de sensores
async function fetchSensors() {
  try {
    const response = await fetch('/api/sensors'); // Cambia al endpoint correcto
    const sensors = await response.json();

    sensors.forEach(sensor => {
      const option = document.createElement('option');
      option.value = sensor.id;
      option.textContent = `${sensor.name} (ID: ${sensor.id})`;
      sensorSelect.appendChild(option);
    });
  } catch (error) {
    console.error('Error obteniendo sensores:', error);
  }
}

// Actualizar gráficos
async function updateCharts(sensorId) {
  if (!sensorId) return;

  loadingSpinner.style.display = 'block';

  try {
    const response = await fetch(`/api/data?sensor_id=${sensorId}`); // Cambia al endpoint correcto
    const data = await response.json();

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
    type1Label.textContent = `Último Dato (${data[0].type1_name})`;
    type1GraphLabel.textContent = `Gráfico (${data[0].type1_name})`;
  } catch (error) {
    console.error('Error actualizando gráficos:', error);
  } finally {
    loadingSpinner.style.display = 'none';
  }
}

// Cambiar sensor
sensorSelect.addEventListener('change', () => {
  const sensorId = sensorSelect.value;
  updateCharts(sensorId);
});

// Inicializar
fetchSensors();
