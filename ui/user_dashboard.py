import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk
import subprocess
from ui.book_movie import book_movie
import psycopg2

def open_user_dashboard(user_id, user_name):
    def logout():
        if msg.askyesno("Logout", "Are you sure you want to log out?"):
            dashboard.destroy()
            try:
                subprocess.run(["python", "main.py"])
            except Exception as e:
                msg.showerror("Error", f"Failed to return to main page:\n{e}")

    def view_bookings():
        def load_bookings():
            tree.delete(*tree.get_children())
            booking_map.clear()

            cursor.execute("""
                SELECT 
                    b.booking_id, 
                    m.title, 
                    s.start_time,
                    b.total_price,
                    ARRAY_AGG(ss.seat_id ORDER BY ss.seat_id) AS seat_ids,
                    COUNT(ss.seat_id) AS total_seats
                FROM bookings b
                JOIN shows s ON b.show_id = s.show_id
                JOIN movies m ON s.movie_id = m.movie_id
                JOIN show_seats ss ON ss.booking_id = b.booking_id
                WHERE b.user_id = %s
                GROUP BY b.booking_id, m.title, s.start_time, b.total_price
                ORDER BY b.booking_time DESC
            """, (user_id,))
            rows = cursor.fetchall()

            if not rows:
                msg.showinfo("No Bookings", "You have not made any bookings yet.")
                bookings_window.destroy()
                return

            for booking in rows:
                booking_id, title, start_time, total_price, seat_ids, total_seats = booking
                seat_str = ", ".join(f"S{seat}" for seat in seat_ids)
                tree.insert('', 'end', iid=str(booking_id), values=(
                    booking_id,
                    title,
                    start_time.strftime("%Y-%m-%d %H:%M"),
                    seat_str,
                    total_seats,
                    f"₦{total_price:,.2f}"
                ))
                booking_map[str(booking_id)] = seat_ids

        conn = psycopg2.connect(
            database="panaview_db",
            user="postgres",
            password="cos101",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        bookings_window = tk.Toplevel()
        bookings_window.title("My Bookings")
        bookings_window.geometry("1000x550")

        cols = ("Booking ID", "Movie Title", "Start Time", "Seats", "Total Seats", "Total Price")
        tree = ttk.Treeview(bookings_window, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120 if col != "Movie Title" else 180)
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        booking_map = {}

        def delete_selected_booking():
            selected = tree.selection()
            if not selected:
                msg.showwarning("No selection", "Please select a booking to delete.")
                return

            booking_id = selected[0]

            if not msg.askyesno("Delete Booking", f"Are you sure you want to delete booking ID {booking_id}?"):
                return

            try:
                cursor.execute("""
                    UPDATE show_seats
                    SET is_booked = FALSE,
                        booking_id = NULL
                    WHERE booking_id = %s
                """, (booking_id,))

                cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
                conn.commit()

                load_bookings()
                msg.showinfo("Deleted", f"Booking ID {booking_id} deleted successfully.")
            except Exception as e:
                conn.rollback()
                msg.showerror("Error", f"Failed to delete booking:\n{e}")

        ttk.Button(bookings_window, text="Delete Booking", command=delete_selected_booking).pack(pady=5)
        ttk.Button(bookings_window, text="Close", command=bookings_window.destroy).pack(pady=5)

        load_bookings()


    dashboard = tk.Tk()
    dashboard.title("User Dashboard")
    dashboard.geometry("800x500")
    dashboard.configure(bg="white")

    logout_button = tk.Button(
        dashboard,
        text="🔙 Logout",
        command=logout,
        font=("Segoe UI", 10, "bold"),
        bg="#ffdddd",
        activebackground="#ffcccc",
        cursor="hand2"
    )
    logout_button.place(x=10, y=10)

    greeting = tk.Label(
        dashboard,
        text=f"👋 Welcome, {user_name}!",
        font=("Segoe UI", 20, "bold"),
        fg="blue",
        bg="white"
    )
    greeting.pack(pady=50)

    button_style = {
        "font": ("Segoe UI", 12),
        "width": 30,
        "padx": 10,
        "pady": 10,
        "bg": "#f0f0f0",
        "activebackground": "#d0e0ff",
        "cursor": "hand2"
    }

    tk.Button(dashboard, text="🎥 Book A Movie", command=lambda: book_movie(user_id), **button_style).pack(pady=10)
    tk.Button(dashboard, text="📄 View My Bookings", command=view_bookings, **button_style).pack(pady=10)

    dashboard.mainloop()
