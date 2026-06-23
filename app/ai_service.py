from utils.ai_client import goi_ai


def generate_suggestions(context: dict) -> str | None:
    """Call AI to produce actionable suggestions based on sensor context.

    ``context`` keys: device_id, sensor_data, alerts, status,
    warning_threshold, danger_threshold.

    Returns a multi-line string, or ``None`` if the AI call fails.
    """
    sensor = context.get("sensor_data", {})
    nhiet_do = sensor.get("temp", "N/A")
    do_am = sensor.get("humidity", "N/A")
    status = context.get("status", "NORMAL")
    warn = context.get("warning_threshold", 35)
    danger = context.get("danger_threshold", 40)

    prompt = (
        f"Nhiệt độ hiện tại: {nhiet_do}°C\n"
        f"Độ ẩm: {do_am}%\n"
        f"Trạng thái: {status}\n"
        f"Ngưỡng cảnh báo: {warn}°C\n"
        f"Ngưỡng nguy hiểm: {danger}°C\n"
        f"\n"
        f"Hãy đưa ra 3-5 gợi ý ngắn gọn, hành động được "
        f"để khắc phục tình trạng {status.lower()} này. "
        f"Mỗi gợi ý trên một dòng."
    )
    return goi_ai(prompt)
