#include <WiFi.h>
#include <HTTPClient.h>
#include <ModbusMaster.h>

// Configuración del WiFi
const char* ssid = "Amanda 2.4G";  // Nombre de tu red WiFi
const char* password = "Gomezriquelmegomez12";  // Contraseña de tu red WiFi

// Dirección del servidor Flask en la Raspberry Pi
const char* serverUrl = "http://tinex3.site:5000/api/mediciones";  // Cambia la IP según sea necesario

// ID del dispositivo
const int deviceID = 121342;  // ID del dispositivo

// Configuración de Modbus RTU
#define RXD_PIN 16
#define TXD_PIN 13
#define CONTROL_PIN 2  // Pin para controlar el DE/RE del RS485
#define RS485_SERIAL Serial2

ModbusMaster node;

// Funciones de control de transmisión para RS485
void preTransmission() {
  digitalWrite(CONTROL_PIN, HIGH);  // Activar transmisión
}

void postTransmission() {
  digitalWrite(CONTROL_PIN, LOW);   // Activar recepción
}

void setup() {
  // Iniciar comunicación serial para depuración
  Serial.begin(115200);

  // Configurar pines de RS485
  pinMode(CONTROL_PIN, OUTPUT);
  digitalWrite(CONTROL_PIN, LOW);

  // Configurar comunicación RS485
  RS485_SERIAL.begin(9600, SERIAL_8N1, RXD_PIN, TXD_PIN);  // Configuración 8N1 según el sensor
  node.begin(1, RS485_SERIAL);           // Dirección del sensor
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  // Conectar al WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConectado a WiFi");
  Serial.print("Dirección IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // Leer datos del sensor Modbus RTU
    uint8_t result;
    float humedad = 0, temperatura = 0;

    result = node.readHoldingRegisters(0x0000, 2);  // Leer 2 registros: 0x0000 (humedad), 0x0001 (temperatura)

    if (result == node.ku8MBSuccess) {
      // Procesar datos leídos
      humedad = node.getResponseBuffer(0) / 10.0;      // Registro 0x0000 (dividir por 10 para el valor real)
      int16_t rawTemp = node.getResponseBuffer(1);     // Registro 0x0001
      temperatura = rawTemp / 10.0;                   // Dividir por 10 para el valor real

      Serial.print("Humedad: ");
      Serial.print(humedad);
      Serial.println(" %RH");
      Serial.print("Temperatura: ");
      Serial.print(temperatura);
      Serial.println(" °C");
    } else {
      Serial.println("Error leyendo Modbus");
      delay(5000);
      return;  // Intentar nuevamente después de 5 segundos
    }

    // Enviar datos al servidor Flask
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Crear el JSON con los datos incluyendo el ID del dispositivo
    String json = "{\"id_dispositivo\": " + String(deviceID) +
                  ", \"humedad\": " + String(humedad) +
                  ", \"temperatura\": " + String(temperatura) + "}";
    Serial.println("Enviando datos: " + json);

    // Enviar la solicitud POST
    int httpResponseCode = http.POST(json);

    // Verificar la respuesta del servidor
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Respuesta del servidor: " + response);
    } else {
      Serial.printf("Error al enviar datos: %d\n", httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi no conectado, intentando reconectar...");
    WiFi.begin(ssid, password);
  }

  // Esperar 10 segundos antes de la próxima lectura
  delay(1200000);
}
