import customtkinter as ctk
import sqlite3
import hashlib
import os
import csv
from datetime import datetime
from tkcalendar import DateEntry
import tkinter as tk
from tkinter import filedialog

DB_PATH = "data/budget.db"

# Inicializācija
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class BudgetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budžeta Pārvaldnieks")
        self.geometry("400x600")

        self.user_id = None

        self.create_login_screen()

    def create_login_screen(self):
        self.clear_widgets()

        self.label = ctk.CTkLabel(self, text="Pieteikšanās", font=("Arial", 20))
        self.label.pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Lietotājvārds")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Parole", show="*")
        self.password_entry.pack(pady=10)

        self.login_button = ctk.CTkButton(self, text="Pieteikties", command=self.login)
        self.login_button.pack(pady=10)

        self.register_button = ctk.CTkButton(self, text="Reģistrēties", command=self.create_register_screen)
        self.register_button.pack(pady=5)

    def create_register_screen(self):
        self.clear_widgets()

        self.label = ctk.CTkLabel(self, text="Reģistrācija", font=("Arial", 20))
        self.label.pack(pady=20)

        self.new_username = ctk.CTkEntry(self, placeholder_text="Jauns lietotājvārds")
        self.new_username.pack(pady=10)

        self.new_password = ctk.CTkEntry(self, placeholder_text="Parole", show="*")
        self.new_password.pack(pady=10)

        self.register_btn = ctk.CTkButton(self, text="Izveidot kontu", command=self.register)
        self.register_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(self, text="Atpakaļ", command=self.create_login_screen)
        self.back_btn.pack(pady=5)

    def create_main_screen(self):
        self.clear_widgets()

        self.label = ctk.CTkLabel(self, text="Sveiks lietotāj!", font=("Arial", 20))
        self.label.pack(pady=20)

        self.add_btn = ctk.CTkButton(self, text="Pievienot transakciju", command=self.create_add_transaction_screen)
        self.add_btn.pack(pady=10)

        self.view_btn = ctk.CTkButton(self, text="Apskatīt transakcijas", command=self.view_transactions)
        self.view_btn.pack(pady=10)

        self.balance_btn = ctk.CTkButton(self, text="Skatīt bilanci", command=self.view_balance)
        self.balance_btn.pack(pady=10)

        self.export_btn = ctk.CTkButton(self, text="Eksportēt CSV", command=self.export_to_csv)
        self.export_btn.pack(pady=10)

        self.logout_btn = ctk.CTkButton(self, text="Iziet", command=self.create_login_screen)
        self.logout_btn.pack(pady=10)

    def export_to_csv(self):
        try:
            filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not filepath:
                return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT date, type, amount, category, comment FROM transactions WHERE user_id = ? ORDER BY date DESC", (self.user_id,))
            transactions = cur.fetchall()
            conn.close()

            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Datums", "Tips", "Summa", "Kategorija", "Komentārs"])
                writer.writerows(transactions)

            self.show_message("✅ Eksportēts uz CSV veiksmīgi!")
        except Exception as e:
            self.show_message(f"Kļūda: {str(e)}", success=False)
        
    def show_message(self, text, success=True):
       color = "green" if success else "red"
       label = ctk.CTkLabel(self, text=text, text_color=color)
       label.pack(pady=5)

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

# DB Setup
if not os.path.exists("data"):
    os.makedirs("data")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        type TEXT,
        date TEXT,
        comment TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
conn.commit()
conn.close()

# Start
app = BudgetApp()
app.mainloop()