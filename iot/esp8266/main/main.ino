#include <ESP8266WiFi.h>
#include <time.h>
#include <FirebaseESP8266.h>
#include "DHT.h"
#include <math.h>
//================SETUP DATABASE==============
#define firebase_host "hethongcambiennhiet-default-rtdb.asia-southeast1.firebasedatabase.app"
#define firebase_auth "FxnWmxRtKDz7XxEIFz3MdozuXusXm0WIywInlKjT"
FirebaseData firebaseData;
FirebaseConfig config;
FirebaseAuth auth;

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

    //cấu hình firebase
    config.host = firebase_host;
    config.signer.tokens.legacy_token = firebase_auth;
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
}

//hàm nhận tín hiệu đo
void KiemTraTinHieuDo(){
  if(millis()-thoi_gian_tam>=1000){
    thoi_gian_tam=millis();
    //đọc từ firebase nếu có tín hiệu thì đo
    String path = "/dht11/" + String(id_chip) + "/tinh_hieu"; // Đường dẫn tín hiệu
    int temp = 0;
    if(Firebase.getInt(firebaseData,path)){
      temp = firebaseData.intData();
    }
    if(temp==1){
      thoi_gian_bat_dau=millis();
      float nhiet_do=dht.readTemperature(); 
      float do_am=dht.readHumidity();
      String du_lieu=String(id_chip)+","+String(nhiet_do)+","+String(do_am)+","+String(time(NULL));
      FirebaseJson jsonData;
      jsonData.set("du_lieu", du_lieu);
      //gửi dữ liệu lên firebase
      String path = "/dht11/" + String(id_chip) ; // Đường dẫn lưu trữ dữ liệu
        if (Firebase.pushJSON(firebaseData, path, jsonData)) {
          Serial.println("-> GỬI FIREBASE THÀNH CÔNG!");
          Serial.println("--------------------");
          Firebase.setInt(firebaseData, "/dht11/" + String(id_chip) + "/tinh_hieu", 0); // Reset tín hiệu sau khi gửi
        } else {
          Serial.println("-> LỖI GỬI: " + firebaseData.errorReason());
          Serial.println("--------------------");
      }
    }
  }
}

void loop(){
  unsigned long thoi_gian_hien_tai=millis();//lấy thời gian hiện tại

  KiemTraTinHieuDo();
  //chuỗi database để lưu trữ dữ liệu
  
  if(thoi_gian_hien_tai-thoi_gian_bat_dau>=thoi_gian_do){
    float nhiet_do=dht.readTemperature(); 
    float do_am=dht.readHumidity();
    String du_lieu=String(id_chip)+","+String(nhiet_do)+","+String(do_am)+","+String(time(NULL));//thời gian xuất ra chỉ ở dạng timestamp
    Serial.println(du_lieu);
    
    thoi_gian_bat_dau=thoi_gian_hien_tai;
    FirebaseJson jsonData;
    jsonData.set("du_lieu", du_lieu);
    //gửi dữ liệu lên firebase
    String path = "/dht11/" + String(id_chip) ; // Đường dẫn lưu trữ dữ liệu
      if (Firebase.pushJSON(firebaseData, path, jsonData)) {
        Serial.println("-> GỬI FIREBASE THÀNH CÔNG!");
        Serial.println("--------------------");
      } else {
        Serial.println("-> LỖI GỬI: " + firebaseData.errorReason());
        Serial.println("--------------------");
      }
  }
}