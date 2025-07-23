import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="panaview_db",
        user="postgres",
        password="cos101",
        host="localhost",
        port="5432"
    )

def add_movie(title, duration):
    conn = None
    movie_id = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO movies (title, duration)
            VALUES (%s, %s)
            RETURNING movie_id;
        """, (title, duration))
        movie_id = cur.fetchone()[0]
        conn.commit()
        print(f"✅ Added movie: {title} ({duration} mins)")
    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ Error adding movie:", e)
    finally:
        if conn:
            cur.close()
            conn.close()
    return movie_id

def main():
    add_movie("Guns Up", 128)
    add_movie("Imported Wives", 111)
    add_movie("Karate Kid: Legends", 118)
    add_movie("Lilo & Stitch", 108)
    add_movie("Mission: Impossible -- The Final Reckoning", 170)
    add_movie("My Mother is a Witch", 100)
    add_movie("Final Destination: Bloodlines", 109)
    add_movie("Thunderbolts", 126)
    add_movie("Sinners", 137)

if __name__ == "__main__":
    main()
