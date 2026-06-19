from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, AliasChoices


class DuLieuNhietVao(BaseModel):
    """Dữ liệu đầu vào từ thiết bị."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    thiet_bi_id: str = Field(alias="device_id")  # Mã thiết bị
    nhiet_do: float = Field(alias="temp")  # Nhiệt độ đo được
    do_am: Optional[float] = Field(default=None, alias="humidity")  # Độ ẩm (nếu có)
    thoi_gian_thiet_bi: Optional[datetime] = Field(default=None, alias="ts")  # Thời gian thiết bị


class DuLieuNhietRa(BaseModel):
    """Dữ liệu trả ra sau xử lý."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    thiet_bi_id: str = Field(alias="device_id", validation_alias=AliasChoices("device_id", "sensor_id"))
    nhiet_do: float = Field(alias="temp")
    do_am: Optional[float] = Field(default=None, alias="humidity")
    thoi_gian_thiet_bi: Optional[datetime] = Field(default=None, alias="timestamp", validation_alias=AliasChoices("ts", "timestamp"))
    thoi_gian_server: Optional[datetime] = Field(default=None, alias="server_ts")


class ApiResponse(BaseModel):
    """Phản hồi API thành công."""

    model_config = ConfigDict(populate_by_name=True)

    trang_thai: str = Field(alias="status")
    thong_diep: str = Field(alias="message")
    du_lieu: Optional[dict] = Field(default=None, alias="data")


class ErrorResponse(BaseModel):
    """Phản hồi API khi có lỗi."""

    model_config = ConfigDict(populate_by_name=True)

    trang_thai: str = Field(alias="status")
    thong_diep: str = Field(alias="message")
    loi: list[dict] = Field(default_factory=list, alias="errors")


class AlertOut(BaseModel):
    """Thông tin cảnh báo (dùng cho UI)."""

    model_config = ConfigDict(populate_by_name=True)

    thiet_bi_id: str = Field(alias="device_id")
    nhiet_do_tb: float = Field(alias="avg_temp")
    nhiet_do_hien_tai: float = Field(alias="temp")
    phan_tram_tang: float = Field(alias="percent_increase")
    nguong_tang: float = Field(alias="threshold")
    muc_do: str = Field(alias="level")
    thong_diep: str = Field(default="Cảnh báo nhiệt độ", alias="warning")
    thoi_gian_tao: Optional[datetime] = Field(default=None, alias="timestamp")


class AiSuggestionRequest(BaseModel):
    """Yêu cầu gợi ý AI."""

    model_config = ConfigDict(populate_by_name=True)

    nhiet_do_hien_tai: float = Field(alias="current_temp")
    nhiet_do_trung_binh: float = Field(alias="avg_temp")
    nguong: float = Field(alias="threshold")


class DeviceLink(BaseModel):
    device_id: str
    name: str

class DeviceSettings(BaseModel):
    temperatureThreshold: Optional[float] = None
    humidityThreshold: Optional[float] = None
    samplingInterval: Optional[int] = None
    notificationEnabled: Optional[bool] = None