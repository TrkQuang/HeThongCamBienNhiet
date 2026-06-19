#include <ESP8266WiFi.h>
#include <time.h>
#include <FirebaseESP8266.h>
#include "DHT.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

//================ CẤU HÌNH MÀN HÌNH OLED =======
#define SCREEN_WIDTH 128 // Chiều rộng màn hình OLED (pixel)
#define SCREEN_HEIGHT 64 // Chiều cao màn hình OLED (pixel)
#define OLED_RESET -1    // Dùng -1 nếu màn hình dùng chung chân Reset với ESP
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

//=============== FIREBASE SETUP ===============
#define FIREBASE_HOST "hethongcambiennhiet-default-rtdb.asia-southeast1.firebasedatabase.app"
#define FIREBASE_AUTH "FxnWmxRtKDz7XxEIFz3MdozuXusXm0WIywInlKjT"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

//================ CẤU HÌNH NHIỆT ĐỘ DHT11 =====
#define DHTPIN 2 // Chân số 2 (Tương ứng với D4 trên mạch NodeMCU)
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//================ THÔNG TIN WIFI ===============
const char* ten_wifi = "Phuc Tai";
const char* pass_wifi = "01012006";

//================ BIẾN TOÀN CỤC ================
unsigned long thoi_gian_bat_dau = 0;
unsigned long thoi_gian_check_fb = 0; 
long thoi_gian_do = 300000;          // Mặc định 5 phút
String address_hien_tai = "chưa có"; // Mặc định chưa có
long id_chip;

//=============== SETUP ========================
void setup() {
  Serial.begin(115200);
  dht.begin();
  
  id_chip = ESP.getChipId();
  Serial.print("ID Chip: ");
  Serial.println(id_chip);

  // 0. Khởi động màn hình OLED
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("LỖI: KHÔNG TÌM THẤY MÀN HÌNH OLED!");
  } else {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(0, 20);
    display.println("Dang ket noi WiFi...");
    display.display();
  }
  
  // 1. Kết nối WiFi
  WiFi.begin(ten_wifi, pass_wifi);
  Serial.print("ĐANG KẾT NỐI WIFI...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nKẾT NỐI THÀNH CÔNG");

  // In ra OLED khi có WiFi
  display.clearDisplay();
  display.setCursor(0, 20);
  display.println("WiFi: OK!");
  display.println("Ket noi Firebase...");
  display.display();

  // 2. Đồng bộ thời gian thực
  configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov"); // UTC+7
  
  // 3. Kết nối Firebase
  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  Serial.println("ĐÃ KẾT NỐI VỚI FB");

  // In ra OLED khi hoàn tất Setup
  display.clearDisplay();
  display.setCursor(0, 20);
  display.println("He Thong San Sang!");
  display.display();
  delay(1000);

  // Kích hoạt đo lần đầu tiên ngay khi vừa bật máy
  ThucHienDoVaGui();
}

//=============== HÀM XỬ LÝ ĐO VÀ ĐẨY DỮ LIỆU ===
void ThucHienDoVaGui() {
  float nhiet_do = dht.readTemperature(); 
  float do_am = dht.readHumidity();
  String canh_bao = "normal";

  // Bắt lỗi cảm biến
  if (isnan(nhiet_do) || isnan(do_am)) {
    canh_bao = "Lỗi cảm biến DHT11";
    nhiet_do = -999.0;
    do_am = -999.0;
  }

  // Lấy giờ chuẩn ISO 8601
  time_t now = time(nullptr);
  struct tm* timeinfo = localtime(&now);
  char timeStringBuff[25];
  strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%dT%H:%M:%S", timeinfo);
  String thoi_gian_chuan = String(timeStringBuff);

  // ================= CẬP NHẬT LÊN OLED =================
  display.clearDisplay();
  
  // Hiển thị Nhiệt độ
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Nhiet do: ");
  display.setTextSize(2); // Phóng to số cho dễ nhìn
  display.setCursor(0, 12);
  if(nhiet_do == -999.0) display.print("ERR"); 
  else display.print(nhiet_do);
  display.print(" C");

  // Hiển thị Độ ẩm
  display.setTextSize(1);
  display.setCursor(0, 35);
  display.print("Do am: ");
  display.setTextSize(2);
  display.setCursor(0, 47);
  if(do_am == -999.0) display.print("ERR"); 
  else display.print(do_am);
  display.print(" %");

  display.display(); // Lệnh này bắt buộc để đẩy chữ ra màn hình
  // =====================================================

  // Đóng gói JSON
  FirebaseJson json;
  json.set("device_id", String(id_chip));
  json.set("temp", nhiet_do);
  json.set("humidity", do_am);
  json.set("ts", thoi_gian_chuan);
  json.set("wanning", canh_bao);         // Báo cáo tình trạng lỗi của dht

  // PUSH lên nhánh lưu trữ
  String pathData = "/sensor_data/" + String(id_chip);
  if (Firebase.pushJSON(fbdo, pathData, json)) {
    Serial.print("Chu ky do (ms): ");
    Serial.println(thoi_gian_do);
    Serial.println("-> PUSH DỮ LIỆU THÀNH CÔNG! Trạng thái: " + canh_bao);
  } else {
    Serial.println("-> LỖI PUSH: " + fbdo.errorReason());
  }
  Serial.println("------------------------------------------------");
}

//=============== VÒNG LẶP CHÍNH =================
void loop() {
  unsigned long hien_tai = millis(); 

  // -------------------------------------------------------------
  // LUỒNG 1: KIỂM TRA LỆNH TỪ APP TRÊN FIREBASE (Mỗi 3 giây)
  // -------------------------------------------------------------
  if (hien_tai - thoi_gian_check_fb >= 3000) {
    thoi_gian_check_fb = hien_tai; 
    String pathSetting = "/settings/" + String(id_chip);

    // 1.1 Kiểm tra và cập nhật chu kỳ đo (thoi_gian_do)
    if (Firebase.getInt(fbdo, pathSetting + "/samplingInterval")) {
      thoi_gian_do = fbdo.intData() * 60000L;
    } 
    
    // 1.2 Kiểm tra và thực hiện đo (khi có lệnh đo từ nút ấn)
    if (Firebase.getInt(fbdo, pathSetting + "/forceMeasure")) {
      if(fbdo.intData() == 1) {
        Serial.println(">>> NHẬN LỆNH ĐO KHẨN CẤP TỪ APP <<<");
        ThucHienDoVaGui();
        Firebase.setInt(fbdo, pathSetting + "/forceMeasure", 0);    
        thoi_gian_bat_dau = millis();
      }
    } 
  }

  // -------------------------------------------------------------
  // LUỒNG 2: ĐO TỰ ĐỘNG THEO CHU KỲ (Nếu không có lệnh khẩn cấp)
  // -------------------------------------------------------------
  if (hien_tai - thoi_gian_bat_dau >= thoi_gian_do) {
    Serial.println(">>> ĐẾN HẠN CHU KỲ TỰ ĐỘNG <<<");
    ThucHienDoVaGui(); 
    thoi_gian_bat_dau = hien_tai; // Đặt lại mốc thời gian
  }
}