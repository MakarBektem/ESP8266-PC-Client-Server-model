#include <ESP8266WiFi.h>    // библиотека для создания и работы с Wi-Fi сервером
#include "ArduinoJson.h"    // библиотека для работы с JSON пакетами
#include <Wire.h>   // библиотека для связи с датчиками через интерфейс I2C
#include <SFE_BMP180.h>   // библиотека для управления барометром
#include <Adafruit_Sensor.h>    // библиотека для датчиков Adafruit
#include <Adafruit_ADXL345_U.h>   // библиотека для управления акселерометром
#include <SparkFun_APDS9960.h>    // библиотека для работы с датчиком жестов
#include <FastLED.h>    // библиотека для управления светодиодной лентой


SFE_BMP180 pressure;  // создание экземпляра класса SFE_BMP180 для работы с барометром
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345); // создание объекта, экземпляр класса ADXL345_U для работы с акселерометром
SparkFun_APDS9960 apds = SparkFun_APDS9960(); // создание объекта, экземпляр класса SparkFun_APDS9960 для работы с датчиком жестов

int gesture;

const char* ssid = "RT-GPON-B750";   // SSID
const char* password = "HFmk4UdK";  // пароль

WiFiServer server(10000); // создание сервера, что общается по указанному порту

//объявление констант (названий выходам 12 (D6), 13 (D7), 15 (D8))
#define PIN_LED1 12
#define PIN_LED2 13
#define PIN_LED3 15

#define NUM_LEDS_IN_STRIPLINE 8   // количество светодиодов на ленте
#define DATA_PIN 16   // пин для подключения ленты
CRGB ledsLine[NUM_LEDS_IN_STRIPLINE];   // экземпляр класса CRGB
int stripColors[NUM_LEDS_IN_STRIPLINE]; // массив цветов светодиодов в ленте

// переменые для принятия пакетов с компьютера
int i = 0;
char data[70];

void setup()
{
  WiFi.begin(ssid, password);    // поключение к точке доступа
  server.begin();   // сервер начинает "слушать" входящие запросы
  // настройка датчика жестов
  apds.init();
  apds.enableGestureSensor(true);
  // перевод цифровых портов со светодиодами в режим вывода
  pinMode(PIN_LED1, OUTPUT);
  pinMode(PIN_LED2, OUTPUT);
  pinMode(PIN_LED3, OUTPUT);
  // настройка светодиодной ленты
  FastLED.addLeds <WS2812, DATA_PIN, GRB>(ledsLine, NUM_LEDS_IN_STRIPLINE).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(50);
}

void loop()
{
  // получение и запись клиента
  WiFiClient client = server.available();
// проверка, существует ли клиент
  if (client)
  { 
    while (client.connected())  // проверка, подключен ли клиент
    { 
      while (client.available() > 0)  // проверка, есть ли байты для чтения от клиента
      { 
        data[i] = static_cast<char>(client.read()); // считываем и записываем первый на очереди байт
        i++;
      }
      DynamicJsonDocument parsed(1024); // выделение памяти для принятой JSON строки
      deserializeJson(parsed, data);  // десериализация принятого JSON пакета
      //парсинг пакета JSON
      // получение сигналов на дискретные светодиоды
      int LED1_status = parsed["LED1"];
      int LED2_status = parsed["LED2"];
      int LED3_status = parsed["LED3"];
      // получение массива сигналов на светодиодную ленту
      for (int i = 0; i < NUM_LEDS_IN_STRIPLINE - 1; i++)
      {
        stripColors[i] = parsed["LEDSTRIP"][i];  // запись цветов светодиодов в ленте
      }
      // смена цветов дискретных светодиодов
      digitalWrite(PIN_LED1, LED1_status);
      digitalWrite(PIN_LED2, LED2_status);
      digitalWrite(PIN_LED3, LED3_status);
      // смена цветов светодиодов в ленте
      for (int a = 0; a < NUM_LEDS_IN_STRIPLINE; a++)
      {
        changeLedInStrip(a, stripColors[a]);
      }
//  выделение памяти для отправляемого JSON объекта
      DynamicJsonDocument doc(64); 

      double Pr = getPressure();  // измерение давления
// создание структуры для занесения в неё показаний акселерометра
      sensors_event_t event;  
// получение текущих показаний акселерометра
      accel.getEvent(&event);
      double aX = event.acceleration.x;
      double aY = event.acceleration.y;
      double aZ = event.acceleration.z;
      
// получение текущих показаний датчика жестов
      gesture = apds.readGesture();
      
// создание пар ключ-значение (сенсор-показания) в структуре JSON
      doc["Pressure"] = Pr; // давление в гПа
      doc["Acceleration"][0] = aX;  // ускорение Х в м/с^2
      doc["Acceleration"][1] = aY;  // ускорение Y в м/с^2
      doc["Acceleration"][0] = aZ;  // ускорение Z в м/с^2
      doc["Gesture"][0] = gesture;  // жест

      String output;  // создание переменной для хранения JSON пакета
      serializeJson(doc, output);   // запись JSON пакета в ранее созданную переменную
      for (int i = 0; i < output.length(); i++)
      {
        client.write(output[i]);
      }
      client.write("   ");
    }
  }
}

// функция измерения давления
double getPressure()
{
  char status;
  double T, P;
  pressure.startTemperature(); // запуск измерения температуры
  delay(status);  // ожидание завершения измерений
  pressure.getTemperature(T);  // извлечение данных о температуре
  pressure.startPressure(3);  // запуск измерения давления
  delay(status);
  pressure.getPressure(P, T); // извлечение данных о давлении
  return (P);   //возвращение измеренного значения в мбар (гПа)
}

// функция смены цветов светодиодной ленты
void changeLedInStrip(int ledPos, int ledColor)
{
  switch (ledColor)
  {
    case 1:
      ledsLine[ledPos] = CRGB::Red;
      FastLED.show();
      break;
    case 2:
      ledsLine[ledPos] = CRGB::Green;
      FastLED.show();
      break;
    case 3:
      ledsLine[ledPos] = CRGB::Blue;
      FastLED.show();
      break;
  }
}
