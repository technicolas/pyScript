# Attention, il faut installer speedtest-cli
# En W$, avec: pip install speedtest-cli

# import speedtest

# # Initialisation
# st = speedtest.Speedtest()

# # Choisir le meilleur serveur
# st.get_best_server()

# # Mesures
# download_speed = st.download() / 1_000_000  # en Mbps
# upload_speed = st.upload() / 1_000_000      # en Mbps
# ping = st.results.ping                      # en ms

# # Affichage des résultats
# print(f"Download : {download_speed:.2f} Mbps")
# print(f"Upload   : {upload_speed:.2f} Mbps")
# print(f"Ping     : {ping:.2f} ms")






import speedtest
import csv
import datetime
import matplotlib.pyplot as plt

# Mesure
import speedtest

st = speedtest.Speedtest()
servers = st.get_servers()
for sid, info in servers.items():
    if "Belgium" in info[0]['country']:
        print(f"ID: {sid}, Ville: {info[0]['name']}, Fournisseur: {info[0]['sponsor']}")

# st.get_best_server()
download_speed = st.download() / 1_000_000  # Mbps
upload_speed = st.upload() / 1_000_000      # Mbps
ping = st.results.ping                      # ms
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Enregistrement dans CSV
filename = 'internet_speed_log.csv'
with open(filename, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([timestamp, download_speed, upload_speed, ping])

print("Résultat enregistré dans le fichier")

# Lecture des données et création du graphique
timestamps, downloads, uploads, pings = [], [], [], []

with open(filename, mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        timestamps.append(row[0])
        downloads.append(float(row[1]))
        uploads.append(float(row[2]))
        pings.append(float(row[3]))

# Affichage du graphique
plt.figure(figsize=(10, 6))
plt.plot(timestamps, downloads, label='Download (Mbps)', marker='o')
plt.plot(timestamps, uploads, label='Upload (Mbps)', marker='x')
plt.plot(timestamps, pings, label='Ping (ms)', marker='s')
plt.xlabel('Date')
plt.ylabel('Vitesse / Ping')
plt.title('Historique de vitesse de connexion')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()