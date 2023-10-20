#include <DallasTemperature.h>
#include <EEPROM.h>
#include "GyverTimers.h"

#define SCLK 5  // пины ардуины
#define RCLK 4
#define DIO 3

#define ONE_WIRE_BUS 6
#define PIN_RELAY 7

#define BUTTON_1 8
#define BUTTON_2 9
#define BUTTON_3 10
#define BUTTON_4 11
#define DELTA_ADDR 10
#define TARGET_ADDR 20

static const int default_delta = 15;
static const int default_target = 5;

int delta = default_delta;
int target = default_target;

// Создаём экземпляр класса для нашей шины и ссылку на него
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

size_t current_index = 0;

static const byte chr[4] = {  // маска для разряда
  0b00001000,
  0b00000100,
  0b00000010,
  0b00000001
};

static const byte digit[11] = {
  // маска для 7 сигментного индикатора
  0b11000000,  // 0
  0b11111001,  // 1
  0b10100100,  // 2
  0b10110000,  // 3
  0b10011001,  // 4
  0b10010010,  // 5
  0b10000010,  // 6
  0b11111000,  // 7
  0b10000000,  // 8
  0b10010000,  // 9
  0b10111111,  // -
};

static const byte t_symbol = 0b10110001;
static const byte d_symbol = 0b10100001;

byte digitBuffer[4];

void setup() {

  Serial.begin(9600);

  pinMode(RCLK, OUTPUT);
  pinMode(SCLK, OUTPUT);
  pinMode(DIO, OUTPUT);
  pinMode(PIN_RELAY, OUTPUT);

  relay_off();

  pinMode(BUTTON_1, INPUT_PULLUP);  // подключаем тактовые кнопки
  pinMode(BUTTON_2, INPUT_PULLUP);
  pinMode(BUTTON_3, INPUT_PULLUP);
  pinMode(BUTTON_4, INPUT_PULLUP);

  sensors.begin();  // Инициализация шины

  Timer1.setPeriod(5555);
  Timer1.enableISR();

  target = EEPROM.read(TARGET_ADDR);
  delta = EEPROM.read(DELTA_ADDR);


  Serial.println(EEPROM[DELTA_ADDR]);       // выведет 200
  Serial.println(EEPROM[TARGET_ADDR]);       // выведет 200

  if (target > 100) { // first read
    target = default_target;
    EEPROM.update(TARGET_ADDR, target);
  }

  if (delta > 100) {  // first read
    delta = default_delta;
    EEPROM.update(DELTA_ADDR, delta);
  }
}

// **************************************************
//                 TIMER
// **************************************************

ISR(TIMER1_A) {
  showNextDisplayDidgit();
}


// **************************************************
//                 DISPLAY
// **************************************************


void float_to_buffer(float n) {

  memset(digitBuffer, 0b11111111, 4);

  bool negative = false;
  if (n < 0) {
    negative = true;
    n *= -1.0;
  }

  float tmp;

  modff(modff(n, &n) * 10, &tmp);

  size_t rover = 3;

  digitBuffer[rover] = digit[uint8_t(tmp)];
  rover--;

  int i = (int)n;

  if(i == 0) {
    digitBuffer[2] = digit[0] & 0b01111111;  // point
    digitBuffer[1] = negative ? digit[10] : 0b11111111;
    return;
  }

  while (i > 0) {
    digitBuffer[rover] = digit[i % 10];
    i = i / 10;
    rover--;
  }

  digitBuffer[2] = digitBuffer[2] & 0b01111111;  // point
  digitBuffer[rover] = negative ? digit[10] : 0b11111111;
}

void showNextDisplayDidgit() {
  digitalWrite(RCLK, LOW);                                    // открываем защелку
  shiftOut(DIO, SCLK, MSBFIRST, digitBuffer[current_index]);  // отправляем байт с "числом"
  shiftOut(DIO, SCLK, MSBFIRST, chr[current_index]);          // включаем разряд
  digitalWrite(RCLK, HIGH);                                   // защелкиваем регистры
  current_index++;

  if (current_index > 3) current_index = 0;
}

// **************************************************
//                 RELAY
// **************************************************

void relay_on() {
  digitalWrite(PIN_RELAY, LOW);
}

void relay_off() {
  digitalWrite(PIN_RELAY, HIGH);
}

// **************************************************
//                 BUTTONS
// **************************************************

enum display_mode {
  dm_show_delta,
  dm_show_target,
  dm_show_temperature
};

display_mode mode = dm_show_temperature;

size_t buttons_pins[4] = { BUTTON_1, BUTTON_2, BUTTON_4, BUTTON_3 };
bool buttons_states[4];


void next_display_state() {
  if (mode == dm_show_temperature) {
    mode = dm_show_delta;
    show_delta();
    return;
  }

  if (mode == dm_show_delta) {
    mode = dm_show_target;
    show_target();
    return;
  }

  if (mode == dm_show_target) {
    mode = dm_show_temperature;
  }
}

void value_up() {
  if (mode == dm_show_delta) {
    delta++;
    EEPROM.update(DELTA_ADDR, delta);
    show_delta();
  }

  if (mode == dm_show_target) {
    target++;
    EEPROM.update(TARGET_ADDR, target);
    show_target();
  }
}

void value_down() {
  if (mode == dm_show_delta) {
    delta--;
    EEPROM.update(DELTA_ADDR, delta);
    show_delta();
  }

  if (mode == dm_show_target) {
    target--;
    EEPROM.update(TARGET_ADDR, target);
    show_target();
  }
}

void button_state_changed(size_t button, bool state) {
  switch (button) {
    case 1:
      {
        mode = state ? dm_show_target : dm_show_temperature;
        if (state) show_target();
        break;
      }
    case 2:
      {
        if (state) next_display_state();
        break;
      }
    case 3:
      {
        if (state) value_down();
        break;
      }
    case 4:
      {
        if (state) value_up();
        break;
      }
  }
}

void check_buttons() {
  for (size_t i = 0; i < 4; i++) {
    bool state = digitalRead(buttons_pins[i]);
    if (buttons_states[i] != state) {
      buttons_states[i] = state;
      button_state_changed(i + 1, !state);
    }
  }
}

// **************************************************
//                 LOOP
// **************************************************

float tmp_outside = 0;
float tmp_inside = 0;

static const int max_time = 6000;
int time = 0;
int sensor_time = 0;


void show_delta() {
  float_to_buffer(delta);
  digitBuffer[0] = d_symbol;
}

void show_target() {
  float_to_buffer(target);
  digitBuffer[0] = t_symbol;
}

void show_temperature() {

  if (sensor_time > 1000) {
    sensors.requestTemperatures();
    sensor_time = 0;
    tmp_outside = sensors.getTempCByIndex(0);
    tmp_inside = sensors.getTempCByIndex(1);
  }
  if (time > max_time / 2) {
    float_to_buffer(tmp_outside);
  } else {
    float_to_buffer(tmp_inside);
  }
}

void check_temperature() {
  if (tmp_inside >= (tmp_outside + delta) && tmp_inside > target) {
    relay_on();
  } else {
    relay_off();
  }
}


void loop() {
  if (mode == dm_show_temperature) {
    show_temperature();
  }
  check_buttons();
  check_temperature();

  delay(10);
  time += 10;
  sensor_time += 10;

  if (time >= max_time) time = 0;
}
