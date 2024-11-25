// Define la URL base de la API
const API_BASE_URL = "http://192.168.0.11:5000"; // Cambia esta IP si es necesario

// Obtener elementos del DOM
const sensorSelect = document.getElementById('sensorSelect');
const chart1Ctx = document.getElementById('chart1').getContext('2d');
const chart2Ctx = document.getElementById('chart2').getContext('2d');
const loadingSpinner = document.getElementById('loadingSpinner');
const lastVariable1 = document.getElementById('lastVariable1');
const lastVariable2 = document.getElementById('lastVariable2');

// Variables globales para datos
let chart1Data = [];
let chart2Data = [];
let timestamps = [];

// Inicializar gráficos
const chart1 = new Chart(chart1Ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Variable 1',
        data: [],
        borderColor: 'red',
        tension: 0.4,
      },
    ],
  },
  options: {
    responsive: true,
    animation: false, // Desactiva animaciones para actualizaciones rápidas
    plugins: {
      legend: { display: true },
    },
    scales: {
      x: { title: { display: true, text: 'Tiempo' } },
      y: { title: { display: true, text: 'Valor' } },
    },
  },
});

const chart2 = new Chart(chart2Ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Variable 2',
        data: [],
        borderColor: 'blue',
        tension: 0.4,
      },
    ],
  },
  options: {
    responsive: true,
    animation: false,
    plugins: {
      legend: { display: true },
    },
    scales: {
      x: { title: { display: true, text: 'Tiempo' } },
      y: { title: { display: true, text: 'Valor' } },
    },
  },
});

// Cargar sensores en el dropdown
async function loadSensors() {
  try {
    const response = await fetch(`${API_BASE_URL}/devices`);
    if (!response.ok) {
      throw new Error(`Error en la solicitud: ${response.status}`);
    }

    const sensors = await response.json();
    console.log('Sensores disponibles:', sensors);

    // Llena el dropdown
    sensorSelect.innerHTML = '';
    sensors.forEach((sensor) => {
      const option = document.createElement('option');
      option.value = sensor.device_id;
      option.textContent = `${sensor.device_name}`;
      sensorSelect.appendChild(option);
    });

    // Seleccionar el primer sensor automáticamente si existen sensores
    if (sensors.length > 0) {
      sensorSelect.value = sensors[0].device_id;
      updateCharts(sensors[0].device_id);
      startAutoRefresh(); // Inicia el auto refresco
    }
  } catch (error) {
    console.error('Error al cargar sensores:', error);
  }
}

// Actualizar gráficos
async function updateCharts(sensorId) {
  if (!sensorId) return;

  loadingSpinner.style.display = 'block';

  try {
    const response = await fetch(`${API_BASE_URL}/device_parameters/${sensorId}`);
    if (!response.ok) {
      throw new Error(`Error en la solicitud: ${response.status}`);
    }

    const data = await response.json();
    console.log('Datos cargados:', data);

    if (data && Array.isArray(data) && data.length > 0) {
      // Extraer datos para gráficos
      timestamps = data.map((d) => new Date(d.updated_at).toLocaleString());
      chart1Data = data.map((d) => d.data_1);
      chart2Data = data.map((d) => d.data_2);

      // Limitar a 10 puntos máximo
      if (chart1Data.length > 10) {
        chart1Data = chart1Data.slice(-10);
        timestamps = timestamps.slice(-10);
      }

      if (chart2Data.length > 10) {
        chart2Data = chart2Data.slice(-10);
      }

      // Actualizar gráficos
      chart1.data.labels = timestamps;
      chart1.data.datasets[0].data = chart1Data;
      chart1.update();

      chart2.data.labels = timestamps;
      chart2.data.datasets[0].data = chart2Data;
      chart2.update();

      // Actualizar últimos datos
      lastVariable1.textContent = chart1Data[chart1Data.length - 1] || '--';
      lastVariable2.textContent = chart2Data[chart2Data.length - 1] || '--';
    } else {
      console.warn('No se encontraron datos para el sensor seleccionado.');
    }
  } catch (error) {
    console.error('Error al actualizar gráficos:', error);
  } finally {
    loadingSpinner.style.display = 'none';
  }
}

// Auto refrescar gráficos cada X segundos sin cambiar el sensor seleccionado
function startAutoRefresh() {
  setInterval(() => {
    const selectedSensorId = sensorSelect.value; // Mantener el sensor actualmente seleccionado
    updateCharts(selectedSensorId);
  }, 10000); // Refrescar cada 10 segundos
}

// Detectar cambios en el dropdown
sensorSelect.addEventListener('change', (event) => {
  updateCharts(event.target.value);
});

// Cargar sensores al cargar la página
window.onload = loadSensors;
