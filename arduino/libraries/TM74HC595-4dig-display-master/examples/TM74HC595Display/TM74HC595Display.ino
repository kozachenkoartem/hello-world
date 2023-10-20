int SCLK = 5;
int RCLK = 4;
int DIO = 3;

byte digitBuffer[4];
  
void setup(){  
  pinMode(RCLK, OUTPUT);
  pinMode(SCLK, OUTPUT);
  pinMode(DIO, OUTPUT);  
}


void loop(){  
  // заполняем массив
  digitBuffer[0] = 1; 
  digitBuffer[1] = 2;
  digitBuffer[2] = 3;
  digitBuffer[3] = 4;
  
  // однократно выводим данные из массива на 7сигмент
  // тоесть функция должна постоянно крутится.
  showDisplay(); 
  
}

void showDisplay(){
  
  const byte digit[10] = {  // маска для 7 сигментного индикатора  
      0b11000000, // 0
      0b11111001, // 1
      0b10100100, // 2
      0b10110000, // 3
      0b10011001, // 4
      0b10010010, // 5
      0b10000010, // 6
      0b11111000, // 7
      0b10000000, // 8
      0b10010000, // 9 
  };

  const byte chr[4] = { // маска для разряда
      0b00001000,  
      0b00000100,  
      0b00000010,  
      0b00000001  
  };

  // отправляем в цикле по два байта в сдвиговые регистры
  for(byte i = 0; i <= 3; i++){ 
    digitalWrite(RCLK, LOW); // открываем защелку
      shiftOut(DIO, SCLK, MSBFIRST, digit[digitBuffer[i]]);  // отправляем байт с "числом"
      shiftOut(DIO, SCLK, MSBFIRST, chr[i]);   // включаем разряд
    digitalWrite(RCLK, HIGH); // защелкиваем регистры
    delay(1); // ждем немного перед отправкой следующего "числа"
  }  
}

