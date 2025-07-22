import psycopg2

def apply_on_delete_cascade():
    try:
        conn = psycopg2.connect(
            dbname="panaview_db",
            user="postgres",
            password="cos101",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

 
        drop_constraints = [
            "ALTER TABLE shows DROP CONSTRAINT IF EXISTS shows_movie_id_fkey;",
            "ALTER TABLE show_seats DROP CONSTRAINT IF EXISTS show_seats_show_id_fkey;",
            "ALTER TABLE show_seats DROP CONSTRAINT IF EXISTS show_seats_seat_id_fkey;",
            "ALTER TABLE bookings DROP CONSTRAINT IF EXISTS bookings_show_id_fkey;",
            "ALTER TABLE bookings DROP CONSTRAINT IF EXISTS bookings_user_id_fkey;",
            "ALTER TABLE booking_seats DROP CONSTRAINT IF EXISTS booking_seats_booking_id_fkey;",
            "ALTER TABLE booking_seats DROP CONSTRAINT IF EXISTS booking_seats_show_seat_id_fkey;"
        ]

        for query in drop_constraints:
            cur.execute(query)


        add_constraints = [
            """
            ALTER TABLE shows
            ADD CONSTRAINT shows_movie_id_fkey
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE;
            """,
            """
            ALTER TABLE show_seats
            ADD CONSTRAINT show_seats_show_id_fkey
            FOREIGN KEY (show_id) REFERENCES shows(show_id) ON DELETE CASCADE;
            """,
            """
            ALTER TABLE show_seats
            ADD CONSTRAINT show_seats_seat_id_fkey
            FOREIGN KEY (seat_id) REFERENCES seats(seat_id);
            """,
            """
            ALTER TABLE bookings
            ADD CONSTRAINT bookings_show_id_fkey
            FOREIGN KEY (show_id) REFERENCES shows(show_id) ON DELETE CASCADE;
            """,
            """
            ALTER TABLE bookings
            ADD CONSTRAINT bookings_user_id_fkey
            FOREIGN KEY (user_id) REFERENCES users(user_id);
            """,
            """
            ALTER TABLE booking_seats
            ADD CONSTRAINT booking_seats_booking_id_fkey
            FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE;
            """,
            """
            ALTER TABLE booking_seats
            ADD CONSTRAINT booking_seats_show_seat_id_fkey
            FOREIGN KEY (show_seat_id) REFERENCES show_seats(show_seat_id);
            """,
            """
            DO $$
            BEGIN
            IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'show_seats' AND column_name = 'booking_id'
            ) THEN
            ALTER TABLE show_seats ADD COLUMN booking_id INTEGER;
            END IF;
            END $$;
            """,
            """
            DO $$
            BEGIN
            IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'fk_booking'
            ) THEN
            ALTER TABLE show_seats
            ADD CONSTRAINT fk_booking
            FOREIGN KEY (booking_id)
            REFERENCES bookings(booking_id)
            ON DELETE SET NULL;
            END IF;
            END $$;
            """
        ]

        for query in add_constraints:
            cur.execute(query)

        conn.commit()
        print("✅ Foreign key constraints updated with ON DELETE CASCADE.")
        print("Database schema updated with booking_id column and foreign key constraint.")


    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    apply_on_delete_cascade()
