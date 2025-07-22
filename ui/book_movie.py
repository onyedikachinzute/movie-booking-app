import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime

conn = psycopg2.connect(database="panaview_db", user="postgres", password="cos101", host="localhost", port="5432")
cursor = conn.cursor()

def book_movie(user_id):
    def load_shows():
        try:
            cursor.execute("""
                SELECT s.show_id, m.title, s.start_time, s.price
                FROM shows s
                JOIN movies m ON s.movie_id = m.movie_id
                ORDER BY s.start_time
            """)
            shows = cursor.fetchall()
            for show in shows:
                show_list.insert('', 'end', values=show)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to load shows.\n{e}")

    def confirm_selection():
        selected = show_list.selection()
        if not selected:
            messagebox.showwarning("Select Show", "Please select a show.")
            return
        values = show_list.item(selected[0])['values']
        show_id, title, show_time, price = values
        show_selection_window.destroy()
        open_seat_selection(show_id, title, show_time, price, user_id)

    show_selection_window = tk.Toplevel()
    show_selection_window.title("Select a Show")
    show_selection_window.geometry("600x400")

    cols = ("Show ID", "Title", "Time", "Price")
    show_list = ttk.Treeview(show_selection_window, columns=cols, show="headings")
    for col in cols:
        show_list.heading(col, text=col)
        show_list.column(col, width=150)
    show_list.pack(pady=20)

    load_shows()
    ttk.Button(show_selection_window, text="Next", command=confirm_selection).pack()

def open_seat_selection(show_id, title, show_time, price, user_id):
    def toggle_seat(btn, seat_id):
        if seat_id in selected_seats:
            selected_seats.remove(seat_id)
            btn.config(bg='gray')
        else:
            selected_seats.add(seat_id)
            btn.config(bg='green')

    def proceed_to_overview():
        if not selected_seats:
            messagebox.showwarning("Select Seats", "Please select at least one seat.")
            return
        seat_window.destroy()
        show_overview()

    seat_window = tk.Toplevel()
    seat_window.title("Select Seats")
    seat_window.configure(bg='black')

    selected_seats = set()

    try:
        cursor.execute("SELECT seat_id, is_booked FROM show_seats WHERE show_id = %s ORDER BY seat_id", (show_id,))
        seats = cursor.fetchall()
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Database Error", f"Failed to load seats.\n{e}")
        return

    seat_buttons = {}
    for i, (seat_id, is_booked) in enumerate(seats):
        side = 'left' if i < 30 else 'right'
        seat_index = i if side == 'left' else i - 30
        is_luxury = seat_index < 5
        col = seat_index % 5
        row = seat_index // 5
        y_offset = 1 if is_luxury else 3
        x_base = 0 if side == 'left' else 6

        btn = tk.Button(
            seat_window,
            text=f"S{seat_id}",
            bg='red' if is_booked else 'gray',
            fg='white',
            width=4,
            height=2,
            state='disabled' if is_booked else 'normal'
        )

        btn.grid(row=row + y_offset, column=col + x_base, padx=5, pady=5)

        if not is_booked:
            btn.config(command=lambda b=btn, sid=seat_id: toggle_seat(b, sid))

        seat_buttons[seat_id] = btn

    ttk.Button(seat_window, text="Confirm Seats", command=proceed_to_overview).grid(row=10, column=0, columnspan=12, pady=20)

    seat_window.geometry("800x600")

    def show_overview():
        total_price = len(selected_seats) * float(price)

        def confirm_booking():
            try:
                cursor.execute(
                    "INSERT INTO bookings (user_id, show_id, booking_time, total_price) VALUES (%s, %s, %s, %s) RETURNING booking_id",
                    (user_id, show_id, datetime.now(), total_price)
                )
                booking_id = cursor.fetchone()[0]
                conn.commit()
                for seat_id in selected_seats:
                    cursor.execute("""
                        UPDATE show_seats 
                        SET is_booked = TRUE, booking_id = %s 
                        WHERE seat_id = %s AND show_id = %s
                    """, (booking_id, seat_id, show_id))
                conn.commit()
                messagebox.showinfo("Booking Confirmed", f"Booking ID: {booking_id}")
                overview_window.destroy()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Booking Error", f"Could not confirm booking.\n{e}")

        overview_window = tk.Toplevel()
        overview_window.title("Booking Overview")

        ttk.Label(overview_window, text=f"Movie: {title}").pack(pady=5)
        ttk.Label(overview_window, text=f"Show Time: {show_time}").pack(pady=5)
        ttk.Label(overview_window, text=f"Seats Selected: {len(selected_seats)}").pack(pady=5)
        ttk.Label(overview_window, text=f"Total Price: ₦{total_price}").pack(pady=5)
        ttk.Button(overview_window, text="Confirm Booking", command=confirm_booking).pack(pady=10)

        overview_window.geometry("400x300")
