import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="panaview_db",
        user="postgres",
        password="cos101",
        host="localhost",
        port="5432"
    )

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Create all tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        password TEXT,
        is_admin BOOLEAN DEFAULT FALSE
    );

    CREATE TABLE IF NOT EXISTS movies (
        movie_id SERIAL PRIMARY KEY,
        title VARCHAR(100),
        duration INT
    );

    CREATE TABLE IF NOT EXISTS shows (
        show_id SERIAL PRIMARY KEY,
        movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
        start_time TIMESTAMP,
        price NUMERIC
    );

    CREATE TABLE IF NOT EXISTS seats (
        seat_id SERIAL PRIMARY KEY,
        seat_number VARCHAR(10),
        row VARCHAR(5),
        seat_type VARCHAR(20)
    );

    CREATE TABLE IF NOT EXISTS show_seats (
        show_seat_id SERIAL PRIMARY KEY,
        show_id INT REFERENCES shows(show_id) ON DELETE CASCADE,
        seat_id INT REFERENCES seats(seat_id),
        is_booked BOOLEAN DEFAULT FALSE
    );

    CREATE TABLE IF NOT EXISTS bookings (
        booking_id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(user_id),
        show_id INT REFERENCES shows(show_id) ON DELETE CASCADE,
        booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_price NUMERIC
    );

    CREATE TABLE IF NOT EXISTS booking_seats (
        id SERIAL PRIMARY KEY,
        booking_id INT REFERENCES bookings(booking_id) ON DELETE CASCADE,
        show_seat_id INT REFERENCES show_seats(show_seat_id)
    );
    """)

    conn.commit()

    # 🪑 Ensure 60 seats exist
    cur.execute("SELECT COUNT(*) FROM seats")
    count = cur.fetchone()[0]
    if count < 60:
        print("Inserting default 60 seats...")
        cur.execute("DELETE FROM seats")  # clean slate
        for i in range(1, 61):
            seat_number = f"S{i:02}"
            row = chr(65 + (i - 1) // 10)  # Rows A-F
            seat_type = "Luxury" if i <= 10 else "Normal"
            cur.execute("""
                INSERT INTO seats (seat_number, row, seat_type)
                VALUES (%s, %s, %s)
            """, (seat_number, row, seat_type))
        conn.commit()

    # 🎟️ Ensure each show has 60 show_seats
    cur.execute("SELECT show_id FROM shows")
    show_ids = [row[0] for row in cur.fetchall()]
    if show_ids:
        cur.execute("SELECT seat_id FROM seats ORDER BY seat_id")
        seat_ids = [row[0] for row in cur.fetchall()]
        for show_id in show_ids:
            cur.execute("SELECT COUNT(*) FROM show_seats WHERE show_id = %s", (show_id,))
            if cur.fetchone()[0] < 60:
                print(f"Adding show_seats for show_id {show_id}...")
                for seat_id in seat_ids:
                    cur.execute("""
                        INSERT INTO show_seats (show_id, seat_id, is_booked)
                        VALUES (%s, %s, FALSE)
                    """, (show_id, seat_id))
        conn.commit()

    print("✅ Tables created and initialized.")
    cur.close()
    conn.close()
    
def main():
    create_tables()

if __name__ == "__main__":
    main()