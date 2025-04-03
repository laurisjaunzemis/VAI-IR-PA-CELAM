import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class CarpoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Koplietošanas App")
        self.root.geometry("800x600")
        
        # Datu bāzes inicializācija
        self.conn = sqlite3.connect('carpool.db')
        self.c = self.conn.cursor()
        self.create_tables()
        
        # Lietotāja stāvoklis
        self.current_user = None
        
        self.show_login_screen()
    
    def create_tables(self):
        """Izveido datu bāzes tabulas"""
        self.c.execute('''CREATE TABLE IF NOT EXISTS lietotaji
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     lietotajvards TEXT UNIQUE,
                     parole TEXT,
                     ir_vaditajs BOOLEAN,
                     vards TEXT,
                     telefons TEXT)''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS braucieni
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     vaditaja_id INTEGER,
                     datums TEXT,
                     laiks TEXT,
                     no_kurienes TEXT,
                     uz_kurieni TEXT,
                     cena REAL,
                     vietas INTEGER,
                     FOREIGN KEY(vaditaja_id) REFERENCES lietotaji(id))''')
        
        self.conn.commit()
    
    def clear_window(self):
        """Notīra visus loga elementus"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Rāda pieslēgšanās/logina ekrānu"""
        self.clear_window()
        
        # Ievades lauki
        ttk.Label(self.root, text="Lietotājvārds:").pack(pady=5)
        self.username_entry = ttk.Entry(self.root)
        self.username_entry.pack(pady=5)
        
        ttk.Label(self.root, text="Parole:").pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        # Pogas
        ttk.Button(self.root, text="Pieslēgties", command=self.login).pack(pady=10)
        ttk.Button(self.root, text="Reģistrēties", command=self.show_register_screen).pack(pady=5)
    
    def show_register_screen(self):
        """Rāda reģistrācijas ekrānu"""
        self.clear_window()
        
        # Ievades lauki
        ttk.Label(self.root, text="Reģistrācija", font=('Arial', 14)).pack(pady=10)
        
        fields = [
            ("Lietotājvārds", "username"),
            ("Parole", "password"),
            ("Vārds", "name"),
            ("Telefons", "phone")
        ]
        
        self.entries = {}
        for text, field in fields:
            ttk.Label(self.root, text=text+":").pack(pady=2)
            entry = ttk.Entry(self.root)
            if field == "password":
                entry.config(show="*")
            entry.pack(pady=2)
            self.entries[field] = entry
        
        # Lietotāja tips
        self.user_type = tk.IntVar()
        ttk.Radiobutton(self.root, text="Vadītājs", variable=self.user_type, value=1).pack()
        ttk.Radiobutton(self.root, text="Pasažieris", variable=self.user_type, value=0).pack()
        
        # Pogas
        ttk.Button(self.root, text="Reģistrēties", command=self.register).pack(pady=10)
        ttk.Button(self.root, text="Atpakaļ", command=self.show_login_screen).pack(pady=5)
    
    def show_main_menu(self):
        """Rāda galveno izvēlni pēc pieslēgšanās"""
        self.clear_window()
        
        if self.current_user['ir_vaditajs']:
            ttk.Label(self.root, text=f"Sveiks, vadītāj {self.current_user['vards']}!").pack(pady=10)
            
            ttk.Button(self.root, text="Pievienot braucienu", 
                      command=self.show_add_ride_screen).pack(pady=5)
        else:
            ttk.Label(self.root, text=f"Sveiks, pasažier {self.current_user['vards']}!").pack(pady=10)
        
        ttk.Button(self.root, text="Apskatīt braucienus", 
                  command=self.show_rides).pack(pady=5)
        ttk.Button(self.root, text="Izrakstīties", 
                  command=self.logout).pack(pady=10)
    
    def show_add_ride_screen(self):
        """Rāda brauciena pievienošanas ekrānu (tikai vadītājiem)"""
        self.clear_window()
        
        ttk.Label(self.root, text="Pievienot jaunu braucienu", font=('Arial', 14)).pack(pady=10)
        
        fields = [
            ("Datums (YYYY-MM-DD)", "date"),
            ("Laiks (HH:MM)", "time"),
            ("No kurienes", "from"),
            ("Uz kurieni", "to"),
            ("Cena (EUR)", "price"),
            ("Pieejamās vietas", "seats")
        ]
        
        self.ride_entries = {}
        for text, field in fields:
            ttk.Label(self.root, text=text+":").pack(pady=2)
            entry = ttk.Entry(self.root)
            entry.pack(pady=2)
            self.ride_entries[field] = entry
        
        ttk.Button(self.root, text="Saglabāt", command=self.save_ride).pack(pady=10)
        ttk.Button(self.root, text="Atcelt", command=self.show_main_menu).pack(pady=5)
    
    def show_rides(self):
        """Rāda visus pieejamos braucienus"""
        self.clear_window()
        
        self.c.execute('''SELECT b.id, l.vards, b.datums, b.laiks, b.no_kurienes, 
                       b.uz_kurieni, b.cena, b.vietas 
                       FROM braucieni b JOIN lietotaji l ON b.vaditaja_id = l.id''')
        rides = self.c.fetchall()
        
        if not rides:
            ttk.Label(self.root, text="Nav pieejamu braucienu.").pack()
            ttk.Button(self.root, text="Atpakaļ", command=self.show_main_menu).pack(pady=10)
            return
        
        # Izveido Treeview (tabulu)
        tree = ttk.Treeview(self.root, columns=('ID', 'Vadītājs', 'Datums', 'Laiks', 'No', 'Uz', 'Cena', 'Vietas'), show='headings')
        
        # Kolonnu galvenes
        for col in tree['columns']:
            tree.heading(col, text=col)
        
        # Pievieno datus
        for ride in rides:
            tree.insert('', 'end', values=ride)
        
        tree.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Ja lietotājs ir pasažieris, parāda rezervācijas pogu
        if not self.current_user['ir_vaditajs']:
            ttk.Button(self.root, text="Rezervēt braucienu", 
                      command=lambda: self.book_ride(tree)).pack(pady=10)
        
        ttk.Button(self.root, text="Atpakaļ", command=self.show_main_menu).pack(pady=5)
    
    def book_ride(self, tree):
        """Rezervē braucienu (pasažierim)"""
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Brīdinājums", "Lūdzu, atlasiet braucienu!")
            return
        
        ride_id = tree.item(selected_item)['values'][0]
        messagebox.showinfo("Rezervācija", f"Brauciens ID {ride_id} rezervēts!")
        self.show_main_menu()
    
    def login(self):
        """Pieslēgšanās funkcionalitāte"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        self.c.execute("SELECT id, vards, ir_vaditajs FROM lietotaji WHERE lietotajvards=? AND parole=?", 
                      (username, password))
        user = self.c.fetchone()
        
        if user:
            self.current_user = {
                'id': user[0],
                'vards': user[1],
                'ir_vaditajs': bool(user[2])
            }
            self.show_main_menu()
        else:
            messagebox.showerror("Kļūda", "Nepareizs lietotājvārds vai parole!")
    
    def register(self):
        """Reģistrācijas funkcionalitāte"""
        username = self.entries['username'].get()
        password = self.entries['password'].get()
        name = self.entries['name'].get()
        phone = self.entries['phone'].get()
        is_driver = bool(self.user_type.get())
        
        try:
            self.c.execute("INSERT INTO lietotaji (lietotajvards, parole, ir_vaditajs, vards, telefons) VALUES (?, ?, ?, ?, ?)",
                         (username, password, is_driver, name, phone))
            self.conn.commit()
            messagebox.showinfo("Veiksmīgi", "Reģistrācija veiksmīga! Lūdzu pieslēdzieties.")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Kļūda", "Lietotājvārds jau eksistē!")
    
    def save_ride(self):
        """Saglabā jaunu braucienu (vadītājam)"""
        date = self.ride_entries['date'].get()
        time = self.ride_entries['time'].get()
        from_loc = self.ride_entries['from'].get()
        to_loc = self.ride_entries['to'].get()
        price = self.ride_entries['price'].get()
        seats = self.ride_entries['seats'].get()
        
        try:
            self.c.execute("INSERT INTO braucieni (vaditaja_id, datums, laiks, no_kurienes, uz_kurieni, cena, vietas) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.current_user['id'], date, time, from_loc, to_loc, float(price), int(seats)))
            self.conn.commit()
            messagebox.showinfo("Veiksmīgi", "Brauciens pievienots!")
            self.show_main_menu()
        except ValueError:
            messagebox.showerror("Kļūda", "Nepareizi ievadīti dati!")
    
    def logout(self):
        """Izrakstīšanās"""
        self.current_user = None
        self.show_login_screen()
    
    def __del__(self):
        """Aizver datu bāzes savienojumu"""
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = CarpoolApp(root)
    root.mainloop()