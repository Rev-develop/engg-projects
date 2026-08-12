//------------------------------------------------------------------------------------//
//                       ESP32 - DHT22 - LCD I2C - NÚT NHẤN - LED - RELAY              //
//                                                                                    //
// Mô tả:                                                                             //
// - Đọc giá trị nhiệt độ và độ ẩm từ cảm biến DHT22.                                  //
// - Hiển thị thông tin lên màn hình LCD I2C 16x2.                                    //
// - In thông tin nhiệt độ, độ ẩm ra Serial Monitor.                                   //
// - Điều khiển một đèn LED ON/OFF bằng nút nhấn (nhấn để đảo trạng thái).            //
// - Điều khiển một Relay dựa trên ngưỡng nhiệt độ (ví dụ: bật quạt khi nhiệt độ > 30°C).//
//                                                                                    //
// Kết nối phần cứng (gợi ý cho ESP32):                                               //
// - DHT22:                                                                           //
//   + VCC -> 3.3V hoặc 5V (kiểm tra datasheet của module DHT22)                      //
//   + DATA -> GPIO2 (có thể thay đổi trong #define DHTPIN)                           //
//   + GND -> GND                                                                     //
//   (Cần một điện trở kéo lên 10K giữa VCC và DATA nếu module không có sẵn)           //
// - LCD I2C:                                                                         //
//   + VCC -> 5V (thường là 5V cho LCD I2C)                                           //
//   + GND -> GND                                                                     //
//   + SDA -> GPIO21 (SDA mặc định của ESP32)                                         //
//   + SCL -> GPIO22 (SCL mặc định của ESP32)                                         //
// - Nút nhấn:                                                                        //
//   + Một chân -> GPIO25 (có thể thay đổi trong buttonPin)                            //
//   + Chân còn lại -> GND                                                            //
//   (Sử dụng điện trở kéo lên nội INPUT_PULLUP)                                       //
// - LED:                                                                             //
//   + Anode (chân dài) -> Điện trở (ví dụ 220 Ohm) -> GPIO26 (LEDPin)                //
//   + Cathode (chân ngắn) -> GND                                                     //
// - Relay Module:                                                                    //
//   + VCC -> 5V (hoặc theo điện áp cuộn hút của relay)                               //
//   + GND -> GND                                                                     //
//   + IN  -> GPIO5 (relayPin)                                                        //
//   (Lưu ý: Một số module relay kích hoạt mức LOW, một số kích hoạt mức HIGH)         //
//------------------------------------------------------------------------------------//

#include <Wire.h>             // Thư viện cho giao tiếp I2C (cần cho LCD I2C)
#include <LiquidCrystal_I2C.h> // Thư viện cho màn hình LCD I2C
#include <DHT.h>              // Thư viện cho cảm biến DHT

// --- Cấu hình cảm biến DHT ---
#define DHTPIN 2      // Chân DATA của cảm biến DHT nối với ESP32 (ví dụ: GPIO2)
#define DHTTYPE DHT22 // Loại cảm biến DHT (DHT11, DHT21, DHT22)
DHT dht(DHTPIN, DHTTYPE); // Khởi tạo đối tượng cảm biến DHT

// --- Cấu hình màn hình LCD I2C ---
// Địa chỉ I2C thường là 0x27 hoặc 0x3F. Kiểm tra bằng I2C Scanner nếu không chắc.
// 16 ký tự, 2 dòng.
LiquidCrystal_I2C lcd(0x27, 16, 2);

// --- Cấu hình chân cho Nút nhấn và LED ---
const int buttonPin = 25; // Chân GPIO của ESP32 nối với nút nhấn
const int LEDPin    = 26; // Chân GPIO của ESP32 nối với LED

// Biến lưu trạng thái của LED và nút nhấn
int ledState           = LOW; // Trạng thái hiện tại của LED (LOW = TẮT, HIGH = BẬT)
int lastButtonState;          // Trạng thái trước đó của nút nhấn
int currentButtonState;       // Trạng thái hiện tại của nút nhấn

// --- Cấu hình chân cho Relay ---
const int relayPin = 5;      // Chân GPIO của ESP32 nối với chân IN của module Relay
const float TEMPERATURE_THRESHOLD = 30.0; // Ngưỡng nhiệt độ để kích hoạt relay (ví dụ: 30°C)
                                          // Thay đổi giá trị này theo nhu cầu

void setup() {
  Serial.begin(9600); // Khởi động giao tiếp Serial ở tốc độ 9600 baud
  Serial.println("--- Khoi dong chuong trinh ---");

  // Khởi tạo màn hình LCD
  lcd.init();      // Khởi tạo LCD (quan trọng hơn begin cho một số thư viện)
  lcd.backlight(); // Bật đèn nền LCD
  lcd.clear();     // Xóa màn hình LCD
  lcd.setCursor(0, 0);
  lcd.print("Dang khoi tao...");

  // Khởi tạo cảm biến DHT
  dht.begin();
  Serial.println("Khoi tao DHT xong.");

  // Cấu hình chân cho nút nhấn và LED
  pinMode(buttonPin, INPUT_PULLUP); // Đặt chân nút nhấn là INPUT với điện trở kéo lên nội
                                    // Khi không nhấn, đọc được HIGH. Khi nhấn (nối GND), đọc được LOW.
  pinMode(LEDPin, OUTPUT);          // Đặt chân LED là OUTPUT
  
  // Đọc trạng thái ban đầu của nút nhấn
  currentButtonState = digitalRead(buttonPin);
  lastButtonState = currentButtonState; // Khởi tạo trạng thái trước đó

  // Đặt trạng thái ban đầu cho LED (TẮT)
  digitalWrite(LEDPin, ledState);
  Serial.println("Khoi tao nut nhan & LED xong.");

  // Cấu hình chân cho Relay
  pinMode(relayPin, OUTPUT);
  // Đặt trạng thái ban đầu cho Relay (ví dụ: TẮT)
  // Giả sử relay kích hoạt ở mức LOW (bật) và tắt ở mức HIGH
  // Nếu relay của bạn kích hoạt ở mức HIGH, đảo ngược logic này
  digitalWrite(relayPin, HIGH); // Tắt relay ban đầu
  Serial.println("Khoi tao Relay xong.");
  
  delay(1000); // Chờ một chút để các cảm biến ổn định
  lcd.clear();
}

void loop() {
  // Nên có một khoảng trễ giữa các lần đọc DHT, đặc biệt là DHT22 (ít nhất 2 giây)
  // DHT11 có thể đọc nhanh hơn (1 giây)
  delay(2000); 

  // Đọc giá trị độ ẩm và nhiệt độ từ cảm biến
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature(); // Mặc định là Celsius

  // Kiểm tra xem có đọc được dữ liệu từ cảm biến không
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Loi: Khong doc duoc du lieu tu cam bien DHT!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Loi DHT!");
    return; // Thoát khỏi vòng lặp hiện tại nếu có lỗi
  }

  // --- Điều khiển Relay dựa trên nhiệt độ ---
  // Ví dụ: Bật relay (ví dụ: quạt) nếu nhiệt độ > ngưỡng, tắt nếu <= ngưỡng
  // Giả sử: relay module kích hoạt khi chân IN ở mức LOW (phổ biến)
  if (temperature > TEMPERATURE_THRESHOLD) {
    digitalWrite(relayPin, LOW); // Bật relay
    Serial.println("Nhiet do cao -> BAT Relay");
  } else {
    digitalWrite(relayPin, HIGH); // Tắt relay
    Serial.println("Nhiet do thap -> TAT Relay");
  }

  // --- Hiển thị lên màn hình LCD ---
  // lcd.clear(); // Không nên clear() trong loop() liên tục vì gây nhấp nháy
                // Chỉ clear() khi cần thiết hoặc định kỳ (ví dụ, mỗi phút)
  
  // Hiển thị nhiệt độ
  lcd.setCursor(0, 0); // Cột 0, dòng 0
  lcd.print("Temp: ");
  lcd.print(temperature, 1); // In với 1 chữ số thập phân
  lcd.print((char)223);      // Ký tự độ (°)
  lcd.print("C   ");         // Thêm khoảng trắng để xóa ký tự cũ nếu số mới ngắn hơn

  // Hiển thị độ ẩm
  lcd.setCursor(0, 1); // Cột 0, dòng 1
  lcd.print("Humi: ");
  lcd.print(humidity, 1);  // In với 1 chữ số thập phân
  lcd.print(" %   ");      // Thêm khoảng trắng

  // --- In ra Serial Monitor ---
  Serial.print("Nhiet do: ");
  Serial.print(temperature);
  Serial.print(" *C, Do am: ");
  Serial.print(humidity);
  Serial.println(" %");

  // --- Xử lý nút nhấn để điều khiển LED ---
  lastButtonState = currentButtonState;         // Lưu trạng thái cũ
  currentButtonState = digitalRead(buttonPin); // Đọc trạng thái mới

  // Kiểm tra nếu có sự thay đổi trạng thái từ HIGH xuống LOW (nút được nhấn)
  if (lastButtonState == HIGH && currentButtonState == LOW) {
    Serial.println("Nut nhan da duoc bam!");
    
    // Đảo trạng thái của LED
    ledState = !ledState; // Nếu ledState là LOW, nó sẽ thành HIGH, và ngược lại
    
    // Điều khiển LED theo trạng thái mới
    digitalWrite(LEDPin, ledState);
    
    if(ledState == HIGH) {
      Serial.println("LED: BAT");
    } else {
      Serial.println("LED: TAT");
    }
  }
}