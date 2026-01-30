# 🌍 MonSéjour.fr - Planificateur de Voyage Intelligent

**MonSéjour** est une application Python orientée objet conçue pour centraliser et personnaliser l'expérience de voyage en agrégeant des données multi-sources (Météo, Transport, Culture, Gastronomie).

## 🚀 Fonctionnalités Clés
* **Profilage Utilisateur :** Filtrage intelligent par budget et régimes alimentaires (Vegan, Halal).
* **Multi-Sourcing :** Intégration d'API REST (Open-Meteo, Data.Culture) et Web Scraping (Guide Michelin).
* **Architecture POO :** Code modulaire structuré en classes métiers et gestionnaires de données.
* **Persistance Locale :** Export et traitement des données via Pandas pour une consultation hors-ligne.

## 🏗️ Architecture Technique
L'application repose sur un moteur de collecte robuste :
- **Collecte :** Gestionnaire de requêtes HTTP et Parsing.
- **Modélisation :** Classes dédiées pour chaque type d'item (Hôtel, Restaurant, etc.).
- **Traitement :** Utilisation de DataFrames Pandas pour le filtrage dynamique.



## 📊 Sources de Données
| Catégorie | Source | Format |
| :--- | :--- | :--- |
| **Météo** | Open-Meteo API | JSON |
| **Restauration** | Guide Michelin | Scraping HTML |
| **Culture** | Data.Culture.gouv | JSON |
| **Transport** | WFS MEL / ODS | GeoJSON |

