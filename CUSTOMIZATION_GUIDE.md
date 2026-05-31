"""
Advanced Customization Guide for Modern Dashboard

This guide shows how to customize colors, layouts, and add new features
to the dashboard_view_modern.py
"""

# ============================================================================

# 1. CUSTOMIZING COLORS AND THEME

# ============================================================================

"""
To change the color scheme, modify these constants at the top of the file:
"""

# Light Mode (Default)

COLOR_SCHEMES = {
'light': {
'BG_LIGHT': "#F3F4F6",
'SIDEBAR': "#FFFFFF",
'CARD_BG': "#FFFFFF",
'PRIMARY': "#3B82F6",
'PRIMARY_HOVER': "#2563EB",
'TEXT_PRIMARY': "#1F2937",
'TEXT_SECONDARY': "#6B7280",
'BORDER': "#E5E7EB",
'WARNING': "#F59E0B",
'DANGER': "#EF4444",
'SUCCESS': "#10B981",
}, # Dark Mode
'dark': {
'BG_LIGHT': "#1F2937",
'SIDEBAR': "#111827",
'CARD_BG': "#374151",
'PRIMARY': "#60A5FA",
'PRIMARY_HOVER': "#3B82F6",
'TEXT_PRIMARY': "#F3F4F6",
'TEXT_SECONDARY': "#D1D5DB",
'BORDER': "#4B5563",
'WARNING': "#FBBF24",
'DANGER': "#F87171",
'SUCCESS': "#34D399",
}, # Modern Gradient Theme
'gradient': {
'BG_LIGHT': "#F5F7FA",
'SIDEBAR': "#FFFFFF",
'CARD_BG': "#FFFFFF",
'PRIMARY': "#7C3AED", # Purple instead of blue
'PRIMARY_HOVER': "#6D28D9",
'TEXT_PRIMARY': "#1F2937",
'TEXT_SECONDARY': "#6B7280",
'BORDER': "#E5E7EB",
'WARNING': "#EC4899", # Pink
'DANGER': "#F97316", # Orange
'SUCCESS': "#06B6D4", # Cyan
}
}

# ============================================================================

# 2. CHANGE THEME DYNAMICALLY

# ============================================================================

def set_dashboard_theme(self, theme_name='light'):
"""Change the dashboard theme at runtime"""
theme = COLOR_SCHEMES.get(theme_name, COLOR_SCHEMES['light'])

    # Update all color globals
    global COLOR_BG_LIGHT, COLOR_SIDEBAR, COLOR_PRIMARY, COLOR_PRIMARY_HOVER
    global COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BORDER

    COLOR_BG_LIGHT = theme['BG_LIGHT']
    COLOR_SIDEBAR = theme['SIDEBAR']
    COLOR_PRIMARY = theme['PRIMARY']
    COLOR_PRIMARY_HOVER = theme['PRIMARY_HOVER']
    COLOR_TEXT_PRIMARY = theme['TEXT_PRIMARY']
    COLOR_TEXT_SECONDARY = theme['TEXT_SECONDARY']
    COLOR_BORDER = theme['BORDER']

    # Recreate the entire dashboard
    self.root.destroy()
    self.__init__(self.root)

# ============================================================================

# 3. ADD CUSTOM CHART TYPES

# ============================================================================

def update_chart_to_bar_chart(self):
"""Change line chart to bar chart"""
fig = Figure(figsize=(6, 3.5), dpi=100, facecolor=COLOR_BG_LIGHT)
ax = fig.add_subplot(111)

    hours = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
    temps = [22, 24, 26, 28, 30, 32, 31, 29, 27]

    # Create bar chart with gradient colors
    colors = [self.get_temp_color(temp) for temp in temps]
    ax.bar(hours, temps, color=colors, edgecolor='white', linewidth=1.5)

    ax.set_facecolor(COLOR_BG_LIGHT)
    ax.set_ylabel('Nhiệt độ (°C)', fontsize=10, color=COLOR_TEXT_SECONDARY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_BORDER)
    ax.spines['bottom'].set_color(COLOR_BORDER)
    ax.tick_params(colors=COLOR_TEXT_SECONDARY, labelsize=9)

    self.chart_canvas.draw()

def update_chart_to_heatmap(self):
"""Change to heatmap for temperature zones"""
import numpy as np

    fig = Figure(figsize=(6, 3.5), dpi=100, facecolor=COLOR_BG_LIGHT)
    ax = fig.add_subplot(111)

    # Create sample heatmap data (temperature zones over time)
    hours = 9
    zones = 5
    data = np.random.randint(20, 35, size=(zones, hours))

    im = ax.imshow(data, cmap='RdYlGn_r', aspect='auto', vmin=15, vmax=40)
    ax.set_xlabel('Giờ', fontsize=10, color=COLOR_TEXT_SECONDARY)
    ax.set_ylabel('Vùng cảm biến', fontsize=10, color=COLOR_TEXT_SECONDARY)
    ax.set_xticklabels(['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'])
    ax.set_yticklabels(['Vùng 1', 'Vùng 2', 'Vùng 3', 'Vùng 4', 'Vùng 5'])

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Nhiệt độ (°C)', fontsize=9, color=COLOR_TEXT_SECONDARY)

    self.chart_canvas.draw()

# ============================================================================

# 4. ADD NEW CARDS TO DASHBOARD

# ============================================================================

def add_humidity_card(self, parent):
"""Add a humidity statistics card"""
card = ctk.CTkFrame(
parent,
fg_color=COLOR_CARD_BG,
corner_radius=15,
border_width=1,
border_color=COLOR_BORDER
)
card.pack(fill="x", pady=10)

    inner = ctk.CTkFrame(card, fg_color=COLOR_CARD_BG)
    inner.pack(fill="both", expand=True, padx=20, pady=15)

    title = ctk.CTkLabel(
        inner,
        text="Độ ẩm hiện tại",
        font=("Arial", 12, "bold"),
        text_color=COLOR_TEXT_PRIMARY
    )
    title.pack(anchor="w")

    humidity_label = ctk.CTkLabel(
        inner,
        text=f"{self.humidity}%",
        font=("Arial", 36, "bold"),
        text_color=COLOR_PRIMARY
    )
    humidity_label.pack(pady=10)

    # Add progress bar for humidity
    progress = ctk.CTkProgressBar(
        inner,
        fg_color=COLOR_BORDER,
        progress_color="#3B82F6"
    )
    progress.pack(fill="x", pady=5)
    progress.set(self.humidity / 100.0)

def add_alert_summary_card(self, parent):
"""Add an alerts summary card"""
card = ctk.CTkFrame(
parent,
fg_color=COLOR_CARD_BG,
corner_radius=15,
border_width=1,
border_color=COLOR_BORDER
)
card.pack(fill="x", pady=10)

    inner = ctk.CTkFrame(card, fg_color=COLOR_CARD_BG)
    inner.pack(fill="both", expand=True, padx=20, pady=15)

    title = ctk.CTkLabel(
        inner,
        text="Cảnh báo hôm nay",
        font=("Arial", 12, "bold"),
        text_color=COLOR_TEXT_PRIMARY
    )
    title.pack(anchor="w")

    # Alert stats
    stats_frame = ctk.CTkFrame(inner, fg_color=COLOR_CARD_BG)
    stats_frame.pack(fill="x", pady=10)

    # Critical alerts
    critical_frame = ctk.CTkFrame(stats_frame, fg_color=COLOR_CARD_BG)
    critical_frame.pack(side="left", fill="x", expand=True, padx=5)

    ctk.CTkLabel(critical_frame, text="🔴 Nghiêm trọng", font=("Arial", 10)).pack()
    ctk.CTkLabel(critical_frame, text="5", font=("Arial", 18, "bold"), text_color=COLOR_DANGER).pack()

    # Warning alerts
    warning_frame = ctk.CTkFrame(stats_frame, fg_color=COLOR_CARD_BG)
    warning_frame.pack(side="left", fill="x", expand=True, padx=5)

    ctk.CTkLabel(warning_frame, text="🟠 Cảnh báo", font=("Arial", 10)).pack()
    ctk.CTkLabel(warning_frame, text="12", font=("Arial", 18, "bold"), text_color=COLOR_WARNING).pack()

    # Info alerts
    info_frame = ctk.CTkFrame(stats_frame, fg_color=COLOR_CARD_BG)
    info_frame.pack(side="left", fill="x", expand=True, padx=5)

    ctk.CTkLabel(info_frame, text="🔵 Thông tin", font=("Arial", 10)).pack()
    ctk.CTkLabel(info_frame, text="23", font=("Arial", 18, "bold"), text_color=COLOR_PRIMARY).pack()

# ============================================================================

# 5. ADD INTERACTIVE FEATURES

# ============================================================================

def add_time_range_filter(self, parent):
"""Add time range selector for chart"""
filter_frame = ctk.CTkFrame(parent, fg_color=COLOR_BG_LIGHT)
filter_frame.pack(fill="x", pady=(0, 10))

    label = ctk.CTkLabel(
        filter_frame,
        text="Thời gian:",
        font=("Arial", 10),
        text_color=COLOR_TEXT_SECONDARY
    )
    label.pack(side="left", padx=(0, 10))

    # Time range buttons
    ranges = ["1 giờ", "6 giờ", "24 giờ", "1 tuần", "1 tháng"]

    for range_name in ranges:
        btn = ctk.CTkButton(
            filter_frame,
            text=range_name,
            font=("Arial", 9),
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_PRIMARY,
            height=25,
            command=lambda r=range_name: self.update_chart_for_range(r)
        )
        btn.pack(side="left", padx=5)

def update_chart_for_range(self, time_range):
"""Update chart based on selected time range"""
print(f"Updating chart for {time_range}") # Implement logic to fetch and update chart data for selected range
pass

def add_export_button(self, parent):
"""Add button to export dashboard data"""
export_btn = ctk.CTkButton(
parent,
text="📥 Export Data",
font=("Arial", 10),
fg_color=COLOR_PRIMARY,
text_color="white",
hover_color=COLOR_PRIMARY_HOVER,
command=self.export_dashboard_data
)
export_btn.pack(side="right", padx=5)

def export_dashboard_data(self):
"""Export current dashboard data to CSV"""
import csv
from datetime import datetime

    filename = f"temperature_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'Temperature (°C)', 'Humidity (%)', 'Status'])
        # Add your data rows here

    print(f"Data exported to {filename}")

# ============================================================================

# 6. ADD STATISTICS PANEL

# ============================================================================

def add_statistics_panel(self, parent):
"""Add detailed statistics panel"""
stats_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD_BG)
stats_frame.pack(fill="both", expand=True, pady=10)

    title = ctk.CTkLabel(
        stats_frame,
        text="Thống kê",
        font=("Arial", 12, "bold"),
        text_color=COLOR_TEXT_PRIMARY
    )
    title.pack(anchor="w", padx=20, pady=(15, 10))

    # Stats grid
    stats_data = [
        ("Trung bình", "28.5°C", COLOR_PRIMARY),
        ("Tối đa", "35.2°C", COLOR_DANGER),
        ("Tối thiểu", "21.8°C", COLOR_SUCCESS),
        ("Độ lệch chuẩn", "4.2°C", COLOR_TEXT_SECONDARY),
    ]

    for label, value, color in stats_data:
        row = ctk.CTkFrame(stats_frame, fg_color=COLOR_CARD_BG)
        row.pack(fill="x", padx=20, pady=5)

        label_widget = ctk.CTkLabel(
            row,
            text=label,
            font=("Arial", 10),
            text_color=COLOR_TEXT_SECONDARY
        )
        label_widget.pack(side="left")

        value_widget = ctk.CTkLabel(
            row,
            text=value,
            font=("Arial", 10, "bold"),
            text_color=color
        )
        value_widget.pack(side="right")

# ============================================================================

# 7. ADD DARK MODE TOGGLE

# ============================================================================

def add_dark_mode_toggle(self, parent):
"""Add theme toggle button"""
toggle_frame = ctk.CTkFrame(parent, fg_color="transparent")
toggle_frame.pack(side="right", padx=10, pady=10)

    def toggle_theme():
        current_mode = ctk.get_appearance_mode()
        new_mode = "dark" if current_mode == "light" else "light"
        ctk.set_appearance_mode(new_mode)
        toggle_btn.configure(text="☀️ Light" if new_mode == "dark" else "🌙 Dark")

    toggle_btn = ctk.CTkButton(
        toggle_frame,
        text="🌙 Dark",
        font=("Arial", 9),
        fg_color=COLOR_PRIMARY,
        text_color="white",
        hover_color=COLOR_PRIMARY_HOVER,
        height=30,
        command=toggle_theme
    )
    toggle_btn.pack()

# ============================================================================

# 8. RESPONSIVE LAYOUT ADJUSTMENTS

# ============================================================================

"""
For different screen sizes, adjust the window geometry:
"""

SCREEN_LAYOUTS = {
'mobile': {'width': 400, 'height': 800, 'sidebar_width': 120},
'tablet': {'width': 800, 'height': 600, 'sidebar_width': 150},
'desktop': {'width': 1400, 'height': 800, 'sidebar_width': 220},
'ultrawide': {'width': 2000, 'height': 900, 'sidebar_width': 280},
}

def set_responsive_layout(self, device_type='desktop'):
"""Set layout based on device type"""
layout = SCREEN_LAYOUTS.get(device_type, SCREEN_LAYOUTS['desktop'])
self.root.geometry(f"{layout['width']}x{layout['height']}") # Adjust font sizes and padding accordingly

# ============================================================================

# 9. ADD CUSTOM NOTIFICATIONS

# ============================================================================

def show_notification(self, title, message, duration=3000, notif_type='info'):
"""Show a toast-like notification"""
import tkinter as tk

    # Color based on type
    colors = {
        'info': COLOR_PRIMARY,
        'warning': COLOR_WARNING,
        'danger': COLOR_DANGER,
        'success': COLOR_SUCCESS
    }

    notif_frame = ctk.CTkFrame(
        self.root,
        fg_color=colors.get(notif_type, COLOR_PRIMARY),
        corner_radius=10
    )
    notif_frame.pack(side="top", fill="x", padx=10, pady=10)

    notif_label = ctk.CTkLabel(
        notif_frame,
        text=f"{'ℹ️' if notif_type == 'info' else '⚠️' if notif_type == 'warning' else '❌' if notif_type == 'danger' else '✓'} {title}: {message}",
        font=("Arial", 10),
        text_color="white"
    )
    notif_label.pack(padx=15, pady=10)

    # Auto-dismiss after duration
    self.root.after(duration, lambda: notif_frame.destroy())

# ============================================================================

# 10. EXAMPLE USAGE IN MAIN

# ============================================================================

def main_with_customizations():
"""Example of using customizations"""
import customtkinter as ctk

    root = ctk.CTk()
    app = TemperatureDashboard(root)

    # Apply customizations
    app.set_dashboard_theme('dark')
    app.set_responsive_layout('desktop')

    # Show notifications
    app.show_notification(
        "Khởi động",
        "Hệ thống quản lý nhiệt độ sẵn sàng",
        notif_type='success'
    )

    root.mainloop()

if **name** == "**main**":
main_with_customizations()
