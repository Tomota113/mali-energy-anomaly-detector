# ⚡ Mali Energy Anomaly Detector

> **Proof of Concept (PoC) développé pour la Semaine du Numérique au Mali**  
> *Plateforme d'Intelligence Artificielle pour la Détection des Pertes Non-Techniques et Fraudes de Consommation Électrique.*

---

## 📌 Présentation du Projet

En Afrique de l'Ouest et particulièrement au Mali, la détection des **pertes non-techniques** (dérivation illégale, compteurs détériorés, fraudes ou surcharges de ligne) représente un défi majeur pour les compagnies d'électricité et les gestionnaires de réseaux micro-grid.

**Mali Energy Anomaly Detector** est un PoC combinant l'algorithme d'apprentissage non supervisé **Isolation Forest** de *Scikit-Learn* avec un tableau de bord web interactif propulsé par *Streamlit* et *Plotly*.

### ✨ Fonctionnalités Clés
- 📊 **Génération & Analyse de données IoT/Compteurs Intelligents** : Analyse en temps réel des séries temporelles (Tension, Consommation kWh, Courant A, Facteur de Puissance).
- 🧠 **Détection Automatique par Machine Learning** : Algorithme Isolation Forest capable d'isoler les comportements anormaux et de calculer un score de suspicion (0 à 1).
- 💰 **Évaluation de l'Impact Financier** : Estimation dynamique des pertes d'énergie et du risque financier évalué en **FCFA**.
- 📈 **Visualisation Graphique Dynamic** : Courbes de consommation interactives avec mise en valeur instantanée des points critiques en rouge.
- 📥 **Exportation des Rapports** : Téléchargement direct des journaux d'anomalies filtrés au format CSV.

---

## 🛠️ Stack Technique

- **Langage** : Python 3.10+
- **Machine Learning** : Scikit-Learn (`IsolationForest`, `StandardScaler`)
- **Data & Traitement** : Pandas, NumPy
- **Interface Web & Visualisation** : Streamlit, Plotly Express & Graph Objects
- **Environnement & OS** : Linux Ubuntu, VS Code, Git

---

## 📂 Arborescence du Projet

```text
mali-energy-anomaly-detector/
├── app.py                      # Application web Streamlit principale
├── requirements.txt            # Dépendances du projet
├── README.md                   # Documentation du projet
├── .gitignore                  # Fichiers à ignorer par Git
├── data/
│   └── energy_consumption_sample.csv  # Dataset d'exemple synthétique
└── src/
    ├── __init__.py
    ├── data_generator.py       # Générateur de données de consommation
    └── anomaly_detector.py     # Modèle et prétraitement ML
```

---

## 🚀 Guide d'Installation et d'Exécution Rapide

### 1. Cloner le projet et accéder au dossier
```bash
git clone https://github.com/Tomota113/mali-energy-anomaly-detector.git
cd mali-energy-anomaly-detector
```

### 2. Créer et activer l'environnement virtuel Python
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Lancer l'application Streamlit
```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`.

---

## 👤 Auteur & Contact

**Ibrahim Tomota**  
*Étudiant en IA & Science des Données | Machine Learning & Software Engineering*  
- **GitHub** : [@Tomota113](https://github.com/Tomota113)  
- **LinkedIn** : [Ibrahim Tomota](https://www.linkedin.com/in/ibrahim-tomota-056756330)  
- **Email** : `itomota11@gmail.com`
