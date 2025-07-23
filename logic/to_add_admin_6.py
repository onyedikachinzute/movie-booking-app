import psycopg2
import hashlib

def connect_db():
    return psycopg2.connect(
        dbname="panaview_db",
        user="postgres",        
        password="cos101",    
        host="localhost",
        port="5432"
    )

def add_admin_user(name, email, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        
        # Insert admin user into the users table
        cur.execute("""
            INSERT INTO users (name, email, password, is_admin)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id;
        """, (name, email, password_hash, True))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        print(f"✅ Admin user added successfully with ID: {user_id}")
    
    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ Error adding admin:", e)
    
    finally:
        if conn:
            cur.close()
            conn.close()

def main():
    admin_name = input("Enter admin name: ")
    admin_email = input("Enter admin email: ")
    admin_password = input("Enter admin password: ")
    add_admin_user(admin_name, admin_email, admin_password)

if __name__ == "__main__":
    main()
