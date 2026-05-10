import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.create_ui()
    
    def create_ui(self):
        #sidebar
        sidebar = tk.Frame(self.root, width=200, bg="white")
        sidebar.pack(side="left", fill="y")
        
        tk.Label(sidebar, text="HỆ THỐNG QUẢN LÝ NHIỆT ĐỘ", font=("Arial", 12, "bold"), bg="white").pack(pady=20)
        
        tk.Button(sidebar, text="DASHBOARD").pack(fill="x", pady=5)
        tk.Button(sidebar, text="ALERTS").pack(fill="x", pady=5)
        tk.Button(sidebar, text="SETTING").pack(fill="x", pady=5)
        
        #bên phải
        main = tk.Frame(self.root, bg='#f2f2f2')
        main.pack(side="right", expand=True, fill="both")

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        left = tk.Frame(main, bg='#f2f2f2')
        left.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        right = tk.Frame(main, bg='#f2f2f2')
        right.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        tk.Label(left, text="Nhiệt độ hiện tại", font=("Arial", 16), bg='#f2f2f2').pack(anchor='n')
        self.temp_label = tk.Label(left, text="36°C", font=("Arial", 50, "bold"), bg='#f2f2f2')
        self.temp_label.pack(pady=20, anchor='n')
        
        tk.Label(left, text="Nóng", font=("Arial", 14), bg='#f2f2f2').pack()
        
        #dữ liệu mẫu
        labels = ['Sáng', 'Trưa', 'Chiều', 'Tối']
        sizes = [30, 36, 32, 28]
        
        #thong ke
        tk.Label(right, text="Thống kê nhiệt độ trong ngày", font=("Arial", 14, "bold"), bg='#f2f2f2').pack(pady=(0, 5), anchor='n')
        
        #tạo figure
        fig = Figure(figsize=(4, 4), dpi=100)
        fig.patch.set_facecolor('#f2f2f2')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#f2f2f2')
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
      
        
        #nhúng vào Tkinter
        canvas = FigureCanvasTkAgg(fig, master=right)
        fig.tight_layout()
        canvas.draw()
        canvas.get_tk_widget().pack(anchor='n')
        
    def update_temp(self, value):
        self.temp_label.config(text=f"{value}°C")