# database/ - Lưu trữ dữ liệu

## Mục đích

Quản lý kết nối DB và định nghĩa models cho dữ liệu nhiệt, cảnh báo.

## Chứa gì

- Kết nối DB (SQLite mặc định)
- Models dữ liệu
- Lớp repository thao tác đọc/ghi

## Danh sách file

- **init**.py (package): Khai báo package, giúp import các module DB.
- db.py (infrastructure): Tạo engine/session, cấu hình kết nối DB.
- models.py (model/ORM): Định nghĩa bảng dữ liệu (du_lieu_nhiet, canh_bao).
- repository.py (repository/service): CRUD và truy vấn theo sensor_id, thời gian.

## Ví dụ sử dụng

Khởi tạo kết nối trong `db.py`, sau đó gọi repository để lưu dữ liệu.

## ERD
<!-- THIET_BI {
        int id_thiet_bi PK "Khóa chính"
        string ma_cam_bien UK "Địa chỉ MAC / Mã cảm biến"
        string vi_tri "Vị trí đặt. VD: Phòng Server"
        float nguong_nhiet_do "Ngưỡng cảnh báo"
        datetime ngay_tao
    }
    
    NHAT_KY_NHIET_DO {
        int id_nhat_ky PK "Khóa chính"
        int id_thiet_bi FK "Khóa ngoại trỏ về THIET_BI"
        float nhiet_do "Giá trị nhiệt độ"
        datetime thoi_gian_do "Thời gian đo (Index)"
    }
    
    CANH_BAO {
        int id_canh_bao PK "Khóa chính"
        int id_thiet_bi FK "Khóa ngoại trỏ về THIET_BI"
        string loai_canh_bao "VD: VUOT_NGUONG"
        string noi_dung "Chi tiết cảnh báo"
        datetime thoi_gian_canh_bao
    }

    %% Định nghĩa mối quan hệ: 1 Thiết bị có nhiều Nhật ký và Cảnh báo
    THIET_BI ||--o{ NHAT_KY_NHIET_DO : "có"
    THIET_BI ||--o{ CANH_BAO : "tạo ra" -->