import customtkinter as ctk
import sqlite3
import hashlib
import os
import csv
from datetime import datetime
from tkcalendar import DateEntry
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
import pyodbc 
print(pyodbc.drivers())
DB_PATH = "data/budget.db"
ADDITIONAL_DB_PATH = "data/reports.db"
MDB_PATH = "data/exported_data.accdb"

# Inicializācija
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
class BudgetApp(ctk.CTk):
    def __init__(self):
        super().__init__()               
        
        self.style_calendar()       
        self.title("Budžeta Pārvaldnieks")
        self.geometry("500x700")

        self.user_id = None

        self.categories = [
            "Pārtika",
            "Veselība",
            "Ēdieni un restorāni",
            "Transports",
            "Brīvais laiks un dzīvesstils",
            "Iepirkšanās un pakalpojumi",
            "Citi izdevumi",
            "Citi ienākumi"
        ]

        self.types = ["Ienākumi", "Izdevumi"]

        self.create_login_screen()
        self.style_calendar()

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

        #self.export_mdb_btn = ctk.CTkButton(self, text="Eksportēt uz MDB", command=self.export_to_mdb)
        #self.export_mdb_btn.pack(pady=10)

        self.label = ctk.CTkLabel(self, text="Sveiks lietotāj!", font=("Arial", 20))
        self.label.pack(pady=20)

        self.add_btn = ctk.CTkButton(self, text="Pievienot transakciju", command=self.create_add_transaction_screen)
        self.add_btn.pack(pady=10)

        self.view_btn = ctk.CTkButton(self, text="Apskatīt transakcijas", command=self.view_transactions)
        self.view_btn.pack(pady=10)

        self.balance_btn = ctk.CTkButton(self, text="Skatīt bilanci", command=self.view_balance)
        self.balance_btn.pack(pady=10)

        self.export_choice = ctk.StringVar(value="CSV")
        self.export_menu = ctk.CTkOptionMenu(self, values=["CSV", "MDB"], variable=self.export_choice)
        self.export_menu.pack(pady=5)

        self.export_btn = ctk.CTkButton(self, text="Eksportēt", command=self.export_based_on_choice)
        self.export_btn.pack(pady=10)                

        self.stats_btn = ctk.CTkButton(self, text="Rādīt statistiku", command=self.calculate_statistics)
        self.stats_btn.pack(pady=5)        

        self.search_entry = ctk.CTkEntry(self, placeholder_text="Ievadiet meklēto vārdu")
        self.search_entry.pack(pady=5)

        self.search_btn = ctk.CTkButton(self, text="Meklēt pēc kritērijiem", command=lambda: self.search_transactions(self.search_entry.get()))
        self.search_btn.pack(pady=5)        


        self.logout_btn = ctk.CTkButton(self, text="Iziet", command=self.create_login_screen)
        self.logout_btn.pack(pady=10)

    def create_add_transaction_screen(self):
        self.clear_widgets()

        self.label = ctk.CTkLabel(self, text="Jauna Transakcija", font=("Arial", 20))
        self.label.pack(pady=10)

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Summa (EUR)")
        self.amount_entry.pack(pady=5)

        self.category_combobox = ctk.CTkComboBox(self, values=self.categories)
        self.category_combobox.set("Pārtika")
        self.category_combobox.pack(pady=5)

        self.type_combobox = ctk.CTkComboBox(self, values=self.types)
        self.type_combobox.set("Izdevumi")
        self.type_combobox.pack(pady=5)

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
            category = self.category_combobox.get()
            type_ = self.type_combobox.get()
            date = self.date_picker.get_date().strftime("%Y-%m-%d")
            comment = self.comment_entry.get()

            if type_ not in self.types:
                self.show_message("Tips jābūt 'Ienākumi' vai 'Izdevumi'", success=False)
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

    def make_edit_callback(self, transaction):
        return lambda: self.edit_transaction(transaction)

    def make_delete_callback(self, transaction_id):
        return lambda: self.delete_transaction(transaction_id)

    def view_transactions(self):
        self.clear_widgets()

        self.label = ctk.CTkLabel(self, text="Tavas transakcijas", font=("Arial", 18))
        self.label.pack(pady=10)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT date, type, amount, category, comment FROM transactions WHERE user_id = ? ORDER BY date DESC", (self.user_id,))        

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, date, type, amount, category, comment FROM transactions WHERE user_id = ? ORDER BY date DESC", (self.user_id,))
        transactions = cur.fetchall()
        cur.execute("""
         SELECT category, SUM(amount)
            FROM transactions
            WHERE user_id = ? AND type = 'Izdevumi'
            GROUP BY category
        """, (self.user_id,))
        category_data = cur.fetchall()
        conn.close()


        for tx in transactions:
            frame = ctk.CTkFrame(self)
            frame.pack(fill="x", padx=10, pady=2)
            tx_text = " | ".join(str(x) for x in tx[1:]) + "€" if len(tx) >= 6 else str(tx)
            ctk.CTkLabel(frame, text=tx_text, anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(frame, text="Rediģēt", width=60, command=self.make_edit_callback(tx)).pack(side="right", padx=2)
            ctk.CTkButton(frame, text="Dzēst", width=60, command=self.make_delete_callback(tx[0])).pack(side="right", padx=2)
                   

        if category_data:
            categories = [row[0] for row in category_data]
            totals = [row[1] for row in category_data]
            fig, ax = plt.subplots(figsize=(4, 4), facecolor='#2a2a2a')
            wedges, texts, autotexts = ax.pie(
                totals,
                labels=categories,
                autopct='%1.1f%%',
                startangle=90,
                textprops=dict(color="white")
            )
            ax.set_title("Izdevumu sadalījums pa kategorijām", color='white')
            
            for spine in ax.spines.values():
                spine.set_visible(False)

            fig.patch.set_facecolor('#2a2a2a')
            pie_chart = FigureCanvasTkAgg(fig, master=self)
            pie_chart.draw()
            pie_chart.get_tk_widget().pack(pady=10)


        self.back_btn = ctk.CTkButton(self, text="Atpakaļ", command=self.create_main_screen)
        self.back_btn.pack(pady=10)

    def export_based_on_choice(self):
        choice = self.export_choice.get()
        if choice == "CSV":
            self.export_to_csv()
        elif choice == "MDB":
            self.export_to_mdb()

    def delete_transaction(self, transaction_id):
        print("Dzēšam ID:", transaction_id)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, self.user_id))

        conn.commit()
        conn.close()
        self.show_message("✅ Transakcija dzēsta!")
        self.view_transactions()

    def edit_transaction(self, transaction):
        print("Rediģējam:", transaction)
        self.clear_widgets()

        tx_id, date, type_, amount, category, comment = transaction

        self.label = ctk.CTkLabel(self, text="Rediģēt Transakciju", font=("Arial", 20))
        self.label.pack(pady=10)

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Summa (EUR)", textvariable=tk.StringVar(value=str(amount)))
        self.amount_entry.pack(pady=5)

        self.category_combobox = ctk.CTkComboBox(self, values=self.categories)
        self.category_combobox.set(category)
        self.category_combobox.pack(pady=5)

        self.type_combobox = ctk.CTkComboBox(self, values=self.types)
        self.type_combobox.set(type_)
        self.type_combobox.pack(pady=5)

        self.date_picker = DateEntry(self, date_pattern='yyyy-mm-dd')
        self.date_picker.set_date(datetime.strptime(date, "%Y-%m-%d"))
        self.date_picker.pack(pady=5)

        self.comment_entry = ctk.CTkEntry(self, placeholder_text="Komentārs", textvariable=tk.StringVar(value=comment))
        self.comment_entry.pack(pady=5)

        self.update_btn = ctk.CTkButton(self, text="Atjaunināt", command=lambda: self.update_transaction(tx_id))
        self.update_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(self, text="Atpakaļ", command=self.view_transactions)
        self.back_btn.pack(pady=5)

    def make_edit_callback(self, transaction):
             return lambda t=transaction: self.edit_transaction(t)

    def update_transaction(self, tx_id):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_combobox.get()
            type_ = self.type_combobox.get()
            date = self.date_picker.get_date().strftime("%Y-%m-%d")
            comment = self.comment_entry.get()

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE transactions
                SET amount = ?, category = ?, type = ?, date = ?, comment = ?
                WHERE id = ? AND user_id = ?
            """, (amount, category, type_, date, comment, tx_id, self.user_id))
            conn.commit()
            conn.close()

            self.show_message("✅ Transakcija atjaunināta!")
            self.view_transactions()
        except Exception as e:
            self.show_message(f"Kļūda: {str(e)}", success=False)

    def view_balance(self):
        self.clear_widgets()

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'Ienākumi'", (self.user_id,))
        income = cur.fetchone()[0] or 0.0
        cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'Izdevumi'", (self.user_id,))
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

    def style_calendar(self):
        style = ttk.Style()
        style.theme_use('default')
    
        style.configure("TCombobox",
                        fieldbackground="#1f6aa5",
                        background="#1f6aa5",
                        foreground="white")

        style.configure("Calendar.Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        fieldbackground="#2a2d2e",
                        rowheight=25)

        style.map("TCombobox",
                  fieldbackground=[('readonly', '#1f6aa5')],
                  background=[('readonly', '#1f6aa5')],
                  foreground=[('readonly', 'white')])

   
    def style_calendar(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("TCombobox",
                        fieldbackground="#333333",
                        background="#444444",
                        foreground="white")

        style.configure("DateEntry",
                        fieldbackground="#333333",
                        background="#444444",
                        foreground="white",
                        arrowsize=14,
                        relief="flat")

        style.map("DateEntry",
                  fieldbackground=[('readonly', '#333333')],
                  background=[('active', '#555555')],
                  foreground=[('disabled', 'gray')])

    def export_to_mdb(self):
        try:                 
             mdb_path = os.path.abspath(MDB_PATH)
             conn_str = (
                 r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
                 rf"DBQ={mdb_path};"
             )
             conn = pyodbc.connect(conn_str)
             cursor = conn.cursor()

             cursor.execute("""
                 CREATE TABLE IF NOT EXISTS transactions (
                     id AUTOINCREMENT PRIMARY KEY,
                     user_id INT,
                     amount DOUBLE,
                     category TEXT,
                     type TEXT,
                     date TEXT,
                     comment TEXT
                 )
             """)

             sqlite_conn = sqlite3.connect(DB_PATH)
             sqlite_cursor = sqlite_conn.cursor()
             sqlite_cursor.execute("SELECT user_id, amount, category, type, date, comment FROM transactions WHERE user_id = ?", (self.user_id,))
             rows = sqlite_cursor.fetchall()
             sqlite_conn.close()

             for row in rows:
                 cursor.execute("INSERT INTO transactions (user_id, amount, category, type, date, comment) VALUES (?, ?, ?, ?, ?, ?)", row)

             conn.commit()
             conn.close()

             self.show_message("✅ Eksportēts uz MDB veiksmīgi!")

        except Exception as e:
             self.show_message(f"Kļūda MDB eksportā: {str(e)}", success=False)

    def search_transactions(self, keyword):
        self.clear_widgets()
        self.label = ctk.CTkLabel(self, text=f"Meklēšanas rezultāti priekš: {keyword}", font=("Arial", 18))
        self.label.pack(pady=10)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT date, type, amount, category, comment FROM transactions
            WHERE user_id = ? AND (category LIKE ? OR comment LIKE ?)
            ORDER BY date DESC
        """, (self.user_id, f"%{keyword}%", f"%{keyword}%"))
        results = cur.fetchall()
        conn.close()

        for tx in results:
            label = ctk.CTkLabel(self, text=f"{tx[0]} | {tx[1]} | {tx[2]}€ | {tx[3]} | {tx[4]}")
            label.pack(pady=2, anchor="w", padx=10)

        back_btn = ctk.CTkButton(self, text="Atpakaļ", command=self.create_main_screen)
        back_btn.pack(pady=10)

    def calculate_statistics(self):
        self.clear_widgets()
        self.label = ctk.CTkLabel(self, text="Statistika", font=("Arial", 18))
        self.label.pack(pady=10)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT MIN(amount), MAX(amount), SUM(amount), AVG(amount) FROM transactions WHERE user_id = ?", (self.user_id,))
        min_val, max_val, total, average = cur.fetchone()
        conn.close()

        stats = [
            f"Minimālā summa: {min_val:.2f} EUR",
            f"Maksimālā summa: {max_val:.2f} EUR",
            f"Kopējā summa: {total:.2f} EUR",
            f"Vidējā summa: {average:.2f} EUR"
        ]

        for stat in stats:
            label = ctk.CTkLabel(self, text=stat, font=("Arial", 16))
            label.pack(pady=2)

        back_btn = ctk.CTkButton(self, text="Atpakaļ", command=self.create_main_screen)
        back_btn.pack(pady=10)
    


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
if __name__ == "__main__":    
    app = BudgetApp()
    app.mainloop()
