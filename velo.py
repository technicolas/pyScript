#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime
import traceback
import configparser
import tkinter as tk
from tkinter import messagebox, filedialog
from pyexcel_ods3 import get_data, save_data

# -----------------------
# Bibliothèque à installer:
# -------------------------
# python -m pip install pyexcel-ods3


# -----------------------
# Configuration
# -----------------------
CONFIG_FILE = "velo.conf"
CONFIG_SECTION = "settings"
CONFIG_KEY_ODS = "ods_path"
DEFAULT_ODS = "parcours.ods"

BASE_HEADERS = ["Date", "Description", "AVS", "MXS", "CAL", "ODO", "TM", "DST", "Dénivelé positif"]
ALL_HEADERS = BASE_HEADERS + ["TM_seconds"]

# -----------------------
# Gestion du fichier de configuration
# -----------------------
def load_config():
    cfg = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        try:
            cfg.read(CONFIG_FILE, encoding="utf-8")
        except Exception:
            # si lecture impossible, on retourne config vide
            cfg = configparser.ConfigParser()
    if CONFIG_SECTION not in cfg:
        cfg[CONFIG_SECTION] = {}
    ods_path = cfg[CONFIG_SECTION].get(CONFIG_KEY_ODS, "").strip()
    if ods_path == "":
        ods_path = DEFAULT_ODS
        cfg[CONFIG_SECTION][CONFIG_KEY_ODS] = ods_path
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                cfg.write(f)
        except Exception:
            pass
    return cfg, ods_path

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            cfg.write(f)
    except Exception as e:
        # ne pas planter l'application si l'écriture échoue
        print("Impossible d'enregistrer la configuration:", e)

# -----------------------
# pyexcel-ods3 utilitaires
# -----------------------
def load_sheet_data(path):
    if not os.path.exists(path):
        return None, []
    data = get_data(path)
    if not data:
        return None, []
    sheet_name = next(iter(data.keys()))
    rows = data[sheet_name]
    return sheet_name, rows

def save_sheet_data(path, sheet_name, rows):
    data = {sheet_name: rows}
    save_data(path, data)

def ensure_file_and_headers(path, sheet_name=None):
    if not os.path.exists(path):
        sheet = sheet_name if sheet_name else "Feuille1"
        rows = [ALL_HEADERS]
        save_sheet_data(path, sheet, rows)
        return sheet, rows

    sname, rows = load_sheet_data(path)
    if sname is None:
        sheet = sheet_name if sheet_name else "Feuille1"
        rows = [ALL_HEADERS]
        save_sheet_data(path, sheet, rows)
        return sheet, rows

    if len(rows) == 0:
        rows = [ALL_HEADERS]
        save_sheet_data(path, sname, rows)
        return sname, rows

    header = rows[0]
    if len(header) < len(ALL_HEADERS):
        header = header + [""] * (len(ALL_HEADERS) - len(header))
    for i, h in enumerate(ALL_HEADERS):
        if i >= len(header) or header[i] is None or str(header[i]).strip() == "":
            if i < len(header):
                header[i] = h
            else:
                header.append(h)
    rows[0] = header

    for ri in range(1, len(rows)):
        r = rows[ri]
        if len(r) < len(ALL_HEADERS):
            rows[ri] = r + [""] * (len(ALL_HEADERS) - len(r))

    save_sheet_data(path, sname, rows)
    return sname, rows

# -----------------------
# Conversion TM -> secondes
# -----------------------
def parse_tm_to_seconds(tm_str):
    s = tm_str.strip()
    if s == "":
        return ""
    s = s.replace(",", ":")
    parts = [p for p in s.split(":") if p != ""]
    try:
        parts = [int(p) for p in parts]
    except Exception:
        return ""
    if len(parts) == 3:
        h, m, sec = parts
    elif len(parts) == 2:
        h = 0
        m, sec = parts
    elif len(parts) == 1:
        h = 0
        m = 0
        sec = parts[0]
    else:
        return ""
    if m < 0 or sec < 0 or h < 0:
        return ""
    return h * 3600 + m * 60 + sec

def norm_num_field(s):
    s = s.strip()
    if s == "":
        return ""
    s2 = s.replace(",", ".")
    try:
        return float(s2)
    except Exception:
        return s

def append_row_with_tm_seconds(path, row_values, sheet_name=None):
    if os.path.exists(path):
        try:
            with open(path, "a"):
                pass
        except PermissionError:
            raise PermissionError(f"Le fichier {path} semble ouvert par une autre application. Fermez-le puis réessayez.")
    sname, rows = ensure_file_and_headers(path, sheet_name)
    if len(row_values) < len(BASE_HEADERS):
        row_values = row_values + [""] * (len(BASE_HEADERS) - len(row_values))
    try:
        tm_index = BASE_HEADERS.index("TM")
    except ValueError:
        tm_index = 6
    tm_val = "" if tm_index >= len(row_values) else ("" if row_values[tm_index] is None else str(row_values[tm_index]))
    tm_seconds = parse_tm_to_seconds(str(tm_val))
    final_row = [v for v in row_values[:len(BASE_HEADERS)]]
    final_row.append(tm_seconds)
    if len(final_row) < len(ALL_HEADERS):
        final_row += [""] * (len(ALL_HEADERS) - len(final_row))
    rows.append(final_row)
    save_sheet_data(path, sname, rows)
    return len(rows)

# -----------------------
# Placeholders helpers
# -----------------------
PLACEHOLDER_COLOR = "#888888"
TEXT_COLOR = "#000000"

def add_placeholder(entry, placeholder_text):
    def on_focus_in(event, e=entry, ph=placeholder_text):
        cur = e.get()
        if cur == ph:
            e.delete(0, "end")
            e.config(fg=TEXT_COLOR)
    def on_focus_out(event, e=entry, ph=placeholder_text):
        cur = e.get()
        if cur.strip() == "":
            e.delete(0, "end")
            e.insert(0, ph)
            e.config(fg=PLACEHOLDER_COLOR)
            e.icursor(0)
    entry.insert(0, placeholder_text)
    entry.config(fg=PLACEHOLDER_COLOR)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    entry.bind("<Button-1>", lambda ev, e=entry: e.icursor(0))

def get_entry_value(entry, placeholder_text):
    v = entry.get()
    if v == placeholder_text:
        return ""
    return v.strip()

# -----------------------
# Interface Tkinter
# -----------------------
class App:
    def __init__(self, root, cfg, ods_path):
        self.root = root
        self.cfg = cfg
        self.ods_path = ods_path
        self.sheet_name = None
        root.title(f"Saisie parcours → {os.path.basename(self.ods_path)}")
        self.create_menu()
        labels = [
            ("Date (YYYY-MM-DD) — laisser vide = aujourd'hui", "date", datetime.date.today().isoformat()),
            ("Description", "desc", "Ex: Tour du Mont..."),
            ("AVS", "avs", "24,1"),
            ("MXS", "mxs", "47,1"),
            ("CAL", "cal", "680,5"),
            ("ODO", "odo", "165,7"),
            ("TM (HH:MM:SS)", "tm", "1:28:32"),
            ("DST", "dst", "35,67"),
            ("Dénivelé positif (m)", "deniv", "450"),
        ]
        self.entries = {}
        for i, (lab, key, example) in enumerate(labels):
            tk.Label(root, text=lab).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            e = tk.Entry(root, width=36)
            e.grid(row=i, column=1, padx=6, pady=4)
            self.entries[key] = (e, example)
            add_placeholder(e, example)

        btn_frame = tk.Frame(root)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)
        save_btn = tk.Button(btn_frame, text="Enregistrer", width=14, command=self.on_save,
                             bg="#28a745", fg="white", activebackground="#218838", activeforeground="white")
        save_btn.pack(side="left", padx=6)
        preview_btn = tk.Button(btn_frame, text="Prévisualiser dernières lignes", width=26, command=self.preview_last_lines)
        preview_btn.pack(side="left", padx=6)
        quit_btn = tk.Button(btn_frame, text="Quitter", width=10, command=root.quit,
                             bg="#dc3545", fg="white", activebackground="#c82333", activeforeground="white")
        quit_btn.pack(side="left", padx=6)

    # Menu
    def create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Ouvrir un fichier .ods...", command=self.menu_open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="À propos / Informations légales", command=self.show_about)
        menubar.add_cascade(label="Aide", menu=helpmenu)

        self.root.config(menu=menubar)

    def menu_open_file(self):
        filetypes = [("Fichiers ODS", "*.ods"), ("Tous les fichiers", "*.*")]
        initialdir = os.path.expanduser("~")
        chosen = filedialog.askopenfilename(title="Choisir un fichier .ods", initialdir=initialdir, filetypes=filetypes)
        if chosen:
            # mettre à jour le chemin et sauvegarder dans la config
            self.ods_path = chosen
            self.cfg[CONFIG_SECTION][CONFIG_KEY_ODS] = self.ods_path
            save_config(self.cfg)
            self.root.title(f"Saisie parcours → {os.path.basename(self.ods_path)}")
            messagebox.showinfo("Fichier sélectionné", f"Le fichier {self.ods_path} sera utilisé et enregistré dans {CONFIG_FILE}.")

    def show_about(self):
        legal_text = (
            "Saisie parcours - version 1.0\n\n"
            "Auteur: Nicolas (utilisateur)\n"
            "Licence: usage personnel\n\n"
            "Ce programme enregistre des données dans un fichier LibreOffice Calc (.ods).\n"
            "Aucune garantie n'est fournie. Fermez LibreOffice si le fichier est ouvert avant d'enregistrer."
        )
        messagebox.showinfo("À propos / Informations légales", legal_text)

    def parse_date(self, s):
        s = s.strip()
        if s == "":
            return datetime.date.today().isoformat()
        try:
            d = datetime.date.fromisoformat(s)
            return d.isoformat()
        except Exception:
            raise ValueError("Date invalide. Utilisez le format YYYY-MM-DD.")

    def on_save(self):
        try:
            date_entry, date_ph = self.entries["date"]
            date_raw = get_entry_value(date_entry, date_ph)
            date_str = self.parse_date(date_raw)
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        def val(key):
            e, ph = self.entries[key]
            return get_entry_value(e, ph)

        desc = val("desc")
        avs_v = norm_num_field(val("avs"))
        mxs_v = norm_num_field(val("mxs"))
        cal_v = norm_num_field(val("cal"))
        odo_v = norm_num_field(val("odo"))
        tm = val("tm")
        dst_v = norm_num_field(val("dst"))
        deniv_v = norm_num_field(val("deniv"))

        row = [date_str, desc, avs_v, mxs_v, cal_v, odo_v, tm, dst_v, deniv_v]

        try:
            total_lines = append_row_with_tm_seconds(self.ods_path, row, self.sheet_name)
            messagebox.showinfo("Succès", f"Données enregistrées dans '{self.ods_path}' (ligne {total_lines})")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Impossible d'enregistrer", f"{e}")

    def preview_last_lines(self, n=8):
        if not os.path.exists(self.ods_path):
            messagebox.showinfo("Aucune donnée", f"Le fichier '{self.ods_path}' n'existe pas encore.")
            return
        try:
            sname, rows = load_sheet_data(self.ods_path)
            if sname is None:
                messagebox.showinfo("Aucune feuille", "Le fichier ne contient aucune feuille lisible.")
                return
            rows_to_show = rows[-n:] if len(rows) > 0 else []
            win = tk.Toplevel(self.root)
            win.title("Prévisualisation dernières lignes")
            txt = tk.Text(win, width=120, height=20)
            txt.pack(padx=6, pady=6)
            for r in rows_to_show:
                line = "\t".join("" if c is None else str(c) for c in r)
                txt.insert("end", line + "\n")
            txt.config(state="disabled")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Erreur", f"Impossible de lire '{self.ods_path}': {e}")

# -----------------------
# Lancement
# -----------------------
def main():
    cfg, ods_path = load_config()
    root = tk.Tk()
    app = App(root, cfg, ods_path)
    root.resizable(False, False)
    root.mainloop()

if __name__ == "__main__":
    main()
