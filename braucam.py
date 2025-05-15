import tkinter as tk  # Importē Tkinter bāzes moduli GUI izveidei
from tkinter import ttk, messagebox  # Importē uzlabotos logrīkus un ziņojumu logus
import requests  # Modulis HTTP pieprasījumu sūtīšanai uz API

# API bāzes adrese (MockAPI serviss testiem)
API_BAZES_ADRESE = "https://67f6d3f542d6c71cca6368d7.mockapi.io/maucam"

# Galvenā lietotnes klase
class BraukšanasLietotne:
    def __init__(self, logs):
        self.logs = logs
        self.logs.title("Maucam")
        self.logs.geometry("800x600")
        self.aktivais_lietotajs = None
        self.paradit_pieslegsanas_ekranu()
        self.logs.iconbitmap("logo.ico")

    def notirit_logu(self):
        for elements in self.logs.winfo_children():
            elements.destroy()

    def paradit_pieslegsanas_ekranu(self):
        self.notirit_logu()

        ttk.Label(self.logs, text="Lietotājvārds:").pack(pady=5)
        self.lietotajvarda_ievade = ttk.Entry(self.logs)
        self.lietotajvarda_ievade.pack(pady=5)

        ttk.Label(self.logs, text="Parole:").pack(pady=5)
        self.paroles_ievade = ttk.Entry(self.logs, show="*")
        self.paroles_ievade.pack(pady=5)

        ttk.Button(self.logs, text="Pieslēgties", command=self.pieslegties).pack(pady=10)
        ttk.Button(self.logs, text="Reģistrēties", command=self.paradit_registracijas_ekranu).pack(pady=5)

    def paradit_registracijas_ekranu(self):
        self.notirit_logu()

        ttk.Label(self.logs, text="Reģistrācija", font=('Arial', 14)).pack(pady=10)

        lauki = [
            ("Lietotājvārds", "lietotajvards"),
            ("Parole", "parole"),
            ("Vārds", "vards"),
            ("Telefons", "telefons")
        ]

        self.ievades_lauki = {}
        for teksts, lauka_nosaukums in lauki:
            ttk.Label(self.logs, text=teksts + ":").pack(pady=2)
            ievade = ttk.Entry(self.logs)
            if lauka_nosaukums == "parole":
                ievade.config(show="*")
            ievade.pack(pady=2)
            self.ievades_lauki[lauka_nosaukums] = ievade

        self.lietotaja_tips = tk.IntVar()
        ttk.Radiobutton(self.logs, text="Vadītājs", variable=self.lietotaja_tips, value=1).pack()
        ttk.Radiobutton(self.logs, text="Pasažieris", variable=self.lietotaja_tips, value=0).pack()

        ttk.Button(self.logs, text="Reģistrēties", command=self.registreties).pack(pady=10)
        ttk.Button(self.logs, text="Atpakaļ", command=self.paradit_pieslegsanas_ekranu).pack(pady=5)

    def paradit_galveno_izvelni(self):
        self.notirit_logu()

        if self.aktivais_lietotajs['ir_vaditajs']:
            ttk.Label(self.logs, text=f"Sveiks, vadītāj {self.aktivais_lietotajs['vards']}!").pack(pady=10)
            ttk.Button(self.logs, text="Pievienot braucienu", command=self.paradit_pievienosanas_ekranu).pack(pady=5)
        else:
            ttk.Label(self.logs, text=f"Sveiks, pasažier {self.aktivais_lietotajs['vards']}!").pack(pady=10)

        ttk.Button(self.logs, text="Apskatīt braucienus", command=self.paradit_braucienus).pack(pady=5)
        ttk.Button(self.logs, text="Izrakstīties", command=self.izrakstities).pack(pady=10)

    def paradit_pievienosanas_ekranu(self):
        self.notirit_logu()

        ttk.Label(self.logs, text="Pievienot jaunu braucienu", font=('Arial', 14)).pack(pady=10)

        lauki = [
            ("Datums (YYYY-MM-DD)", "datums"),
            ("Laiks (HH:MM)", "laiks"),
            ("No kurienes", "no_kurienes"),
            ("Uz kurieni", "uz_kurieni"),
            ("Cena (EUR)", "cena"),
            ("Pieejamās vietas", "vietas")
        ]

        self.brauciena_ievade = {}
        for teksts, atsl in lauki:
            ttk.Label(self.logs, text=teksts + ":").pack(pady=2)
            ievade = ttk.Entry(self.logs)
            ievade.pack(pady=2)
            self.brauciena_ievade[atsl] = ievade

        ttk.Button(self.logs, text="Saglabāt", command=self.saglabat_braucienu).pack(pady=10)
        ttk.Button(self.logs, text="Atcelt", command=self.paradit_galveno_izvelni).pack(pady=5)

    def paradit_braucienus(self):
        self.notirit_logu()
        try:
            atbilde = requests.get(f"{API_BAZES_ADRESE}/Braucieni")
            braucieni = atbilde.json()
        except Exception as kluda:
            messagebox.showerror("Kļūda", str(kluda))
            return

        if not braucieni:
            ttk.Label(self.logs, text="Nav pieejamu braucienu.").pack()
            ttk.Button(self.logs, text="Atpakaļ", command=self.paradit_galveno_izvelni).pack(pady=10)
            return

        tabula = ttk.Treeview(self.logs, columns=('ID', 'Vadītājs', 'Datums', 'Laiks', 'No', 'Uz', 'Cena', 'Vietas'), show='headings')
        for kol in tabula['columns']:
            tabula.heading(kol, text=kol)

        for brauciens in braucieni:
            tabula.insert('', 'end', values=(brauciens['id'], brauciens.get('vaditaja_id'), brauciens['datums'], brauciens['laiks'], brauciens['no_kurienes'], brauciens['uz_kurieni'], brauciens['cena'], brauciens['vietas']))

        tabula.pack(expand=True, fill='both', padx=10, pady=10)

        if not self.aktivais_lietotajs['ir_vaditajs']:
            ttk.Button(self.logs, text="Rezervēt braucienu", command=lambda: self.rezervet_braucienu(tabula)).pack(pady=10)

        ttk.Button(self.logs, text="Atpakaļ", command=self.paradit_galveno_izvelni).pack(pady=5)

    def rezervet_braucienu(self, tabula):
        atlase = tabula.focus()
        if not atlase:
            messagebox.showwarning("Brīdinājums", "Lūdzu, atlasiet braucienu!")
            return

        vertibas = tabula.item(atlase)['values']
        brauciena_id = vertibas[0]
        atlikusas_vietas = int(vertibas[7])

        if atlikusas_vietas <= 0:
            messagebox.showerror("Kļūda", "Šajā braucienā vairs nav brīvu vietu!")
            return

        jaunas_vietas = atlikusas_vietas - 1

        try:
            atbilde = requests.put(
                f"{API_BAZES_ADRESE}/Braucieni/{brauciena_id}",
                json={"vietas": jaunas_vietas}
            )
            if atbilde.status_code == 200:
                messagebox.showinfo("Rezervācija", f"Brauciens ID {brauciena_id} rezervēts!\nAtlikušas vietas: {jaunas_vietas}")
            else:
                messagebox.showerror("Kļūda", f"Rezervācija neizdevās! Statuss: {atbilde.status_code}")
        except Exception as kluda:
            messagebox.showerror("Kļūda", f"Radās kļūda: {str(kluda)}")

        self.paradit_galveno_izvelni()

    def pieslegties(self):
        lietotajvards = self.lietotajvarda_ievade.get()
        parole = self.paroles_ievade.get()
        try:
            atbilde = requests.get(f"{API_BAZES_ADRESE}/lietotaja")
            lietotaji = atbilde.json()
            for lietotajs in lietotaji:
                if lietotajs['lietotajvards'] == lietotajvards and lietotajs['parole'] == parole:
                    self.aktivais_lietotajs = lietotajs
                    self.paradit_galveno_izvelni()
                    return
            messagebox.showerror("Kļūda", "Nepareizs lietotājvārds vai parole!")
        except Exception as kluda:
            messagebox.showerror("Kļūda", str(kluda))

    def registreties(self):
        lietotajvards = self.ievades_lauki['lietotajvards'].get()
        parole = self.ievades_lauki['parole'].get()
        vards = self.ievades_lauki['vards'].get()
        telefons = self.ievades_lauki['telefons'].get()
        ir_vaditajs = bool(self.lietotaja_tips.get())

        if not lietotajvards or not parole or not vards or not telefons:
            messagebox.showerror("Kļūda", "Visi lauki jāaizpilda!")
            return

        dati = {
            "lietotajvards": lietotajvards,
            "parole": parole,
            "vards": vards,
            "telefons": telefons,
            "ir_vaditajs": ir_vaditajs
        }

        try:
            atbilde = requests.post(f"{API_BAZES_ADRESE}/lietotaja", json=dati)
            if atbilde.status_code == 201:
                messagebox.showinfo("Veiksmīgi", "Reģistrācija veiksmīga! Lūdzu pieslēdzieties.")
                self.paradit_pieslegsanas_ekranu()
            else:
                messagebox.showerror("Kļūda", f"Reģistrācija neizdevās! Statuss: {atbilde.status_code}, Atbilde: {atbilde.text}")
        except Exception as kluda:
            messagebox.showerror("Kļūda", f"Radās kļūda: {str(kluda)}")

    def saglabat_braucienu(self):
        datums = self.brauciena_ievade['datums'].get()
        laiks = self.brauciena_ievade['laiks'].get()
        no_kurienes = self.brauciena_ievade['no_kurienes'].get()
        uz_kurieni = self.brauciena_ievade['uz_kurieni'].get()
        cena = self.brauciena_ievade['cena'].get()
        vietas = self.brauciena_ievade['vietas'].get()

        brauciens = {
            "vaditaja_id": self.aktivais_lietotajs['id'],
            "datums": datums,
            "laiks": laiks,
            "no_kurienes": no_kurienes,
            "uz_kurieni": uz_kurieni,
            "cena": float(cena),
            "vietas": int(vietas)
        }

        try:
            atbilde = requests.post(f"{API_BAZES_ADRESE}/Braucieni", json=brauciens)
            if atbilde.status_code == 201:
                messagebox.showinfo("Veiksmīgi", "Brauciens pievienots!")
                self.paradit_galveno_izvelni()
            else:
                messagebox.showerror("Kļūda", "Neizdevās pievienot braucienu!")
        except Exception as kluda:
            messagebox.showerror("Kļūda", str(kluda))

    def izrakstities(self):
        self.aktivais_lietotajs = None
        self.paradit_pieslegsanas_ekranu()

if __name__ == "__main__":
    logs = tk.Tk()
    aplikacija = BraukšanasLietotne(logs)
    logs.mainloop()


