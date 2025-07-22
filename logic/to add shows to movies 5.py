import psycopg2
import random

def get_connection():
    return psycopg2.connect(
        dbname="panaview_db",
        user="postgres",
        password="cos101",
        host="localhost",
        port="5432"
    )



def add_showtimes_for_movie(movie_id, date_str, time1_str, time2_str):
    """
    Adds two showtimes for a movie and auto-generates 60 show_seats each.
    Randomly assigns a base price between 5000 and 9000 (in steps of 500).
    - date_str: 'YYYY-MM-DD'
    - time1_str / time2_str: 'HH:MM'
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Fetch seat IDs (ensure there are 60)
        cur.execute("SELECT seat_id FROM seats ORDER BY seat_id")
        seat_ids = [row[0] for row in cur.fetchall()]
        if len(seat_ids) != 60:
            raise Exception("Exactly 60 seats must exist in the 'seats' table.")

        # Random price from [5000, 5500, ..., 9000]
        base_price = random.choice([price for price in range(5000, 9500, 500)])

        for time_str in [time1_str, time2_str]:
            showtime = f"{date_str} {time_str}"
            cur.execute("""
                INSERT INTO shows (movie_id, start_time, price)
                VALUES (%s, %s, %s)
                RETURNING show_id
            """, (movie_id, showtime, base_price))
            show_id = cur.fetchone()[0]

            # Add 60 show_seats
            for seat_id in seat_ids:
                cur.execute("""
                    INSERT INTO show_seats (show_id, seat_id, is_booked)
                    VALUES (%s, %s, FALSE)
                """, (show_id, seat_id))

            print(f"✅ Added show at {showtime} for movie {movie_id} with 60 show seats. Price: ₦{base_price}")

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ Error adding showtimes:", e)

    finally:
        if conn:
            cur.close()
            conn.close()


# 🔁 Add showtimes for multiple movies
add_showtimes_for_movie(1, "2025-09-12", "11:30", "12:50")
add_showtimes_for_movie(2, "2025-09-12", "13:00", "15:20")
add_showtimes_for_movie(3, "2025-09-13", "10:45", "14:10")
add_showtimes_for_movie(4, "2025-09-13", "09:30", "11:15")
add_showtimes_for_movie(5, "2025-09-14", "14:45", "18:00")
add_showtimes_for_movie(6, "2025-09-14", "12:30", "16:30")
add_showtimes_for_movie(7, "2025-09-15", "15:00", "19:10")
add_showtimes_for_movie(8, "2025-09-15", "11:00", "13:15")
add_showtimes_for_movie(9, "2025-09-15", "14:00", "16:15")
