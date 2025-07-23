import db.create_db_1
from db.create_db_1 import main as createdb_main
import db.init_db_2
from db.init_db_2 import main as initdb_main
import db.Final_table_edits_3
from db.Final_table_edits_3 import main as finaltable_main
import logic.to_add_movies_4
from logic.to_add_movies_4 import main as movies_main
import logic.to_add_shows_to_movies_5
from logic.to_add_shows_to_movies_5 import main as showstomovies_main
import logic.to_add_admin_6
from logic.to_add_admin_6 import main as admin_main

def main():
    print("🔧 Creating database...")
    createdb_main()

    print("📦 Initializing tables...")
    initdb_main()

    print("🛠️ Final table edits...")
    finaltable_main()

    print("🎬 Seeding movies...")
    movies_main()

    print("🕒 Seeding showtimes...")
    showstomovies_main()

    print("👤 Creating admin user...")
    admin_main()

    print("🚀 Successfully Initialized all Database Items and Admin User!")


main()
