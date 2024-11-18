#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// Configuración de Wi-Fi
const char* ssid = "Amanda 2.4G";           // Reemplaza con el SSID de tu red
const char* password = "Gomezriquelmegomez12";   // Reemplaza con la contraseña de tu red

// Configuración del sensor DHT11
#define DHTPIN 4           // Pin al que está conectado el DHT11
#define DHTTYPE DHT11      // Tipo de sensor: DHT11
DHT dht(DHTPIN, DHTTYPE);

// ID del dispositivo
const int deviceID = 121341;  // ID del dispositivo en la base de datos

// URL del servidor para enviar datos
const char* serverURL = "http://tinex3.site:5000/api/mediciones";

// Declaraciones de funciones
void conectarWiFi();
void enviarDatos(float temperature, float humidity);
void reconectarWiFi();

void setup() {
  Serial.begin(115200);

  // Inicializar el sensor DHT11
  dht.begin();

  // Conectar a la red Wi-Fi
  conectarWiFi();
}

void loop() {
  // Leer datos del sensor DHT11
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Verificar si la lectura fue exitosa
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Error al leer del sensor DHT11");
    delay(5000);  // Esperar antes de intentar nuevamente
    return;
  }

  // Mostrar datos en el monitor serie
  Serial.println("\nDatos del sensor DHT11:");
  Serial.print("ID del dispositivo: ");
  Serial.println(deviceID);
  Serial.print("Temperatura: ");
  Serial.print(temperature);
  Serial.println(" °C");
  Serial.print("Humedad: ");
  Serial.print(humidity);
  Serial.println(" %");

  // Enviar datos al servidor
  if (WiFi.status() == WL_CONNECTED) {
    enviarDatos(temperature, humidity);
  } else {
    Serial.println("WiFi desconectado. Intentando reconectar...");
    reconectarWiFi();
  }

  // Esperar 10 segundos antes de la próxima lectura
  delay(1200000);
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

void reconectarWiFi() {
  int retryCount = 0;
  while (WiFi.status() != WL_CONNECTED && retryCount < 10) {
    Serial.println("Intentando reconectar a WiFi...");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    delay(2000 * (retryCount + 1));  // Incrementar el tiempo de espera con cada intento
    retryCount++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Reconexión WiFi exitosa");
  } else {
    Serial.println("No se pudo reconectar a WiFi");
  }
}

void enviarDatos(float temperature, float humidity) {
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  // Crear el payload en formato JSON
  String payload = "{";
  payload += "\"id_dispositivo\": " + String(deviceID) + ",";
  payload += "\"temperatura\": " + String(temperature) + ",";
  payload += "\"humedad\": " + String(humidity);
  payload += "}";

  // Enviar POST request
  int httpResponseCode = http.POST(payload);

  if (httpResponseCode > 0) {
    Serial.print("Respuesta del servidor: ");
    Serial.println(httpResponseCode);

    // Procesar respuesta del servidor
    String response = http.getString();
    Serial.println("Respuesta: " + response);
  } else {
    Serial.print("Error al enviar datos. Código HTTP: ");
    Serial.println(httpResponseCode);
    if (httpResponseCode == -1) {
      Serial.println("Posible desconexión del servidor o fallo en la red.");
    }
  }

  http.end();
}
