# 🅿️ Smart Parking Management System

An interactive, database-driven web application built with Python, Streamlit, and MySQL to manage real-time parking slot availability, vehicle entry/exit, automatic billing, and revenue analytics.

---

## 📌 Overview

This project digitizes parking management for a 30-slot parking facility. It tracks slot availability in real time, records vehicle entry and exit with automatic time-based billing, maintains a full parking history, and provides revenue and usage analytics — all through a single, color-coded web dashboard.

---

## ✨ Features

- Live Slot Status — color-coded grid (🟢 Available, 🔴 Occupied, 🟣 Reserved)
- Vehicle Entry — select a slot, choose vehicle type (Car/Bike), enter vehicle number; duplicate entries are automatically blocked
- Vehicle Exit with Billing — automatically calculates parking duration and generates a digital receipt (₹10/hr for cars, ₹5/hr for bikes)
- Vehicle Search — look up any vehicle by registration number to find its current slot or last parking record
- Parking History & Revenue — full transaction log, total revenue collected, daily revenue chart, peak-hour analysis, and most-used slots chart
- Overstay Alerts — flags vehicles parked beyond a configurable time limit
- Manual refresh for the live slot grid

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3 |
| Web Framework | Streamlit |
| Database | MySQL |
| DB Connector | mysql-connector-python |
| Data Handling | Pandas |
| Visualization | Plotly Express |

---

## 🗄️ Database Schema

**slots table**
| Column | Type | Description |
|---|---|---|
| slot_number | INT (PK) | Slot identifier (1–30) |
| status | VARCHAR | Available / Occupied / Reserved |
| vehicle_number | VARCHAR | Currently parked vehicle's number |
| vehicle_type | VARCHAR | Car / Bike |
| entry_time | DATETIME | Time the vehicle was parked |

**parking_history table**
| Column | Type | Description |
|---|---|---|
| id | INT (PK, auto) | Record ID |
| slot_number | INT | Slot used |
| vehicle_number | VARCHAR | Vehicle registration number |
| vehicle_type | VARCHAR | Car / Bike |
| entry_time | DATETIME | Entry timestamp |
| exit_time | DATETIME | Exit timestamp |
| amount | DECIMAL | Bill amount charged |

---

## 📂 Project Structure

parking_system/
└── app.py    (Main Streamlit application with all dashboard tabs)

---

## 🚀 How to Run Locally

1. Clone this repository
   git clone https://github.com/Varsha2719/smart-parking-system.git
   cd smart-parking-system

2. Install the required libraries
   pip install streamlit mysql-connector-python pandas plotly

3. Set up the MySQL database

   CREATE DATABASE parking_system;
   USE parking_system;

   CREATE TABLE slots (
       slot_number INT PRIMARY KEY,
       status VARCHAR(20) DEFAULT 'Available',
       vehicle_number VARCHAR(20),
       entry_time DATETIME,
       vehicle_type VARCHAR(10)
   );

   CREATE TABLE parking_history (
       id INT AUTO_INCREMENT PRIMARY KEY,
       slot_number INT,
       vehicle_number VARCHAR(20),
       entry_time DATETIME,
       exit_time DATETIME,
       amount DECIMAL(10,2),
       vehicle_type VARCHAR(10)
   );

   Then insert 30 slots (slot_number 1–30) with status 'Available'.

4. Update the database password inside app.py (get_connection function).

5. Run the app
   streamlit run app.py

6. Open the link shown in the terminal (usually http://localhost:8501) in your browser.

---

## 🔮 Future Scope

- Real IoT sensor integration (ultrasonic/IR) for automatic slot detection
- QR-code based digital receipts and online payment
- Advance slot booking via a mobile-friendly interface
- Role-based login for operators and administrators
- Cloud deployment with a managed MySQL instance

---

## 👩‍💻 Author

Varsha Gangwar