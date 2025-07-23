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


## 🧪 How to Run

Follow these steps to set up and run the Movie Booking App on your machine:

### 1. 📁 Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/onyedikachinzute/movie-booking-app.git
cd movie-booking-app 
```

2. 📦 Install Dependencies
Make sure you have Python and pip installed.

Install the required package:
```bash
pip install psycopg2
```

3. 🗄️ Set Up the PostgreSQL Database
Create a PostgreSQL database (e.g. movie_app).

Locate and open the db/create_db1.py file and other related files in db and the project.

Update the connection settings with your PostgreSQL credentials:
```bash
conn = psycopg2.connect(
    host="localhost",
    database="movie_app",
    user="your_username",
    password="your_password"
)
```

4. ▶️ Run the Initialization Application
From your terminal:
```bash
python initdb.py
```

5. ▶️ Run the Application
From your terminal:
```bash
python main.py
```
