import tkinter as tk
from tkinter import messagebox
from logic.db_queries import register, login_user
import hashlib

class RegisterWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.bind_all("<Return>", lambda event: self.register_user())

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        label_font = ("Segoe UI", 12)
        entry_font = ("Segoe UI", 12)
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

        tk.Label(self, text="📝 Register New User", font=("Segoe UI", 16), fg="blue").pack(pady=10)

        self._add_labeled_entry("👤 Name:", self.name_var, label_font, entry_font, entry_width)

        self._add_labeled_entry("📧 Email:", self.email_var, label_font, entry_font, entry_width)

        self._add_labeled_entry("🔒 Password:", self.password_var, label_font, entry_font, entry_width, show="*")

        self._add_labeled_entry("🔒 Confirm Password:", self.confirm_password_var, label_font, entry_font, entry_width, show="*")

        register_btn = tk.Button(self, text="Register", command=self.register_user, **button_style)
        register_btn.pack(pady=10)
        self.add_hover_effect(register_btn)

        self.message_label = tk.Label(self, text="", fg="red", font=("Segoe UI", 10))
        self.message_label.pack()

        back_btn = tk.Button(self, text="🔙 Back", command=self.go_back, **button_style)
        back_btn.pack(pady=10)
        self.add_hover_effect(back_btn)

    def _add_labeled_entry(self, label_text, variable, label_font, entry_font, width, show=None):
        frame = tk.Frame(self)
        frame.pack(fill="x", padx=20, pady=5)

        tk.Label(frame, text=label_text, font=label_font, anchor="w").pack(anchor="w")
        entry = tk.Entry(frame, textvariable=variable, width=width, font=entry_font, show=show)
        entry.pack(fill="x")

    def add_hover_effect(self, button):
        def on_enter(e): button.config(bg="#d0e0ff")
        def on_leave(e): button.config(bg="#f0f0f0")
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def register_user(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()

        if not name or not email or not password or not confirm_password:
            self.message_label.config(text="All fields are required!")
            return

        if password != confirm_password:
            self.message_label.config(text="Passwords do not match!")
            return

        if login_user(email):
            self.message_label.config(text="User already exists with this email!")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            register(name, email, password_hash)
            self.message_label.config(text="Registration successful! Redirecting to login...", fg="green")
            self.clear_fields()
            self.after(3000, self.controller.show_login)
        except Exception as e:
            self.message_label.config(text=f"Error: {str(e)}", fg="red")

    def clear_fields(self):
        self.name_var.set("")
        self.email_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")

    def go_back(self):
        self.controller.show_home()
