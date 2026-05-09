#include <ESP8266WiFi.h>
#include <time.h>

// ================= CẤU HÌNH WI-FI =================
const char* ssid = "Nguyễn Đình Chương";      // Đổi thành tên Wi-Fi nhà bạn
const char* password = "11111111";  // Đổi thành mật khẩu Wi-Fi

// ================= CẤU HÌNH THỜI GIAN ĐO =================
unsigned long previousMillis = 0;
// 300000 mili-giây = 5 phút. 
// Tạm thời tui để 10000 (10 giây) để bạn test cho lẹ, khi báo cáo thì đổi lại 300000
const long interval = 10000; 

// ================= SETUP (Chạy 1 lần) =================
void setup() {
  Serial.begin(115200);
  Serial.println("\n--- KHOI DONG HE THONG ---");

  // 1. Kết nối Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Dang ket noi Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nKet noi thanh cong! IP: " + WiFi.localIP().toString());

  // 2. Cấu hình lấy giờ từ Internet (NTP)
  // 7 * 3600 là bù giờ UTC+7 cho múi giờ Việt Nam
  configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  Serial.println("Dang dong bo thoi gian...");
  delay(2000); // Chờ 2 giây để mạch kịp tải giờ về
}

// ================= LOOP (Chạy lặp lại liên tục) =================
void loop() {
  // Lấy thời gian hiện tại của mạch (tính bằng mili-giây)
  unsigned long currentMillis = millis();

  // Kiểm tra xem đã trôi qua đủ thời gian cài đặt chưa (5 phút / 10 giây)
  if (currentMillis - previousMillis >= interval) {
    // Lưu lại cột mốc thời gian mới
    previousMillis = currentMillis;
    
    // Gọi hàm đo và gửi dữ liệu
    doVaGuiDuLieu();
  }

  // Khúc này mạch vẫn "rảnh rỗi" chạy liên tục, sau này sẽ chèn code "Lắng nghe yêu cầu đo đột xuất" vào đây
}

// ================= HÀM XỬ LÝ DỮ LIỆU =================
void doVaGuiDuLieu() {
  // 1. Tạo dữ liệu giả lập (Vì chưa có DHT11)
  // Random nhiệt độ từ 28.0 đến 35.0, độ ẩm từ 60.0 đến 80.0
  float nhiet_do = random(280, 350) / 10.0; 
  float do_am = random(600, 800) / 10.0;

  // 2. Lấy giờ thực tế (Timestamp)
  time_t now = time(nullptr);
  struct tm* timeinfo = localtime(&now);
  char timeString[20];
  // Định dạng giờ: Năm-Tháng-Ngày Giờ:Phút:Giây
  strftime(timeString, sizeof(timeString), "%Y-%m-%d %H:%M:%S", timeinfo);

  // 3. Lấy ID duy nhất của mạch ESP8266
  String chipId = String(ESP.getChipId());

  // 4. Đóng gói tất cả thành chuỗi JSON
  String payload = "{";
  payload += "\"esp_id\":\"" + chipId + "\",";
  payload += "\"sensor_type\":\"DHT11\",";
  payload += "\"temperature\":" + String(nhiet_do, 1) + ",";
  payload += "\"humidity\":" + String(do_am, 1) + ",";
  payload += "\"timestamp\":\"" + String(timeString) + "\"";
  payload += "}";

  // 5. In ra Serial Monitor để kiểm tra trước (Sau này thay bằng lệnh gửi qua mạng)
  Serial.println("Ban tin moi: " + payload);
}