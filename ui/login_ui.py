import tkinter as tk
from logic.db_queries import login_user
from ui.user_dashboard import open_user_dashboard
from ui.admin_dashboard import open_admin_dashboard
import hashlib

class LoginWindow(tk.Frame):
    def __init__(self, master, controller, on_login_success=None):
        super().__init__(master)
        self.controller = controller
        self.on_login_success = on_login_success
        self.bind_all("<Return>", lambda event: self.login())

        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()

        label_font = ("Segoe UI", 12)
        entry_width = 30
        button_style = {
            "font": ("Segoe UI", 11),
            "width": 25,
            "height": 2,
            "relief": "raised",
            "bg": "#f0f0f0",
            "activebackground": "#d0e0ff",
            "cursor": "hand2",
            "bd": 1,
        }

        tk.Label(self, text="🔐 Login to PanView Cinemas!", font=("Segoe UI", 16), fg="blue").pack(pady=10)

        tk.Label(self, text="📧 Email:", font=label_font).pack(pady=5)
        email_entry = tk.Entry(self, textvariable=self.email_var, width=entry_width, font=label_font)
        email_entry.pack()

        tk.Label(self, text="🔒 Password:", font=label_font).pack(pady=5)
        password_entry = tk.Entry(self, textvariable=self.password_var, show="*", width=entry_width, font=label_font)
        password_entry.pack()

        login_btn = tk.Button(self, text="Login", command=self.login, **button_style)
        login_btn.pack(pady=10)
        self.add_hover_effect(login_btn)

        self.message_label = tk.Label(self, text="", fg="red", font=("Segoe UI", 10))
        self.message_label.pack()
        
        back_btn = tk.Button(self, text="🔙 Back", command=self.go_back, **button_style)
        back_btn.pack(pady=10)
        self.add_hover_effect(back_btn)

    def add_hover_effect(self, button):
        def on_enter(e):
            button['background'] = "#d0e0ff"
        def on_leave(e):
            button['background'] = "#f0f0f0"
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def open_dashboard(self, user_id, name, is_admin):
        self.controller.destroy()
        if is_admin:
            open_admin_dashboard(user_id, name)
        else:
            open_user_dashboard(user_id, name)

    def login(self):
        email = self.email_var.get()
        password1 = self.password_var.get()

        pwd_hash = hashlib.sha256(password1.encode()).hexdigest()
        pwd_no_hash = password1

        user = login_user(email)
        if user is None:
            self.message_label.config(text="User not found.")
            return

        user_id, name, email, password, is_admin = user
        if password == pwd_hash or password == pwd_no_hash:
            self.message_label.config(text="Login successful!", fg="green")
            self.after(1000, lambda: self.open_dashboard(user_id, name, is_admin))
            if self.on_login_success:
                self.on_login_success(user_id, name, is_admin)
        else:
            self.message_label.config(text="Incorrect password.", fg="red")

    def go_back(self):
        self.controller.show_home()
