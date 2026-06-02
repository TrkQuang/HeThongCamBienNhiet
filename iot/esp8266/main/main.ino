#include <ESP8266WiFi.h>
#include <time.h>
#include <FirebaseESP8266.h>
#include "DHT.h"

//=============== FIREBASE SETUP ===============
#define FIREBASE_HOST "hethongcambiennhiet-default-rtdb.asia-southeast1.firebasedatabase.app"
#define FIREBASE_AUTH "FxnWmxRtKDz7XxEIFz3MdozuXusXm0WIywInlKjT"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

//================ CẤU HÌNH NHIỆT ĐỘ DHT11 =====
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//================ THÔNG TIN WIFI ===============
const char* ten_wifi = "Nguyễn Đình Chương";
const char* pass_wifi = "11111111";

//================ BIẾN TOÀN CỤC ================
unsigned long thoi_gian_bat_dau = 0;
unsigned long thoi_gian_check_fb = 0; 
long thoi_gian_do = 30000;          // Mặc định 5 phút
String address_hien_tai = "chưa có"; // Mặc định chưa có
long id_chip;

//=============== SETUP ========================
void setup() {
  Serial.begin(115200);
  dht.begin();
  
  id_chip = ESP.getChipId();
  Serial.print("ID Chip: ");
  Serial.println(id_chip);
  
  // 1. Kết nối WiFi
  WiFi.begin(ten_wifi, pass_wifi);
  Serial.print("ĐANG KẾT NỐI WIFI...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nKẾT NỐI THÀNH CÔNG");

  // 2. Đồng bộ thời gian thực
  configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov"); // UTC+7
  
  // 3. Kết nối Firebase
  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  Serial.println("ĐÃ KẾT NỐI VỚI FB");
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

  // Đóng gói JSON
  FirebaseJson json;
  json.set("sensor_id", String(id_chip));
  json.set("temp", nhiet_do);
  json.set("humidity", do_am);
  json.set("timestamp", thoi_gian_chuan);
  json.set("address", address_hien_tai); // Lấy biến động cập nhật từ App
  json.set("wanning", canh_bao);         // Báo cáo tình trạng lỗi của dht

  // PUSH lên nhánh lưu trữ
  String pathData = "/iot/dht11_data/" + String(id_chip);
  if (Firebase.pushJSON(fbdo, pathData, json)) {
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
    String pathApp = "/app/" + String(id_chip);

    // 1.1 Kiểm tra và cập nhật vị trí (address)
    if (Firebase.getString(fbdo, pathApp + "/address")) {
      address_hien_tai = fbdo.stringData();
    }

    // 1.2 Kiểm tra và cập nhật chu kỳ đo (thoi_gian_do)
    if (Firebase.getInt(fbdo, pathApp + "/thoi_gian_do")) {
      thoi_gian_do = fbdo.intData();
    }

    // 1.3 Kiểm tra tín hiệu đo khẩn cấp (temp)
    if (Firebase.getInt(fbdo, pathApp + "/temp")) {
      int tinh_hieu = fbdo.intData();
      if (tinh_hieu == 1) {
        Serial.println(">>> APP YÊU CẦU ĐO NGAY LẬP TỨC! <<<");
        ThucHienDoVaGui(); 
        
        // Reset cờ báo động về 0 trên Firebase
        Firebase.setInt(fbdo, pathApp + "/temp", 0);
        
        // Reset lại đồng hồ đếm chu kỳ để tránh đo đúp
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