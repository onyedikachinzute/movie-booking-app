# 📽️ Movie Booking App

An SQL and Python-based movie reservation and booking application.  
This project allows users to view available movies, select showtimes, pick seats, and complete bookings.  
It also includes an admin interface for managing movies and viewing seat occupancy.

---

## 🚀 Features

### 🎟️ User Functionality
- Browse available movies and showtimes
- View ticket prices
- Select and reserve seats (with live seat availability)
- Generate booking receipts with total cost
- Save booking details into the database

### 🎬 Admin Functionality
- Add or delete movies and showtimes
- View seat occupancy by show
- Automatically remove associated shows when a movie is deleted

---

## 🛠️ Technologies Used

- **Python** (main logic and GUI via `tkinter`)
- **PostgreSQL** (database storage for movies, shows, bookings)
- **Tkinter** (GUI for both user and admin dashboards)
- **psycopg2** (for PostgreSQL-Python connection)

---

## 🗂️ Project Structure

movie-booking-app/
│
├── db/ # Database initialization and edits
│ └── create_db 1.py
| └── init_db 2.py
| └── Final table edits 3.py
│
├── logic/ # To add to the database
│ ├── to add movies 4.py
│ └── to add shows to movies 5.py
| └── to add admin 6.py
| └── db_queries.py
│
├── ui/ # GUI modules
│ ├── admin_dashboard.py
│ └── user_dashboard.py
| └── login_ui.py
| └── register_ui.py
| └── book_movie.py
│
├── main.py # Entry point of the application
├── README.md # This file
├── LICENSE # MIT License
