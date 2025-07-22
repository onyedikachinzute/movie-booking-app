import tkinter as tk
from tkinter import ttk, messagebox as msg
import psycopg2
from tkinter import Toplevel, Listbox, Scrollbar, RIGHT, Y, END
import subprocess 

def open_admin_dashboard(user_id, user_name):
    def logout():
        if msg.askyesno("Logout", "Are you sure you want to log out?"):
            dashboard.destroy()
            try:
                subprocess.run(["python", "main.py"])
            except Exception as e:
                msg.showerror("Error", f"Failed to return to main page:\n{e}")

    def manage_movies():
        def refresh_movie_list():
            listbox.delete(0, tk.END)
            cur.execute("""
                SELECT m.movie_id, m.title, m.duration, COALESCE(MIN(s.price), 0)
                FROM movies m
                LEFT JOIN shows s ON m.movie_id = s.movie_id
                GROUP BY m.movie_id, m.title, m.duration
                ORDER BY m.title
            """)
            for movie_id, title, duration, price in cur.fetchall():
                listbox.insert(tk.END, f"{movie_id} - {title} ({duration} mins) ₦{int(price)}")

        def add_movie():
            import random
            from datetime import datetime, timedelta

            title = title_var.get().strip()
            try:
                duration = int(duration_var.get().strip())
            except ValueError:
                msg.showerror("Invalid Input", "Duration must be a number.")
                return

            if not title or duration <= 0:
                msg.showerror("Missing Fields", "Please enter a valid title and duration.")
                return

            try:
                cur.execute("INSERT INTO movies (title, duration) VALUES (%s, %s) RETURNING movie_id", (title, duration))
                movie_id = cur.fetchone()[0]
                conn.commit()

                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                hours = list(range(10, 20))
                hour1 = random.choice(hours)
                hour2 = random.choice([h for h in hours if abs(h - hour1) >= 2])
                showtime1 = today + timedelta(hours=hour1)
                showtime2 = today + timedelta(hours=hour2)
                base_price = random.choice([price for price in range(5000, 9500, 500)])

                cur.execute("INSERT INTO shows (movie_id, start_time, price) VALUES (%s, %s, %s) RETURNING show_id", (movie_id, showtime1, base_price))
                show_id1 = cur.fetchone()[0]
                cur.execute("INSERT INTO shows (movie_id, start_time, price) VALUES (%s, %s, %s) RETURNING show_id", (movie_id, showtime2, base_price))
                show_id2 = cur.fetchone()[0]
                conn.commit()

                cur.execute("SELECT COUNT(*) FROM seats")
                if cur.fetchone()[0] < 60:
                    cur.execute("DELETE FROM seats")
                    for i in range(1, 61):
                        seat_num = f"S{i:02}"
                        row = chr(65 + (i - 1) // 10)
                        seat_type = 'Luxury' if i <= 10 else 'Normal'
                        cur.execute("INSERT INTO seats (seat_id, seat_number, row, seat_type) VALUES (%s, %s, %s, %s)", (i, seat_num, row, seat_type))
                    conn.commit()

                cur.execute("SELECT seat_id FROM seats ORDER BY seat_id")
                seat_ids = [row[0] for row in cur.fetchall()]
                for show_id in [show_id1, show_id2]:
                    for seat_id in seat_ids:
                        cur.execute("INSERT INTO show_seats (show_id, seat_id, is_booked) VALUES (%s, %s, FALSE)", (show_id, seat_id))
                conn.commit()

                msg.showinfo("✅ Movie Added", f"🎬 '{title}' added with two showtimes.\n🎟 Ticket Price: ₦{base_price}")
                refresh_movie_list()

            except Exception as e:
                conn.rollback()
                msg.showerror("Error", f"Failed to add movie:\n{e}")

        def delete_selected():
            selected = listbox.curselection()
            if not selected:
                msg.showwarning("No Selection", "Select a movie to delete.")
                return

            selected_text = listbox.get(selected[0])
            movie_id = selected_text.split(" - ")[0]

            cur.execute("""
                SELECT m.title, COALESCE(MIN(s.price), 0)
                FROM movies m
                LEFT JOIN shows s ON m.movie_id = s.movie_id
                WHERE m.movie_id = %s
                GROUP BY m.title
            """, (movie_id,))
            movie_data = cur.fetchone()
            if not movie_data:
                msg.showerror("Error", "Movie not found.")
                return
            movie_title, price = movie_data

            confirm = msg.askyesno("Confirm Deletion", f"Delete 🎬 '{movie_title}' (₦{int(price)}) and all related showtimes & seats?")
            if confirm:
                cur.execute("SELECT show_id FROM shows WHERE movie_id = %s", (movie_id,))
                show_ids = [r[0] for r in cur.fetchall()]
                for show_id in show_ids:
                    cur.execute("DELETE FROM show_seats WHERE show_id = %s", (show_id,))
                cur.execute("DELETE FROM shows WHERE movie_id = %s", (movie_id,))
                cur.execute("DELETE FROM movies WHERE movie_id = %s", (movie_id,))
                conn.commit()
                msg.showinfo("🗑️ Deleted", f"'{movie_title}' and all related data have been deleted.")
                refresh_movie_list()

        try:
            conn = psycopg2.connect(
                dbname="panaview_db",
                user="postgres",
                password="cos101",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
        except Exception as e:
            msg.showerror("Database Error", str(e))
            return

        win = Toplevel()
        win.title("Manage Movies")
        win.geometry("500x500")

        title_var = tk.StringVar()
        duration_var = tk.StringVar()

        tk.Label(win, text="🎬 Title:").pack(pady=(10, 0))
        tk.Entry(win, textvariable=title_var, width=40).pack()

        tk.Label(win, text="⏱️ Duration (mins):").pack(pady=(10, 0))
        tk.Entry(win, textvariable=duration_var, width=40).pack()

        tk.Button(win, text="Add Movie", command=add_movie, bg="#d0f0c0").pack(pady=10)

        listbox = tk.Listbox(win, width=60)
        listbox.pack(pady=10)

        tk.Button(win, text="🗑️ Delete Selected Movie", command=delete_selected, bg="#ffcccc").pack()

        refresh_movie_list()

        def on_close():
            cur.close()
            conn.close()
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

    def view_bookings():
        def load_bookings():
            tree.delete(*tree.get_children())
            booking_map.clear()

            cursor.execute("""
                SELECT 
                    b.booking_id, 
                    u.name,
                    u.email,
                    m.title, 
                    s.start_time,
                    b.total_price,
                    ARRAY_AGG(ss.seat_id ORDER BY ss.seat_id) AS seat_ids,
                    COUNT(ss.seat_id) AS total_seats
                FROM bookings b
                JOIN users u ON b.user_id = u.user_id
                JOIN shows s ON b.show_id = s.show_id
                JOIN movies m ON s.movie_id = m.movie_id
                JOIN show_seats ss ON ss.booking_id = b.booking_id
                GROUP BY b.booking_id, u.name, u.email, m.title, s.start_time, b.total_price
                ORDER BY b.booking_time DESC
            """)
            rows = cursor.fetchall()

            if not rows:
                msg.showinfo("No Bookings", "There are no bookings yet.")
                bookings_window.destroy()
                return

            for booking in rows:
                booking_id, name, email, title, start_time, total_price, seat_ids, total_seats = booking
                seat_str = ", ".join(f"S{seat}" for seat in seat_ids)
                tree.insert('', 'end', iid=str(booking_id), values=(
                    booking_id,
                    name,
                    email,
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
        bookings_window.title("All Bookings (Admin)")
        bookings_window.geometry("1150x550")

        cols = ("Booking ID", "User Name", "Email", "Movie Title", "Start Time", "Seats", "Total Seats", "Total Price")
        tree = ttk.Treeview(bookings_window, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=140 if col != "Seats" else 180)
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


    def manage_showtimes():
        try:
            conn = psycopg2.connect(
                dbname="panaview_db",
                user="postgres",
                password="cos101",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
        except Exception as e:
            msg.showerror("Database Error", str(e))
            return

        def refresh_show_list():
            listbox.delete(0, tk.END)
            cur.execute("""
                SELECT s.show_id, m.title, s.start_time, s.price
                FROM shows s
                JOIN movies m ON s.movie_id = m.movie_id
                ORDER BY s.start_time
            """)
            rows = cur.fetchall()
            for row in rows:
                show_id, title, start_time, price = row
                time_str = start_time.strftime('%Y-%m-%d %I:%M %p')
                listbox.insert(tk.END, f"{show_id} - {title} 🕒 {time_str} 💵 ₦{int(price)}")

        def delete_selected_show():
            selected = listbox.curselection()
            if not selected:
                msg.showwarning("No Selection", "Select a showtime to delete.")
                return

            selected_text = listbox.get(selected[0])
            show_id = selected_text.split(" - ")[0]

            confirm = msg.askyesno("Confirm Deletion", "Delete this showtime and all related seat bookings?")
            if confirm:
                try:
                    cur.execute("DELETE FROM show_seats WHERE show_id = %s", (show_id,))
                    cur.execute("DELETE FROM shows WHERE show_id = %s", (show_id,))
                    conn.commit()
                    msg.showinfo("Deleted", "Showtime and related records deleted.")
                    refresh_show_list()
                except Exception as e:
                    conn.rollback()
                    msg.showerror("Error", f"Failed to delete showtime:\n{e}")

        def edit_selected_show():
            selected = listbox.curselection()
            if not selected:
                msg.showwarning("No Selection", "Select a showtime to edit.")
                return

            selected_text = listbox.get(selected[0])
            show_id = selected_text.split(" - ")[0]

            def save_edits():
                new_time = time_var.get().strip()
                new_price = price_var.get().strip()
                try:
                    from datetime import datetime
                    parsed_time = datetime.strptime(new_time, "%Y-%m-%d %H:%M")
                    new_price_val = int(new_price)
                    cur.execute("UPDATE shows SET start_time = %s, price = %s WHERE show_id = %s", (parsed_time, new_price_val, show_id))
                    conn.commit()
                    msg.showinfo("Updated", "Showtime updated successfully.")
                    editor.destroy()
                    refresh_show_list()
                except Exception as e:
                    msg.showerror("Error", f"Failed to update:\n{e}")

            editor = Toplevel()
            editor.title("Edit Showtime")
            editor.geometry("300x200")

            time_var = tk.StringVar()
            price_var = tk.StringVar()

            tk.Label(editor, text="New Start Time (YYYY-MM-DD HH:MM):").pack(pady=(10, 0))
            tk.Entry(editor, textvariable=time_var).pack()

            tk.Label(editor, text="New Price (₦):").pack(pady=(10, 0))
            tk.Entry(editor, textvariable=price_var).pack()

            tk.Button(editor, text="Save", command=save_edits, bg="#ccffcc").pack(pady=10)

        win = Toplevel()
        win.title("Manage Showtimes")
        win.geometry("600x500")

        tk.Label(win, text="🎞️ Showtimes", font=("Segoe UI", 14, "bold")).pack(pady=10)

        listbox = Listbox(win, width=80, font=("Segoe UI", 10))
        listbox.pack(pady=10)

        tk.Button(win, text="🗑️ Delete Selected Showtime", command=delete_selected_show, bg="#ffcccc").pack(pady=5)
        tk.Button(win, text="✏️ Edit Selected Showtime", command=edit_selected_show, bg="#d0e0ff").pack(pady=5)

        refresh_show_list()

        def on_close():
            cur.close()
            conn.close()
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

    def view_seat_occupancy():
        try:
            conn = psycopg2.connect(
                dbname="panaview_db",
                user="postgres",
                password="cos101",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            cur.execute("""
                SELECT s.show_id, m.title, s.start_time
                FROM shows s
                JOIN movies m ON s.movie_id = m.movie_id
                ORDER BY m.title, s.start_time
            """)
            shows = cur.fetchall()

            if not shows:
                msg.showinfo("No Shows", "There are no shows available.")
                return

            popup = Toplevel()
            popup.title("Seat Occupancy Viewer")
            popup.geometry("800x700")
            popup.configure(bg="black")

            selected_show = tk.StringVar()
            show_options = [f"{show_id} - {title} @ {start_time.strftime('%Y-%m-%d %I:%M %p')}" for show_id, title, start_time in shows]
            selected_show.set(show_options[0])

            dropdown = tk.OptionMenu(popup, selected_show, *show_options)
            dropdown.config(font=("Segoe UI", 12))
            dropdown.pack(pady=10)

            canvas = tk.Canvas(popup, width=760, height=600, bg="black", highlightthickness=0)
            canvas.pack()

            def draw_seats():
                canvas.delete("all")
                selected_text = selected_show.get()
                show_id = selected_text.split(" - ")[0]

                cur.execute("""
                    SELECT ss.seat_id, ss.is_booked, st.seat_number
                    FROM show_seats ss
                    JOIN seats st ON ss.seat_id = st.seat_id
                    WHERE ss.show_id = %s
                    ORDER BY st.seat_id
                """, (show_id,))
                seats = cur.fetchall()

                if len(seats) != 60:
                    msg.showerror("Error", "Expected 60 seats per show.")
                    return

                seat_width = seat_height = 30
                spacing = 10
                offset_x = 60
                offset_y = 60
                gap_between_sections = 80
                luxury_spacing_y = 40  # Space between luxury and normal seats

                for i in range(60):
                    seat_id, is_booked, seat_number = seats[i]
                    fill_color = "red" if is_booked else "grey"

                    if i < 5:
                        # Left luxury row
                        col = i
                        x = offset_x + col * (seat_width + spacing)
                        y = offset_y
                    elif i >= 5 and i < 30:
                        # Left normal seats (5 rows of 5)
                        idx = i - 5
                        row = idx // 5
                        col = idx % 5
                        x = offset_x + col * (seat_width + spacing)
                        y = offset_y + seat_height + luxury_spacing_y + row * (seat_height + spacing)
                    elif i >= 30 and i < 35:
                        # Right luxury row
                        col = i - 30
                        x = offset_x + 5 * (seat_width + spacing) + gap_between_sections + col * (seat_width + spacing)
                        y = offset_y
                    else:
                        # Right normal seats (5 rows of 5)
                        idx = i - 35
                        row = idx // 5
                        col = idx % 5
                        x = offset_x + 5 * (seat_width + spacing) + gap_between_sections + col * (seat_width + spacing)
                        y = offset_y + seat_height + luxury_spacing_y + row * (seat_height + spacing)

                    canvas.create_rectangle(x, y, x + seat_width, y + seat_height, fill=fill_color, outline="white")
                    canvas.create_text(x + seat_width / 2, y + seat_height / 2, text=seat_number, fill="white", font=("Segoe UI", 8))

            draw_seats()
            selected_show.trace("w", lambda *args: draw_seats())

            def on_close():
                cur.close()
                conn.close()
                popup.destroy()

            popup.protocol("WM_DELETE_WINDOW", on_close)

        except Exception as e:
            msg.showerror("Database Error", str(e))

    def see_available_movies():
        try:
            conn = psycopg2.connect(
                dbname="panaview_db",
                user="postgres",
                password="cos101",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT m.title, s.start_time, s.price
                FROM movies m
                JOIN shows s ON m.movie_id = s.movie_id
                ORDER BY m.title, s.start_time
            """)
            results = cur.fetchall()

            if not results:
                msg.showinfo("No Data", "No movies or showtimes found.")
                return

            movie_showtimes = {}
            for title, start_time, price in results:
                if start_time:
                    movie_showtimes.setdefault(title, []).append((start_time, price))

            popup = Toplevel()
            popup.title("Available Movies & Showtimes")
            popup.geometry("500x400")

            scrollbar = Scrollbar(popup)
            scrollbar.pack(side=RIGHT, fill=Y)

            listbox = Listbox(popup, font=("Segoe UI", 12), yscrollcommand=scrollbar.set)

            any_inserted = False
            for title, show_info in movie_showtimes.items():
                if show_info:
                    listbox.insert(END, f"🎬 {title}")
                    for start_time, price in show_info[:2]:
                        try:
                            time_str = start_time.strftime('%Y-%m-%d %I:%M %p')
                            listbox.insert(END, f"    🕒 {time_str}   💵 ₦{int(price)}")
                        except Exception:
                            listbox.insert(END, f"    🕒 [Invalid date]   💵 ₦{int(price)}")
                    listbox.insert(END, "")
                    any_inserted = True

            if not any_inserted:
                listbox.insert(END, "No valid showtimes available.")

            listbox.pack(fill="both", expand=True, padx=10, pady=10)
            scrollbar.config(command=listbox.yview)

            cur.close()
            conn.close()

        except Exception as e:
            msg.showerror("Database Error", str(e))


    # The GUI proper
    dashboard = tk.Tk()
    dashboard.title("Admin Dashboard")
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
        text=f"👤 Hello, {user_name}!",
        font=("Segoe UI", 20, "bold"),
        fg="green",
        bg="white"
    )
    greeting.pack(pady=30)

    button_style = {
        "font": ("Segoe UI", 12),
        "width": 30,
        "padx": 10,
        "pady": 10,
        "bg": "#f0f0f0",
        "activebackground": "#d0e0ff",
        "cursor": "hand2"
    }

    tk.Button(dashboard, text="🎟️ See Available Movies & Showtimes", command=see_available_movies, **button_style).pack(pady=5)
    tk.Button(dashboard, text="🎬 Manage Movies", command=manage_movies, **button_style).pack(pady=5)
    tk.Button(dashboard, text="🕒 Manage Showtimes", command=manage_showtimes, **button_style).pack(pady=5)
    tk.Button(dashboard, text="📑 View Bookings", command=view_bookings, **button_style).pack(pady=5)
    tk.Button(dashboard, text="🪑 View Seat Occupancy", command=view_seat_occupancy, **button_style).pack(pady=5)


    dashboard.mainloop()
