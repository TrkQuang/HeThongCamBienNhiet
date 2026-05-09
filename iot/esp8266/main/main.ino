#include <ESP8266WiFi.h>
#include <time.h>
//================THÔNG TIN WIFI===============
const char* ten_wifi="Nguyễn Đình Chương";
const char* pass_wifi="11111111";
//================THỜI GIAN ĐO================
unsigned long thoi_gian_bat_dau=0;
const long thoi_gian_do=5000; 
//===============SETUP========================
const long id_chip=ESP.getChipId();

void setup(){
  Serial.begin(115200);
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
void loop(){
  unsigned long thoi_gian_hien_tai=millis();//lấy thời gian hiện tại

  float nhiet_do=random(280, 350)/10.0; //giả sử nhiệt độ là ramdom 
  float do_am=random(400, 800)/10.0; //giả sử độ ẩm là random

//chuỗi database để lưu trữ dữ liệu
  String du_lieu=String(id_chip)+","+String(nhiet_do)+","+String(do_am)+","+time(NULL);//thời gian xuất ra chỉ ở dạng timestamp

  if(thoi_gian_hien_tai-thoi_gian_bat_dau>=thoi_gian_do){
    Serial.println("ĐANG ĐO NHIỆT ĐỘ");
    Serial.println(du_lieu);
    
    thoi_gian_bat_dau=thoi_gian_hien_tai;
  }
}