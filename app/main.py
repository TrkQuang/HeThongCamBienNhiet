import tkinter as tk
from dashboard_view import Dashboard

root = tk.Tk()
root.title("Dashboard")
root.geometry("900x500")

app = Dashboard(root)

app.update_temp(28)

root.mainloop()