import requests
import csv
import os
import random
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
DOSSIER_DATA = r"C:\Users\Adam\Documents\Université\wahil\nb\SAE Collecte auto de données web\SAE\data"

# --- 1. CLASSES ITEMS ---
class Profil:
    def __init__(self, nom, age, budget_max, nb_personnes, preferences, regime):
        self.nom, self.age, self.budget_max = nom, age, budget_max
        self.nb_personnes, self.preferences, self.regime = nb_personnes, preferences, regime

class Restaurant:
    def __init__(self, nom, cuisine, prix, lat, lon):
        self.nom, self.cuisine, self.prix, self.lat, self.lon = nom, cuisine, prix, lat, lon

class Hotel:
    def __init__(self, nom, etoiles, prix, lat, lon):
        self.nom, self.etoiles, self.prix, self.lat, self.lon = nom, etoiles, prix, lat, lon

class Loisir:
    def __init__(self, nom, type_l, lat, lon):
        self.nom, self.type_l, self.lat, self.lon = nom, type_l, lat, lon

class Transport:
    def __init__(self, nom, type_transport, lat, lon):
        self.nom, self.type_transport, self.lat, self.lon = nom, type_transport, lat, lon

class Meteo:
    def __init__(self, ville, temperature, description):
        self.ville, self.temp, self.desc = ville, temperature, description


# --- 2. CLASSE COLLECTE (Moteur d'APIs) ---
class Collecte:
    @staticmethod
    def api_ods(dataset, ville, champ_ville="meta_name_com"):
        url = f"https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/{dataset}/records"
        results = []
        limit, offset = 100, 0
        while True:
            params = {"limit": limit, "offset": offset, "where": f"{champ_ville} like '{ville}'"}
            try:
                r = requests.get(url, params=params, timeout=10).json()
                batch = r.get("results", [])
                if not batch: break
                results.extend(batch)
                offset += limit
            except: break
        return results

    @staticmethod
    def api_culture(ville):
        url = "https://data.culture.gouv.fr/api/explore/v2.1/catalog/datasets/base-des-lieux-et-des-equipements-culturels/records"
        results = []
        limit, offset = 100, 0
        while True:
            params = {"limit": limit, "offset": offset, "where": f"libelle_geographique like '{ville}'"}
            try:
                r = requests.get(url, params=params, timeout=10).json()
                batch = r.get("results", [])
                if not batch: break
                results.extend(batch)
                offset += limit
            except: break
        return results

    @staticmethod
    def scraping_michelin():
        url = "https://guide.michelin.com/fr/fr/restaurants"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        results = []
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.content, 'html.parser')
            for it in soup.select('.card__menu'):
                nom_tag = it.find('h3', class_='card__menu-content-title')
                info_tag = it.find('div', class_='card__menu-footer--price')
                if nom_tag:
                    results.append({
                        'name': nom_tag.get_text().strip(), 
                        'cuisine': info_tag.get_text().strip() if info_tag else "Gastronomique"
                    })
            return results
        except: return []

    @staticmethod
    def api_meteo(lat=50.62, lon=3.05):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        try: return requests.get(url, timeout=10).json().get("current_weather", {})
        except: return {}


# --- 3. GESTIONNAIRES ---
class Restaurants:
    def __init__(self): self.liste_objets = []
    def charger(self, ville):
        self.liste_objets = [] 
        for i in Collecte.api_ods("osm-france-food-service", ville):
            geo = i.get('meta_geo_point', {})
            self.liste_objets.append(Restaurant(i.get('name', 'Resto'), i.get('cuisine', 'Divers'), random.randint(18, 42), geo.get('lat'), geo.get('lon')))
        for m in Collecte.scraping_michelin():
            info = m['cuisine']
            p = 85 if "€€€" in info else 55 if "€€" in info else 35
            self.liste_objets.append(Restaurant(m['name'], info, p, 50.63, 3.06))
    def to_csv(self, filename):
        path = os.path.join(DOSSIER_DATA, filename)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(["Nom", "Cuisine", "Prix", "Lat", "Lon"])
            for r in self.liste_objets: w.writerow([r.nom, r.cuisine, r.prix, r.lat, r.lon])

class Hotels:
    def __init__(self): self.liste_objets = []
    def charger(self, ville):
        self.liste_objets = [] 
        for i in Collecte.api_ods("osm-france-tourism-accommodation", ville):
            geo = i.get('meta_geo_point', {})
            stars = i.get('stars', '')
            try: p = 60 + (int(stars) * 35) if stars else 85
            except: p = 85
            self.liste_objets.append(Hotel(i.get('name', 'Hôtel'), stars, p, geo.get('lat'), geo.get('lon')))
    def to_csv(self, filename):
        path = os.path.join(DOSSIER_DATA, filename)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(["Nom", "Etoiles", "Prix", "Lat", "Lon"])
            for h in self.liste_objets: w.writerow([h.nom, h.etoiles, h.prix, h.lat, h.lon])

class Loisirs:
    def __init__(self): self.liste_objets = []
    def charger(self, ville):
        self.liste_objets = [] 
        for i in Collecte.api_culture(ville):
            self.liste_objets.append(Loisir(i.get('nom', 'Lieu'), i.get('type_equipement_ou_lieu', 'Culture'), i.get('latitude'), i.get('longitude')))
    def to_csv(self, filename):
        path = os.path.join(DOSSIER_DATA, filename)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(["Nom", "Type", "Lat", "Lon"])
            for l in self.liste_objets: w.writerow([l.nom, l.type_l, l.lat, l.lon])

class Transports:
    def __init__(self): self.liste_objets = []
    def charger(self, ville):
        self.liste_objets = [] 
        ville_clean = ville.strip().upper()
        for i in Collecte.api_ods("osm-france-stops-railway", ville_clean):
            geo = i.get('meta_geo_point', {})
            self.liste_objets.append(Transport(i.get('name', 'Gare'), "Train/Gare", geo.get('lat'), geo.get('lon')))
        villes_mel = ["LILLE", "ROUBAIX", "TOURCOING", "VILLENEUVE-D'ASCQ", "WATTRELOS", "CROIX"]
        if ville_clean in villes_mel:
            ville_api = ville_clean.replace("'", "''")
            url_wfs = (
                f"https://data.lillemetropole.fr/geoserver/wfs?SERVICE=WFS&REQUEST=GetFeature&"
                f"VERSION=2.0.0&TYPENAMES=dsp_ilevia%3Aarret_point&OUTPUTFORMAT=application%2Fjson&"
                f"SRSNAME=EPSG%3A4326&CQL_FILTER=commune%20LIKE%20'{ville_api}'"
            )
            try:
                res = requests.get(url_wfs, timeout=15).json()
                features = res.get('features', [])
                for feature in features:
                    prop = feature.get('properties', {})
                    geom = feature.get('geometry', {})
                    coords = geom.get('coordinates', [0, 0])
                    l_type = prop.get('location_type')
                    type_label = "Métro/Tram" if str(l_type) == '1' else "Bus"
                    self.liste_objets.append(Transport(prop.get('stop_name', 'Arrêt'), type_label, coords[1], coords[0]))
            except: pass
    def to_csv(self, filename):
        path = os.path.join(DOSSIER_DATA, filename)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(["Nom", "Type", "Lat", "Lon"])
            for t in self.liste_objets: w.writerow([t.nom, t.type_transport, t.lat, t.lon])

class Meteos:
    def __init__(self): self.donnees = None
    def charger(self, ville):
        raw = Collecte.api_meteo()
        self.donnees = Meteo(ville, raw.get('temperature'), "Stable" if raw.get('weathercode', 0) < 3 else "Perturbé")


# --- 4. CLASSE VOYAGE ---
class Voyage:
    def __init__(self, ville, profil):
        self.ville, self.profil = ville, profil
        self.h_m, self.r_m, self.l_m = Hotels(), Restaurants(), Loisirs()
        self.t_m, self.meteo_m = Transports(), Meteos()

    def generer(self):
        self.h_m.charger(self.ville)
        self.r_m.charger(self.ville)
        self.l_m.charger(self.ville)
        self.t_m.charger(self.ville)
        self.meteo_m.charger(self.ville)
        self.h_m.to_csv(f"hotels_{self.ville}.csv")
        self.r_m.to_csv(f"restaurants_{self.ville}.csv")
        self.l_m.to_csv(f"loisirs_{self.ville}.csv")
        self.t_m.to_csv(f"transports_{self.ville}.csv")


# --- 5. CLASSE INTERFACE (Backend pour le Notebook) ---
class Interface:
    @staticmethod
    def preparer_sejour(ville, nb_pers):
        p = Profil("Test", 20, 500, nb_pers, ["Culture"], "Vegan")
        v = Voyage(ville, p)
        v.generer()
        return p, v

    @staticmethod
    def afficher_bilan_synchro(v):
        modes = ", ".join(set(t.type_transport for t in v.t_m.liste_objets)) if v.t_m.liste_objets else "Aucun"
        print(f"✅ SYNCHRONISATION : {v.ville.upper()}")
        print(f"🏨 {len(v.h_m.liste_objets)} Hôtels | 🍴 {len(v.r_m.liste_objets)} Restos | 🚇 {modes}")

    @staticmethod
    def fiche_hotel_html(hotel_nom, df_h, ville):
        if hotel_nom not in df_h['Nom'].values: return ""
        info = df_h[df_h['Nom'] == hotel_nom].iloc[0]
        prix = info.get('Prix', 80)
        etoiles = info.get('Etoiles', 3)
        # On peut pointer vers l'image du logo monséjour ou une image par défaut
        img_path = "data/logo-monséjour.png" 
        
        return f"""
        <div style="border: 2px solid #3498db; padding: 20px; border-radius: 15px; background-color: #f7f9fc; display: flex; align-items: center; gap: 20px;">
            <div style="flex: 1;">
                <h2 style="color: #2c3e50; margin-top: 0;">{info['Nom']}</h2>
                <p style="font-size: 1.2em; color: #f1c40f;">{"★" * int(etoiles if etoiles else 3)}</p>
                <p style="font-size: 1.1em;"><b>💰 Tarif :</b> {prix}€ la nuit</p>
                <p style="color: #7f8c8d; font-size: 0.9em;">📍 {ville.capitalize()}</p>
            </div>
            <div style="width: 150px; height: 100px; background: white; border-radius: 10px; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 1px solid #ddd;">
                 <img src="https://via.placeholder.com/150x100?text=Hotel+Ref" style="width: 100%; height: auto;">
            </div>
        </div>
        """

    @staticmethod
    def obtenir_restaurants_filtres(ville, regime, style, prix_max):
        import pandas as pd
        path = os.path.join(DOSSIER_DATA, f"restaurants_{ville}.csv")
        if not os.path.exists(path): return pd.DataFrame()
        df_r = pd.read_csv(path, sep=';')
        df_r['Prix'] = pd.to_numeric(df_r['Prix'], errors='coerce')
        mask = (df_r['Prix'] <= prix_max)
        if regime.lower() != 'omnivore':
            mask &= (df_r['Cuisine'].str.lower().str.contains(regime.lower(), na=False))
        if style:
            mask &= (df_r['Cuisine'].str.lower().str.contains(style.lower(), na=False))
        return df_r[mask].sort_values(by='Prix').head(10)

    @staticmethod
    def trouver_stations_proches(v, lat_dep, lon_dep, lat_arr, lon_arr):
        import pandas as pd
        path = os.path.join(DOSSIER_DATA, f"transports_{v.ville}.csv")
        if not os.path.exists(path): return None, None
        df_t = pd.read_csv(path, sep=';')
        df_t['Lat'] = pd.to_numeric(df_t['Lat'], errors='coerce')
        df_t['Lon'] = pd.to_numeric(df_t['Lon'], errors='coerce')
        df_t['dist_dep'] = ((df_t['Lat'] - float(lat_dep))**2 + (df_t['Lon'] - float(lon_dep))**2)**0.5
        df_t['dist_arr'] = ((df_t['Lat'] - float(lat_arr))**2 + (df_t['Lon'] - float(lon_arr))**2)**0.5
        return df_t.sort_values('dist_dep').iloc[0], df_t.sort_values('dist_arr').iloc[0]

    @staticmethod
    def generer_carte_trajet(h_lat, h_lon, dest_lat, dest_lon, st_dep, st_arr, dest_nom):
        import folium
        m = folium.Map(location=[(float(h_lat) + float(dest_lat))/2, (float(h_lon) + float(dest_lon))/2], zoom_start=14)
        folium.Marker([float(h_lat), float(h_lon)], popup="Hôtel", icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker([float(dest_lat), float(dest_lon)], popup=dest_nom, icon=folium.Icon(color='orange')).add_to(m)
        folium.Marker([float(st_dep['Lat']), float(st_dep['Lon'])], popup=f"Départ: {st_dep['Nom']}", icon=folium.Icon(color='green', icon='subway', prefix='fa')).add_to(m)
        folium.Marker([float(st_arr['Lat']), float(st_arr['Lon'])], popup=f"Arrivée: {st_arr['Nom']}", icon=folium.Icon(color='green', icon='subway', prefix='fa')).add_to(m)
        folium.PolyLine([[float(st_dep['Lat']), float(st_dep['Lon'])], [float(st_arr['Lat']), float(st_arr['Lon'])]], color="red", weight=4).add_to(m)
        return m

    @staticmethod
    def afficher_recap_complet_budget(hotel, resto, nb_pers, budget_max, df_h, df_r):
        import ipywidgets as widgets
        from IPython.display import display
        try:
            h_p = float(df_h[df_h['Nom'] == hotel].iloc[0]['Prix'])
            r_p_total = float(df_r[df_r['Nom'] == resto].iloc[0]['Prix']) * int(nb_pers)
            t_p_total = 5.0 * int(nb_pers)
            total = h_p + r_p_total + t_p_total
            print(f"👥 Voyageurs : {nb_pers} | 🏨 {h_p}€ | 🍴 {r_p_total}€ | 🚇 {t_p_total}€")
            print(f"💰 TOTAL : {total:.2f}€ / {budget_max:.2f}€")
            style = 'success' if total <= budget_max else 'danger'
            display(widgets.FloatProgress(value=total, min=0, max=max(budget_max, total), bar_style=style, layout={'width': '100%'}))
        except: print("⏳ Sélections incomplètes.")

    @staticmethod
    def generer_recap_texte(v, hotel_nom, resto_nom, activite_nom):
        return f"{'='*40}\n🌍 SÉJOUR À {v.ville.upper()}\n🏨 Hôtel : {hotel_nom}\n🎨 Activité : {activite_nom}\n🍴 Dîner : {resto_nom}\n{'='*40}"

if __name__ == "__main__":
    if not os.path.exists(DOSSIER_DATA): os.makedirs(DOSSIER_DATA)