#include <WiFi.h>
#include <HTTPClient.h>

// Configuración de Wi-Fi
const char* ssid = "Amanda 2.4G";          // Reemplaza con tu SSID
const char* password = "Gomezriquelmegomez12"; // Reemplaza con tu contraseña

// URL del servidor al que se enviarán los datos
const char* serverURL = "http://tinex3.site:5000/api/mediciones";

// ID del dispositivo
const int deviceID = 121343; // ID único de tu dispositivo

// Intervalo de tiempo entre envíos de datos (en milisegundos)
const int intervalo = 1200000; // Enviar datos cada 10 segundos

// Prototipos de funciones
void conectarWiFi();
void enviarDatos(float temperatura, float humedad);

void setup() {
  Serial.begin(115200);

  // Conexión a la red Wi-Fi
  conectarWiFi();
}

void loop() {
  // Generar datos aleatorios para temperatura y humedad
  float temperatura = random(0, 50) + random(0, 10) / 10.0; // Temperatura entre 0 y 50°C
  float humedad = random(0, 100) + random(0, 10) / 10.0;    // Humedad entre 0 y 100%

  // Mostrar los datos generados en el monitor serie
  Serial.println("\nDatos generados:");
  Serial.print("ID del dispositivo: ");
  Serial.println(deviceID);
  Serial.print("Temperatura: ");
  Serial.print(temperatura);
  Serial.println(" °C");
  Serial.print("Humedad: ");
  Serial.print(humedad);
  Serial.println(" %");

  // Enviar los datos al servidor
  if (WiFi.status() == WL_CONNECTED) {
    enviarDatos(temperatura, humedad);
  } else {
    Serial.println("WiFi desconectado. Intentando reconectar...");
    conectarWiFi();
  }

  // Esperar antes de enviar los datos nuevamente
  delay(intervalo);
}

// Implementación de las funciones

void conectarWiFi() {
  Serial.print("Conectando a WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConexión WiFi establecida");
  Serial.print("Dirección IP: ");
  Serial.println(WiFi.localIP());
}

void enviarDatos(float temperatura, float humedad) {
  HTTPClient http;

  // Configurar la conexión al servidor
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  // Crear el payload en formato JSON
  String payload = "{";
  payload += "\"id_dispositivo\": " + String(deviceID) + ",";
  payload += "\"temperatura\": " + String(temperatura) + ",";
  payload += "\"humedad\": " + String(humedad) + ",";
  payload += "\"distancia\": null,";
  payload += "\"valor_random\": null";
  payload += "}";

  // Enviar la solicitud POST
  Serial.println("Enviando datos al servidor:");
  Serial.println(payload);

  int httpResponseCode = http.POST(payload);

  // Procesar la respuesta del servidor
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("Respuesta del servidor: ");
    Serial.println(response);
  } else {
    Serial.print("Error al enviar datos. Código HTTP: ");
    Serial.println(httpResponseCode);
  }

  // Finalizar la conexión HTTP
  http.end();
}
