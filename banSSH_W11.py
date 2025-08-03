import re
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
from tkinter import Tk, filedialog
import os

def analyser_fichier(fichier_chemin):
    ip_counts = defaultdict(int)
    ip_pattern = r"\d{1,3}(?:\.\d{1,3}){3}"

    with open(fichier_chemin, 'r') as f:
        for line in f:
            ips = re.findall(ip_pattern, line)
            for ip in ips:
                ip_counts[ip] += 1

    return ip_counts

def exporter_excel(ip_counts, chemin_export):
    df = pd.DataFrame(list(ip_counts.items()), columns=['IP', 'Occurrences'])
    df.sort_values(by='Occurrences', ascending=False, inplace=True)
    df.to_excel(chemin_export, index=False)
    print(f"Fichier Excel exporté : {chemin_export}")

def generer_graphe(ip_counts, chemin_image):
    df = pd.DataFrame(list(ip_counts.items()), columns=['IP', 'Occurrences'])
    df.sort_values(by='Occurrences', ascending=False, inplace=True)

    plt.figure(figsize=(12, 6))
    plt.bar(df['IP'], df['Occurrences'], color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Adresse IP")
    plt.ylabel("Occurrences")
    plt.title("Occurrences totales des adresses IP")
    plt.tight_layout()
    plt.savefig(chemin_image, bbox_inches='tight')
    print(f"Graphique sauvegardé : {chemin_image}")

def main():
    root = Tk()
    root.withdraw()
    chemin_fichier = filedialog.askopenfilename(title="Sélectionne ton fichier de logs s'il te plaît bien ?")

    if not chemin_fichier:
        print("Sauf erreur de ma part, il n'y a aucun fichier qui a été sélectionné... :-( ")
        return

    dossier = os.path.dirname(chemin_fichier)
    fichier_excel = os.path.join(dossier, "ban_ip_stats.xlsx")
    fichier_image = os.path.join(dossier, "ban_ip_graphique.png")

    ip_counts = analyser_fichier(chemin_fichier)
    exporter_excel(ip_counts, fichier_excel)
    generer_graphe(ip_counts, fichier_image)

if __name__ == "__main__":
    main()
