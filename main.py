import tkinter as tk
from ui.login_ui import LoginWindow
from ui.register_ui import RegisterWindow


class MainApp(tk.Tk):   
    def __init__(self):
        super().__init__()
        self.title("Panaview Movie Booking")
        self.geometry("700x500")

        self.container = tk.Frame(self, bg="lightblue")
        self.container.pack(fill="both", expand=True)

        self.home_frame = None
        self.login_frame = None
        self.register_frame = None

        self.show_home()

    def show_home(self):
        self.clear_container()
        self.home_frame = tk.Frame(self.container, bg="lightblue")

        hme_msg = tk.Label(self.home_frame, text="🎬 Welcome to PanaView Cinemas!",
                           font=("Segoe UI", 18, "bold"), fg="blue", bg="lightblue")
        hme_msg.pack(pady=40)

        btn_register = tk.Button(self.home_frame, text="📝 Register User",
                                 width=25, height=2, font=("Segoe UI", 11),
                                 bg="#f0f0f0", activebackground="#d0e0ff",
                                 cursor="hand2", bd=1, relief="raised",
                                 command=self.show_register)
        btn_register.pack(pady=10)
        self.add_hover_effect(btn_register)

        btn_login = tk.Button(self.home_frame, text="🔐 Login User",
                              width=25, height=2, font=("Segoe UI", 11),
                              bg="#f0f0f0", activebackground="#d0e0ff",
                              cursor="hand2", bd=1, relief="raised",
                              command=self.show_login)
        btn_login.pack(pady=10)
        self.add_hover_effect(btn_login)

        self.home_frame.pack(fill="both", expand=True)

    def add_hover_effect(self, button):
        def on_enter(e): button.config(bg="#d0e0ff")
        def on_leave(e): button.config(bg="#f0f0f0")
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def show_register(self):
        self.clear_container()
        self.register_frame = RegisterWindow(self.container, self)
        self.register_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.clear_container()
        self.login_frame = LoginWindow(self.container, self)
        self.login_frame.pack(fill="both", expand=True)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()