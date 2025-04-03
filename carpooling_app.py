import tkinter as tk
from tkinter import messagebox
import sqlite3
from database import get_db_connection, create_tables

class Carpool:
    def __init__(self):
        # Initialize database tables
        create_tables()

    def add_ride(self, driver, phone, start_location, end_location, time, available_seats):
        """Add a new ride to the database"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO rides (driver, phone, start_location, end_location, time, available_seats)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (driver, phone, start_location, end_location, time, available_seats))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def join_ride(self, user, start_location, end_location, time):
        """Join an existing ride by updating available seats"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Find rides matching the criteria
                cursor.execute('''
                SELECT id, available_seats FROM rides 
                WHERE start_location = ? AND end_location = ? AND time = ? AND available_seats > 0
                ''', (start_location, end_location, time))
                
                ride = cursor.fetchone()
                
                if ride:
                    ride_id = ride['id']
                    current_seats = ride['available_seats']
                    
                    # Update available seats
                    cursor.execute('''
                    UPDATE rides SET available_seats = ? WHERE id = ?
                    ''', (current_seats - 1, ride_id))
                    
                    # Add passenger record (optional, for future tracking)
                    cursor.execute('''
                    INSERT INTO passengers (ride_id, passenger_name)
                    VALUES (?, ?)
                    ''', (ride_id, user))
                    
                    conn.commit()
                    return f"{user} pievienojās braucienam no {start_location} uz {end_location} plkst. {time}."
                else:
                    cursor.execute('''
                    SELECT id FROM rides 
                    WHERE start_location = ? AND end_location = ? AND time = ? AND available_seats = 0
                    ''', (start_location, end_location, time))
                    
                    if cursor.fetchone():
                        return "Nav pieejamas vietas šajā braucienā."
                    return "Nav atrasts atbilstošs brauciens."
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return "Kļūda pievienojoties braucienam. Lūdzu mēģiniet vēlreiz."

    def show_rides(self):
        """Retrieve all available rides from the database"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM rides ORDER BY time
                ''')
                
                rides = cursor.fetchall()
                
                if not rides:
                    return "Nav pieejamu braucienu."
                
                rides_info = ""
                for ride in rides:
                    rides_info += f"Vadītājs: {ride['driver']}, Telefons: {ride['phone']}, "
                    rides_info += f"No: {ride['start_location']} Uz: {ride['end_location']} "
                    rides_info += f"Laiks: {ride['time']} Pieejamās vietas: {ride['available_seats']}\n"
                
                return rides_info
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return "Kļūda ielādējot braucienus. Lūdzu mēģiniet vēlreiz."

class CarpoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Carpooling Sistēma")

        self.carpool_system = Carpool()

        # Izveidojam GUI komponentes
        self.create_widgets()

    def create_widgets(self):
        # Pievienot braucienu sadaļa
        self.add_ride_frame = tk.LabelFrame(self.root, text="Pievienot Braucienu", padx=10, pady=10)
        self.add_ride_frame.grid(row=0, column=0, padx=10, pady=10)

        self.driver_label = tk.Label(self.add_ride_frame, text="Vadītāja Vārds:")
        self.driver_label.grid(row=0, column=0)
        self.driver_entry = tk.Entry(self.add_ride_frame)
        self.driver_entry.grid(row=0, column=1)

        self.phone_label = tk.Label(self.add_ride_frame, text="Telefona Numurs:")
        self.phone_label.grid(row=1, column=0)
        self.phone_entry = tk.Entry(self.add_ride_frame)
        self.phone_entry.grid(row=1, column=1)

        self.start_label = tk.Label(self.add_ride_frame, text="Sākuma Vieta:")
        self.start_label.grid(row=2, column=0)
        self.start_entry = tk.Entry(self.add_ride_frame)
        self.start_entry.grid(row=2, column=1)

        self.end_label = tk.Label(self.add_ride_frame, text="Galamērķis:")
        self.end_label.grid(row=3, column=0)
        self.end_entry = tk.Entry(self.add_ride_frame)
        self.end_entry.grid(row=3, column=1)

        self.time_label = tk.Label(self.add_ride_frame, text="Laiks:")
        self.time_label.grid(row=4, column=0)
        self.time_entry = tk.Entry(self.add_ride_frame)
        self.time_entry.grid(row=4, column=1)

        self.seats_label = tk.Label(self.add_ride_frame, text="Pieejamās Vietas:")
        self.seats_label.grid(row=5, column=0)
        self.seats_entry = tk.Entry(self.add_ride_frame)
        self.seats_entry.grid(row=5, column=1)

        self.add_ride_button = tk.Button(self.add_ride_frame, text="Pievienot Braucienu", command=self.add_ride)
        self.add_ride_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Pievienoties braucienam sadaļa
        self.join_ride_frame = tk.LabelFrame(self.root, text="Pievienoties Braucienam", padx=10, pady=10)
        self.join_ride_frame.grid(row=1, column=0, padx=10, pady=10)

        self.user_label = tk.Label(self.join_ride_frame, text="Tavs Vārds:")
        self.user_label.grid(row=0, column=0)
        self.user_entry = tk.Entry(self.join_ride_frame)
        self.user_entry.grid(row=0, column=1)

        self.join_start_label = tk.Label(self.join_ride_frame, text="Sākuma Vieta:")
        self.join_start_label.grid(row=1, column=0)
        self.join_start_entry = tk.Entry(self.join_ride_frame)
        self.join_start_entry.grid(row=1, column=1)

        self.join_end_label = tk.Label(self.join_ride_frame, text="Galamērķis:")
        self.join_end_label.grid(row=2, column=0)
        self.join_end_entry = tk.Entry(self.join_ride_frame)
        self.join_end_entry.grid(row=2, column=1)

        self.join_time_label = tk.Label(self.join_ride_frame, text="Laiks:")
        self.join_time_label.grid(row=3, column=0)
        self.join_time_entry = tk.Entry(self.join_ride_frame)
        self.join_time_entry.grid(row=3, column=1)

        self.join_ride_button = tk.Button(self.join_ride_frame, text="Pievienoties Braucienam", command=self.join_ride)
        self.join_ride_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Rādīt pieejamos braucienus
        self.show_button = tk.Button(self.root, text="Rādīt Pieejamos Braucienus", command=self.show_rides, bg="#4CAF50", fg="white")
        self.show_button.grid(row=2, column=0, padx=10, pady=10)

        self.rides_text = tk.Text(self.root, height=10, width=50)
        self.rides_text.grid(row=3, column=0, padx=10, pady=10)

    def add_ride(self):
        """Handle the add ride button click event"""
        driver = self.driver_entry.get()
        phone = self.phone_entry.get()
        start_location = self.start_entry.get()
        end_location = self.end_entry.get()
        time = self.time_entry.get()
        
        # Validate form data
        if not all([driver, phone, start_location, end_location, time]):
            messagebox.showerror("Trūkst informācijas", "Lūdzu, aizpildiet visus laukus.")
            return
        
        try:
            available_seats = int(self.seats_entry.get())
            if available_seats <= 0:
                raise ValueError("Sēdvietu skaitam jābūt pozitīvam")
        except ValueError:
            messagebox.showerror("Nederīgs ievads", "Lūdzu ievadiet derīgu skaitli pieejamajām vietām.")
            return
        
        # Add ride to database
        success = self.carpool_system.add_ride(driver, phone, start_location, end_location, time, available_seats)
        
        if success:
            messagebox.showinfo("Brauciens pievienots", "Jūsu brauciens ir veiksmīgi pievienots!")
            # Clear form fields
            self.driver_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.start_entry.delete(0, tk.END)
            self.end_entry.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)
            self.seats_entry.delete(0, tk.END)
            # Update ride list
            self.show_rides()
        else:
            messagebox.showerror("Kļūda", "Neizdevās pievienot braucienu. Lūdzu mēģiniet vēlreiz.")

    def join_ride(self):
        """Handle the join ride button click event"""
        user = self.user_entry.get()
        start_location = self.join_start_entry.get()
        end_location = self.join_end_entry.get()
        time = self.join_time_entry.get()
        
        # Validate form data
        if not all([user, start_location, end_location, time]):
            messagebox.showerror("Trūkst informācijas", "Lūdzu, aizpildiet visus laukus.")
            return
        
        result = self.carpool_system.join_ride(user, start_location, end_location, time)
        messagebox.showinfo("Pievienoties Braucienam", result)
        
        # Update ride list
        self.show_rides()
        
        # Clear form fields if successful join
        if "pievienojās" in result:
            self.user_entry.delete(0, tk.END)
            self.join_start_entry.delete(0, tk.END)
            self.join_end_entry.delete(0, tk.END)
            self.join_time_entry.delete(0, tk.END)

    def show_rides(self):
        """Display available rides in the text area"""
        rides_info = self.carpool_system.show_rides()
        self.rides_text.delete(1.0, tk.END)
        self.rides_text.insert(tk.END, rides_info)

def main():
    root = tk.Tk()
    app = CarpoolApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()