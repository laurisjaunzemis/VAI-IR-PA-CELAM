import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_BASE_URL = "https://67f6d3f542d6c71cca6368d7.mockapi.io/maucam"

class CarpoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Koplietošanas App")
        self.root.geometry("800x600")
        self.current_user = None
        self.show_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_window()

        ttk.Label(self.root, text="Lietotājvārds:").pack(pady=5)
        self.username_entry = ttk.Entry(self.root)
        self.username_entry.pack(pady=5)

        ttk.Label(self.root, text="Parole:").pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self.root, text="Pieslēgties", command=self.login).pack(pady=10)
        ttk.Button(self.root, text="Reģistrēties", command=self.show_register_screen).pack(pady=5)

    def show_register_screen(self):
        self.clear_window()

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

        self.user_type = tk.IntVar()
        ttk.Radiobutton(self.root, text="Vadītājs", variable=self.user_type, value=1).pack()
        ttk.Radiobutton(self.root, text="Pasažieris", variable=self.user_type, value=0).pack()

        ttk.Button(self.root, text="Reģistrēties", command=self.register).pack(pady=10)
        ttk.Button(self.root, text="Atpakaļ", command=self.show_login_screen).pack(pady=5)

    def show_main_menu(self):
        self.clear_window()

        if self.current_user['ir_vaditajs']:
            ttk.Label(self.root, text=f"Sveiks, vadītāj {self.current_user['vards']}!").pack(pady=10)
            ttk.Button(self.root, text="Pievienot braucienu", command=self.show_add_ride_screen).pack(pady=5)
        else:
            ttk.Label(self.root, text=f"Sveiks, pasažier {self.current_user['vards']}!").pack(pady=10)

        ttk.Button(self.root, text="Apskatīt braucienus", command=self.show_rides).pack(pady=5)
        ttk.Button(self.root, text="Izrakstīties", command=self.logout).pack(pady=10)

    def show_add_ride_screen(self):
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
        self.clear_window()
        try:
            response = requests.get(f"{API_BASE_URL}/braucieni")
            rides = response.json()
        except Exception as e:
            messagebox.showerror("Kļūda", str(e))
            return

        if not rides:
            ttk.Label(self.root, text="Nav pieejamu braucienu.").pack()
            ttk.Button(self.root, text="Atpakaļ", command=self.show_main_menu).pack(pady=10)
            return

        tree = ttk.Treeview(self.root, columns=('ID', 'Vadītājs', 'Datums', 'Laiks', 'No', 'Uz', 'Cena', 'Vietas'), show='headings')
        for col in tree['columns']:
            tree.heading(col, text=col)

        for ride in rides:
            tree.insert('', 'end', values=(ride['id'], ride.get('vaditaja_id'), ride['datums'], ride['laiks'], ride['no_kurienes'], ride['uz_kurieni'], ride['cena'], ride['vietas']))

        tree.pack(expand=True, fill='both', padx=10, pady=10)

        if not self.current_user['ir_vaditajs']:
            ttk.Button(self.root, text="Rezervēt braucienu", command=lambda: self.book_ride(tree)).pack(pady=10)

        ttk.Button(self.root, text="Atpakaļ", command=self.show_main_menu).pack(pady=5)

    def book_ride(self, tree):
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Brīdinājums", "Lūdzu, atlasiet braucienu!")
            return

        ride_id = tree.item(selected_item)['values'][0]
        messagebox.showinfo("Rezervācija", f"Brauciens ID {ride_id} rezervēts!")
        self.show_main_menu()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            response = requests.get(f"{API_BASE_URL}/lietotaja")
            users = response.json()
            for user in users:
                if user['lietotajvards'] == username and user['parole'] == password:
                    self.current_user = user
                    self.show_main_menu()
                    return
            messagebox.showerror("Kļūda", "Nepareizs lietotājvārds vai parole!")
        except Exception as e:
            messagebox.showerror("Kļūda", str(e))

    def register(self):
        username = self.entries['username'].get()
        password = self.entries['password'].get()
        name = self.entries['name'].get()
        phone = self.entries['phone'].get()
        is_driver = bool(self.user_type.get())

        # Pārbauda, vai visi lauki ir aizpildīti
        if not username or not password or not name or not phone:
            messagebox.showerror("Kļūda", "Visi lauki jāaizpilda!")
            return

        # Sagatavo lietotāja datus
        user_data = {
            "lietotajvards": username,
            "parole": password,
            "vards": name,
            "telefons": phone,
            "ir_vaditajs": is_driver
        }

        # Pārbauda, ko tieši mēs sūtām
        print("Sūta uz serveri:", user_data)

        try:
            response = requests.post(f"{API_BASE_URL}/lietotaja", json=user_data)

            # Izdrukā servera atbildi
            print("Servera atbilde:", response.status_code, response.text)

            # Pārbauda atbildes statusu
            if response.status_code == 201:
                messagebox.showinfo("Veiksmīgi", "Reģistrācija veiksmīga! Lūdzu pieslēdzieties.")
                self.show_login_screen()
            else:
                # Parāda detalizētu kļūdas informāciju
                messagebox.showerror("Kļūda", f"Reģistrācija neizdevās! Statuss: {response.status_code}, Atbilde: {response.text}")
        except Exception as e:
            messagebox.showerror("Kļūda", f"Radās kļūda: {str(e)}")

    def save_ride(self):
        date = self.ride_entries['date'].get()
        time = self.ride_entries['time'].get()
        from_loc = self.ride_entries['from'].get()
        to_loc = self.ride_entries['to'].get()
        price = self.ride_entries['price'].get()
        seats = self.ride_entries['seats'].get()

        ride_data = {
            "vaditaja_id": self.current_user['id'],
            "datums": date,
            "laiks": time,
            "no_kurienes": from_loc,
            "uz_kurieni": to_loc,
            "cena": float(price),
            "vietas": int(seats)
        }

        try:
            response = requests.post(f"{API_BASE_URL}/braucieni", json=ride_data)
            if response.status_code == 201:
                messagebox.showinfo("Veiksmīgi", "Brauciens pievienots!")
                self.show_main_menu()
            else:
                messagebox.showerror("Kļūda", "Neizdevās pievienot braucienu!")
        except Exception as e:
            messagebox.showerror("Kļūda", str(e))

    def logout(self):
        self.current_user = None
        self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = CarpoolApp(root)
    root.mainloop()