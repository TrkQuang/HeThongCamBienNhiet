#include <ESP8266WiFi.h>
#include <time.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "DHT.h"
#include <math.h>

//================CẤU HÌNH NHIỆT ĐỘ DHT11=====
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
//================THÔNG TIN WIFI===============
const char* ten_wifi="Nguyễn Đình Chương";
const char* pass_wifi="11111111";
//================THỜI GIAN ĐO================
unsigned long thoi_gian_bat_dau=0,thoi_gian_tam=0;
const long thoi_gian_do=300000; 
//===============SETUP========================
const long id_chip=ESP.getChipId();
//===============KẾT NỐi VỚI PAYLOAD==========
String serverName = "http://192.168.1.3:5000/api/du-lieu-nhiet"; 

void setup(){
  Serial.begin(115200);
  dht.begin();
  Serial.print("ID Chip: ");
  Serial.println(id_chip);
  WiFi.begin(ten_wifi,pass_wifi); //kết nối wifi
  Serial.print("ĐANG KẾT NỐI WIFI");
  configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov"); // UTC+7
  long temp=0;
  delay(3000); 
  while (WiFi.status()!=WL_CONNECTED){
    delay(1000);
    if(millis()-temp>=2000){
    temp=millis();
    Serial.println("ERO: CHƯA KẾT NỐI ĐƯỢC WIFI");
    }
  }
  Serial.println("KẾT NỐI THÀNH CÔNG");

}

//hàm nhận tín hiệu đo
void KiemTraTinHieuDo(){
  if(millis()-thoi_gian_tam>=1000){
    thoi_gian_tam=millis();
    //đọc từ firebase nếu có tín hiệu thì đo
    String path = "/dht11/" + String(id_chip) + "/tinh_hieu"; // Đường dẫn tín hiệu
    int temp = 0;
    if(temp==1){
      thoi_gian_bat_dau=millis();
      float nhiet_do=dht.readTemperature(); 
      float do_am=dht.readHumidity();
      String du_lieu=String(id_chip)+","+String(nhiet_do)+","+String(do_am)+","+String(time(NULL));


      String path = "/dht11/" + String(id_chip) ; // Đường dẫn lưu trữ dữ liệu

    }
  }
}
void loop(){
  unsigned long thoi_gian_hien_tai = millis(); 

  if(thoi_gian_hien_tai-thoi_gian_bat_dau>=thoi_gian_do){
    float nhiet_do=dht.readTemperature(); 
    float do_am=dht.readHumidity();

    // 1. LẤY GIỜ CHUẨN ISO 8601 TỪ NTP
    time_t now = time(nullptr);
    struct tm* timeinfo = localtime(&now);
    char timeStringBuff[25];
    strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%dT%H:%M:%S", timeinfo);
    String thoi_gian_chuan = String(timeStringBuff);

    // 2. ĐÓNG GÓI JSON CHO KHỚP VỚI KHUÔN FLASK
    String payload = "{\"sensor_id\":\"" + String(id_chip) + "\",\"device_id\":\"ESP8266-" + String(id_chip) + "\",\"temp\":" + String(nhiet_do) + ",\"humidity\":" + String(do_am) + ",\"ts\":\"" + thoi_gian_chuan + "\"}";
    
    Serial.println("Chuẩn bị bắn hàng: " + payload);

    // 3. KHAI HỎA HTTP POST ĐỂ ĐẨY QUA LAPTOP
    WiFiClient client;
    HTTPClient http;

    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.print("-> GỬI API THÀNH CÔNG! Mã: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("-> LỖI GỬI API: ");
      Serial.println(http.errorToString(httpResponseCode).c_str());
    }
    http.end();
    
    thoi_gian_bat_dau=thoi_gian_hien_tai; 
  }
}