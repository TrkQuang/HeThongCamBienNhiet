import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from .alert_panel import AlertView
from .api_client import ApiClient
from .dashboard_view_modern import DashboardView
from .data_service import DataService
from .settings_store import AppSettings, load_settings, save_settings
from .settings_view import SettingsView
from .widgets import *
from firebase.device_repo import delete_device


class AddDeviceDialog(ctk.CTkToplevel):
    def __init__(self, master, api_client: ApiClient, on_success):
        super().__init__(master)
        self.title("Thêm Thiết Bị Mới")
        self.geometry("400x300")
        self.attributes("-topmost", True)
        self._api, self._on_success = api_client, on_success
        self._adding = False
        k = ctk.CTkFrame(self, fg_color=MAU_THE_BG)
        k.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(k, text="Thêm Thiết Bị", font=("Arial", 16, "bold"), text_color=MAU_CHU_CHINH).pack(pady=(10, 20))
        self.e_id = ctk.CTkEntry(k, placeholder_text="Device ID", width=300)
        self.e_id.pack(pady=10)
        self.e_name = ctk.CTkEntry(k, placeholder_text="Tên hiển thị", width=300)
        self.e_name.pack(pady=10)
        self.l_err = ctk.CTkLabel(k, text="", text_color=MAU_NGUY_HIEM)
        self.l_err.pack(pady=5)
        self.btn_xn = ctk.CTkButton(k, text="Xác nhận", fg_color=MAU_CHINH, hover_color=MAU_CHINH_HOVER, command=self.kiem_tra)
        self.btn_xn.pack()

    def kiem_tra(self):
        if self._adding:
            return
        did = self.e_id.get().strip()
        name = self.e_name.get().strip() or "Thiết bị mới"
        if not did:
            self.l_err.configure(text="Nhập Device ID")
            return
        self._adding = True
        self.btn_xn.configure(state="disabled", text="⏳ Đang thêm...")
        self.l_err.configure(text="", text_color=MAU_CHU_PHU)
        def xl():
            loi = None
            try:
                self._api._post("/api/devices/link", {"device_id": did, "name": name})
            except Exception as e:
                loi = f"Lỗi kết nối: {e}" if "connection" in str(e).lower() else f"Lỗi: {e}"
            self.after(0, lambda: self.kq(loi, did, name))
        threading.Thread(target=xl, daemon=True).start()

    def kq(self, loi, did, name):
        if loi:
            self.l_err.configure(text=loi, text_color=MAU_NGUY_HIEM)
            self.btn_xn.configure(state="normal", text="Xác nhận")
            self._adding = False
        else:
            self._on_success(did, name)
            self.destroy()


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        ap_dung_giao_dien()
        self._set = load_settings()
        self._api = ApiClient(self._set.api_base_url)
        self._ds = DataService(self._api, self._set)
        self.title("Giám Sát Nhiệt Độ")
        self.geometry("1400x800")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._nut_tab, self._tab_ht = {}, "Dashboard"
        self._prev_device_ids: list = []

        self.kb = ctk.CTkFrame(self, fg_color=MAU_THANH_BEN, corner_radius=0, width=250)
        self.kb.grid(row=0, column=0, sticky="nsew")
        self.kb.grid_propagate(False)
        self.knd = ctk.CTkFrame(self, fg_color=MAU_NEN_SANG, corner_radius=0)
        self.knd.grid(row=0, column=1, sticky="nsew")

        self.tao_thanh_ben()
        self.tao_noi_dung()

        # Subscribe for device-list sync only — NOT for every sensor update
        self._ds.subscribe(lambda: self.after(0, self._on_ds_notify))

        if self._set.device_id: self.chon(self._set.device_id)
        elif self._set.devices: self.chon(self._set.devices[0]["id"])
        else: self.hien_trong()

    def _on_ds_notify(self):
        """Called from DataService on ALL data changes — we only re-render sidebar
        when the device list actually changed (DataService's _update_device_list
        skips the notify call when no change occurred)."""
        # Only sync device list (this is lightweight since DataService
        # skips _notify when _last_device_ids hasn't changed)
        self.render_ds()

    def tao_thanh_ben(self):
        for w in self.kb.winfo_children(): w.destroy()
        td = ctk.CTkFrame(self.kb, fg_color="transparent")
        td.pack(fill="x", pady=20, padx=20)
        ctk.CTkLabel(td, text="📡 THIẾT BỊ", font=("Arial", 16, "bold"), text_color=MAU_CHINH).pack()
        ctk.CTkFrame(self.kb, height=1, fg_color=MAU_DUONG_BIEN).pack(fill="x", padx=20, pady=(0, 10))
        self.ds_tb = ctk.CTkScrollableFrame(self.kb, fg_color="transparent")
        self.ds_tb.pack(fill="both", expand=True, padx=10)
        ctk.CTkButton(self.kb, text="+ Thêm thiết bị", fg_color="transparent", border_width=2,
                       text_color=MAU_CHINH, command=lambda: AddDeviceDialog(self, self._api, self.them)).pack(fill="x", padx=20, pady=20)
        self.render_ds()

    def render_ds(self):
        """Incremental sidebar: only rebuild when device list actually changed.

        Compares device-ID signature (sorted list) to avoid full rebuild
        on every sensor-data notification.
        """
        devices = self._set.devices or []

        # Build current ID signature
        current_ids = [d["id"] for d in devices]
        if (self._prev_device_ids == current_ids and len(self._nut_tab) == len(devices)):
            self.cap_nhat_mau()
            return
        self._prev_device_ids = current_ids

        for w in self.ds_tb.winfo_children(): w.destroy()
        self._nut_tab.clear()

        if not devices:
            ctk.CTkLabel(self.ds_tb, text="Chưa có thiết bị", text_color=MAU_CHU_PHU).pack(pady=20)
            return

        for tb in devices:
            did, name = tb["id"], tb.get("name", tb["id"])
            khung = ctk.CTkFrame(self.ds_tb, fg_color="transparent")
            khung.pack(fill="x", pady=5)
            n = ctk.CTkButton(khung, text=f"🏠 {name}\n{did}", fg_color="transparent",
                              text_color=MAU_CHU_CHINH, height=50, command=lambda d=did: self.chon(d))
            n.pack(side="left", fill="x", expand=True)
            del_btn = ctk.CTkButton(khung, text="🗑", width=40, height=50, fg_color="transparent",
                                    hover_color="#ff4444", command=lambda d=did: self.xoa_device(d))
            del_btn.pack(side="right", padx=(5, 0))
            self._nut_tab[did] = khung
        self.cap_nhat_mau()

    def cap_nhat_mau(self):
        for did, khung in self._nut_tab.items():
            for child in khung.winfo_children():
                if isinstance(child, ctk.CTkButton) and child.cget("text").startswith("🏠"):
                    child.configure(
                        fg_color=MAU_CHINH if did == self._set.device_id else "transparent",
                        text_color="white" if did == self._set.device_id else MAU_CHU_CHINH
                    )

    def them(self, did, name):
        self._refresh_device_list()
        self._set.device_id = did
        save_settings(self._set)
        self.render_ds()
        self.chon(did)

    def _refresh_device_list(self):
        try:
            devices_raw = self._api.get_devices()
            self._set.devices = [
                {"id": d.get("device_id", d.get("id")), "name": d.get("name", d.get("device_id", ""))}
                for d in devices_raw
            ]
            save_settings(self._set)
        except Exception as e:
            print(f"[REFRESH] error: {e}")

    def xoa_device(self, did):
        kq = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xoá device này không?")
        if not kq:
            return
        try:
            delete_device("default_user", did)
        except Exception as loi:
            print(f"[DEL] delete_device error: {loi}")
        self._refresh_device_list()
        if self._set.device_id == did:
            self._set.device_id = self._set.devices[0]["id"] if self._set.devices else ""
            save_settings(self._set)
            self.render_ds()
            if self._set.device_id:
                self.chon(self._set.device_id)
            else:
                self.hien_trong()
        else:
            save_settings(self._set)
            self.render_ds()

    def tao_noi_dung(self):
        self.knd.grid_rowconfigure(1, weight=1)
        self.knd.grid_columnconfigure(0, weight=1)
        tb = ctk.CTkFrame(self.knd, fg_color=MAU_NEN_SANG, corner_radius=0, height=50)
        tb.grid(row=0, column=0, sticky="ew")
        self.n_db = ctk.CTkButton(tb, text="Tổng quan", command=lambda: self.tab("Dashboard"))
        self.n_db.pack(side="left", padx=(20, 10), pady=10)
        self.n_al = ctk.CTkButton(tb, text="Cảnh báo", command=lambda: self.tab("Alerts"))
        self.n_al.pack(side="left", padx=10, pady=10)
        self.n_st = ctk.CTkButton(tb, text="Cài đặt", command=lambda: self.tab("Settings"))
        self.n_st.pack(side="left", padx=10, pady=10)

        self.kt = ctk.CTkFrame(self.knd, fg_color=MAU_NEN_SANG, corner_radius=0)
        self.kt.grid(row=1, column=0, sticky="nsew")
        self.kt.grid_rowconfigure(0, weight=1)
        self.kt.grid_columnconfigure(0, weight=1)

        self._views = {
            "Dashboard": DashboardView(self.kt, self._ds),
            "Alerts": AlertView(self.kt, self._ds),
            "Settings": SettingsView(self.kt, self._ds, self.luu),
        }
        for v in self._views.values(): v.grid(row=0, column=0, sticky="nsew")

    def tab(self, name):
        self._tab_ht = name
        try:
            if hasattr(self, '_nhan_trong') and self._nhan_trong:
                self._nhan_trong.destroy(); self._nhan_trong = None
        except: pass
        for v in self._views.values():
            v.grid(row=0, column=0, sticky="nsew")
        for n, v in self._views.items():
            if n == name: v.tkraise()
        for n, b in [("Dashboard", self.n_db), ("Alerts", self.n_al), ("Settings", self.n_st)]:
            b.configure(
                fg_color=MAU_CHINH if n == name else "transparent",
                text_color="white" if n == name else MAU_CHU_CHINH,
                border_width=0 if n == name else 1,
                border_color=MAU_DUONG_BIEN
            )

    def chon(self, did):
        self._set.device_id = did
        save_settings(self._set)
        self.cap_nhat_mau()
        self._ds.update_settings(self._set)
        self.tab(self._tab_ht)

    def hien_trong(self):
        for v in self._views.values(): v.grid_forget()
        self._nhan_trong = ctk.CTkLabel(self.kt, text="Chọn thiết bị", text_color=MAU_CHU_PHU)
        self._nhan_trong.place(relx=0.5, rely=0.5, anchor="center")

    def luu(self, ch: AppSettings):
        self._set = ch
        save_settings(ch)
        def db():
            if ch.device_id:
                try:
                    payload = {
                        "temperatureThreshold": ch.warning_threshold,
                        "dangerThreshold": ch.danger_threshold,
                        "humidityThreshold": ch.humidity_threshold,
                        "samplingInterval": max(int(ch.refresh_ms / 60000), 1),
                        "notificationEnabled": ch.sound_alert,
                    }
                    print(f"[SETTINGS] SAVE payload to API: {payload}")
                    resp = self._api.update_settings(ch.device_id, payload)
                    print(f"[SETTINGS] SAVE response: {resp}")
                except Exception as e:
                    print(f"[SETTINGS] SAVE error: {e}")
        threading.Thread(target=db, daemon=True).start()
        self._ds.update_settings(ch)


__all__ = ["MainWindow"]
