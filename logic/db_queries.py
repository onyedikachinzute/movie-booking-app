# This file is where we define all the database functions we are going to use for the gui. 
# This is to make it easier for our code and stuff.

# db_queries.py
import psycopg2
import hashlib

def get_connection():
    return psycopg2.connect(
        dbname="panaview_db",
        user="postgres",
        password="cos101",
        host="localhost",
        port="5432"
    )
    

def register(name, email, password):
    conn = get_connection()
    cur = conn.cursor()
    pwd = password

    try:
        cur.execute("""
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
        """, (name, email, pwd))
        conn.commit()
        return True, "User registered successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def login_user(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, name, email, password, is_admin
        FROM users
        WHERE email = %s;
    """, (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user  # Returns tuple (user_id, name, email, password_hash, is_admin)

def add_movie(title, duration):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO movies (title, duration)
        VALUES (%s, %s)
        RETURNING movie_id;
    """, (title, duration))
    movie_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return movie_id

def add_show(movie_id, start_time, price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO shows (movie_id, start_time, price)
        VALUES (%s, %s, %s)
        RETURNING show_id;
    """, (movie_id, start_time, price))
    show_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return show_id

def get_available_shows():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT shows.show_id, movies.title, shows.start_time, shows.price
        FROM shows
        JOIN movies ON shows.movie_id = movies.movie_id
        ORDER BY shows.start_time;
    """)
    shows = cur.fetchall()
    cur.close()
    conn.close()
    return shows

def get_seats_for_show(show_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ss.show_seat_id, s.seat_number, s.row, s.seat_type, ss.is_booked
        FROM show_seats ss
        JOIN seats s ON ss.seat_id = s.seat_id
        WHERE ss.show_id = %s
        ORDER BY s.row, s.seat_number;
    """, (show_id,))
    seats = cur.fetchall()
    cur.close()
    conn.close()
    return seats

def book_seats(user_id, show_id, selected_show_seat_ids, total_price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bookings (user_id, show_id, total_price)
        VALUES (%s, %s, %s)
        RETURNING booking_id;
    """, (user_id, show_id, total_price))
    booking_id = cur.fetchone()[0]

    for show_seat_id in selected_show_seat_ids:
        cur.execute("""
            INSERT INTO booking_seats (booking_id, show_seat_id)
            VALUES (%s, %s);
        """, (booking_id, show_seat_id))

        cur.execute("""
            UPDATE show_seats
            SET is_booked = TRUE
            WHERE show_seat_id = %s;
        """, (show_seat_id,))

    conn.commit()
    cur.close()
    conn.close()
    return booking_id

def make_button_interactive(button, normal_color="lightgray", hover_color="gray"):
    button.config(bg=normal_color, activebackground=hover_color)
    button.bind("<Enter>", lambda e: button.config(bg=hover_color))
    button.bind("<Leave>", lambda e: button.config(bg=normal_color))
