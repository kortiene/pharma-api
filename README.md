# 💊 pharma-api — Gestion intelligente des stocks pharmaceutiques

`pharma-api` est une plateforme complète de **gestion intelligente des stocks pharmaceutiques**, combinant logique métier, simulation de données, analyse IA et génération de langage naturel avec un **LLM local intégré (LLaMA 3)**.

Ce projet a pour objectif de fournir un **assistant autonome et conversationnel** pour les pharmaciens, capable de :

- Générer des alertes intelligentes (seuils critiques, péremptions)
- Prédire les besoins en commande
- Analyser les ruptures et les performances
- Expliquer les indicateurs en langage naturel
- Aider à la prise de décision via un moteur LLM local (LLaMA 3)

> 🧪 Idéal pour les pharmacies, centres hospitaliers, laboratoires ou ONG en contexte à ressources limitées.

---

## 🚀 Fonctionnalités principales

- 🧠 **Agent IA métier** avec 7 cas d’usage automatisés
- 🧮 **Simulateur complet de données pharmaceutiques** (produits, mouvements, stock)
- 📡 **API FastAPI RESTful** pour interaction avec les modules IA
- 🤖 **Moteur LLaMA 3 intégré localement** (via `llama-cpp-python`)
- 💬 **Prompts spécialisés dynamiques** par usecase pour enrichir les réponses LLM
- 🔁 API conversationnelle pour pharmacien

---

## 🛣️ Roadmap Technique – `pharma-api`

### ✅ **Phase 1 — Fonctionnalités principales (✔ Réalisé)**

- [x] Mise en place d’un simulateur de produits, mouvements et stocks (MongoDB)
- [x] Implémentation de l’agent IA `SmartInventoryAgent` avec 7 cas d’usage :
  - Prévision de consommation
  - Alerte seuil critique
  - Péremption
  - Audit d’inventaire
  - KPI
  - Proposition de commande
  - Vérification de livraison
- [x] API FastAPI pour exposer chaque fonctionnalité
- [x] Intégration d’un moteur LLaMA 3 local (`llama-cpp-python`)
- [x] Génération de prompts dynamiques spécialisés par usecase
- [x] Endpoints `/llm/...` pour enrichissement des analyses via LLM

### 🚧 **Phase 2 — Fiabilisation & UX conversationnelle (En cours)**

- [ ] 🔐 Sécurisation des endpoints API (authentification simple ou JWT)
- [ ] 💬 Ajout d’un **mode conversationnel pharmacien-agent IA** (chat UI ou API dialoguée)
- [ ] 🧠 Injection automatique de contexte métier dans les prompts (`stocks`, `alertes`, `historique`)
- [ ] 📥 Système de feedback utilisateur sur les réponses du LLM
- [ ] 📦 Création de jeux de tests automatisés (Pytest) pour l’agent IA

### 🧭 **Phase 3 — Intégration terrain & mobile (À venir)**

- [ ] 📱 Connexion à une interface mobile ou web pour pharmacien (React, Streamlit, Flutter)
- [ ] 🔁 Ajout d’un cron / planificateur pour exécuter les vérifications automatiquement
- [ ] 🧾 Génération de rapports PDF téléchargeables (inventaire, KPI, alertes)
- [ ] 📊 Visualisation des données via un tableau de bord embarqué
- [ ] ☁️ Déploiement cloud local ou hybride (Docker, OVH, Render)

### 💡 **Idées à explorer**

- 🔮 Prédiction automatique de rupture basée sur tendances
- 🧪 Recommandation de remplacement de produits en fonction des ruptures
- 🤝 Connexion avec systèmes de gestion pharmaceutique externes (ERP, API fournisseurs)
- 🧑‍⚕️ Mode formation IA pour apprentissage interactif (agent pédagogique)

---

## 🧰 Technologies principales

- Python 3.11+
- FastAPI / Uvicorn
- MongoDB
- Pydantic
- llama-cpp-python + LLaMA 3 (local LLM)
- Pytest (à venir)

---

## 🛠️ Installation locale

```bash
# 1. Cloner le repo
git clone https://github.com/kortiene/pharma-api.git
cd pharma-api

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Démarrer l'API
uvicorn main:app --reload --port 8000

# 4. Lancer le simulateur (facultatif)
python main.py
```

Assurez-vous que **MongoDB est bien installé et accessible** sur le port `27017`.

---

## 📬 Contact & Contributeurs

Ce projet est maintenu par [Sekou Oumar KONE](https://github.com/kortiene) – Incubtek.

Contributions bienvenues via pull requests ou issues GitHub 🙌
