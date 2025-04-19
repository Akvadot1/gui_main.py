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

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=? AND password=?", (username, hashed))
        result = cur.fetchone()
        conn.close()

        if result:
            self.user_id = result[0]
            self.show_message("Veiksmīga pieteikšanās!", success=True)
            self.create_main_screen()
        else:
            self.show_message("Nepareizi dati", success=False)

    def register(self):
        username = self.new_username.get()
        password = self.new_password.get()
        hashed = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            self.show_message("Reģistrācija veiksmīga!", success=True)
            self.create_login_screen()
        except sqlite3.IntegrityError:
            self.show_message("Lietotājvārds jau eksistē", success=False)
        conn.close()

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

    def create_add_transaction_screen(self):
        self.clear_widgets()

        self.label = ctk.CTkLabel(self, text="Jauna Transakcija", font=("Arial", 20))
        self.label.pack(pady=10)

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Summa (EUR)")
        self.amount_entry.pack(pady=5)

        self.category_entry = ctk.CTkEntry(self, placeholder_text="Kategorija")
        self.category_entry.pack(pady=5)

        self.type_entry = ctk.CTkEntry(self, placeholder_text="Tips (income/expense)")
        self.type_entry.pack(pady=5)

        self.date_picker = DateEntry(self, date_pattern='yyyy-mm-dd')
        self.date_picker.pack(pady=5)

        self.comment_entry = ctk.CTkEntry(self, placeholder_text="Komentārs")
        self.comment_entry.pack(pady=5)

        self.save_btn = ctk.CTkButton(self, text="Saglabāt", command=self.save_transaction)
        self.save_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(self, text="Atpakaļ", command=self.create_main_screen)
        self.back_btn.pack(pady=5)

    def save_transaction(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_entry.get()
            type_ = self.type_entry.get().strip().lower()
            date = self.date_picker.get_date().strftime("%Y-%m-%d")
            comment = self.comment_entry.get()

            if type_ not in ["income", "expense"]:
                self.show_message("Tips jābūt 'income' vai 'expense'", success=False)
                return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO transactions (user_id, amount, category, type, date, comment)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.user_id, amount, category, type_, date, comment))
            conn.commit()
            conn.close()

            self.show_message("✅ Transakcija pievienota!")
            self.create_main_screen()
        except Exception as e:
            self.show_message(f"Kļūda: {str(e)}", success=False)

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

            generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn2 = sqlite3.connect(ADDITIONAL_DB_PATH)
            cur2 = conn2.cursor()
            cur2.execute("INSERT INTO reports (user_id, generated_at, filename) VALUES (?, ?, ?)", (self.user_id, generated_at, filepath))
            conn2.commit()
            conn2.close()

            self.show_message("✅ Eksportēts uz CSV veiksmīgi!")
        except Exception as e:
            self.show_message(f"Kļūda: {str(e)}", success=False)

    def view_transactions(self):
        self.clear_widgets()

        self.label = ctk.CTkLabel(self, text="Tavas transakcijas", font=("Arial", 18))
        self.label.pack(pady=10)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT date, type, amount, category, comment FROM transactions WHERE user_id = ? ORDER BY date DESC", (self.user_id,))
        transactions = cur.fetchall()
        conn.close()

        for tx in transactions:
            tx_label = ctk.CTkLabel(self, text=f"{tx[0]} | {tx[1]} | {tx[2]}€ | {tx[3]} | {tx[4]}", anchor="w")
            tx_label.pack(pady=2, anchor="w", padx=10)

        self.back_btn = ctk.CTkButton(self, text="Atpakaļ", command=self.create_main_screen)
        self.back_btn.pack(pady=10)

    def view_balance(self):
        self.clear_widgets()

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'income'", (self.user_id,))
        income = cur.fetchone()[0] or 0.0
        cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'expense'", (self.user_id,))
        expense = cur.fetchone()[0] or 0.0
        balance = income - expense
        conn.close()

        ctk.CTkLabel(self, text=f"Ienākumi: {income:.2f} EUR", font=("Arial", 16)).pack(pady=5)
        ctk.CTkLabel(self, text=f"Izdevumi: {expense:.2f} EUR", font=("Arial", 16)).pack(pady=5)
        ctk.CTkLabel(self, text=f"Bilance: {balance:.2f} EUR", font=("Arial", 18, "bold")).pack(pady=10)

        self.back_btn = ctk.CTkButton(self, text="Atpakaļ", command=self.create_main_screen)
        self.back_btn.pack(pady=10)

    def show_message(self, text, success=True):
        color = "green" if success else "red"
        label = ctk.CTkLabel(self, text=text, text_color=color)
        label.pack(pady=5)

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

# === DB Setup (primary database) ===
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

# === Additional Database (e.g., reports.db) ===
ADDITIONAL_DB_PATH = "data/reports.db"

conn2 = sqlite3.connect(ADDITIONAL_DB_PATH)
cur2 = conn2.cursor()
cur2.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        generated_at TEXT,
        filename TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
conn2.commit()
conn2.close()

# Start
app = BudgetApp()
app.mainloop()