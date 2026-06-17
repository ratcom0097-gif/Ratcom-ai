# RIAL AI — Backend WhatsApp IA

Backend Node.js qui gère les sessions WhatsApp via Baileys et les réponses automatiques via Claude API (Anthropic).

---

## 🗂️ Structure

```
src/
├── index.js              ← Point d'entrée Express
├── middleware/
│   └── auth.js           ← Protection API Key
├── routes/
│   ├── sessions.js       ← Gérer les sessions WhatsApp
│   ├── webhooks.js       ← Configurer les webhooks sortants
│   └── health.js         ← Statut du serveur
└── lib/
    ├── session.js        ← Cœur : Baileys + gestion sessions
    ├── claude.js         ← Réponses IA via Claude API
    ├── sheets.js         ← Sync Google Sheets
    ├── hubspot.js        ← Sync HubSpot CRM
    └── webhook.js        ← Notifications webhook sortantes
```

---

## 🚀 Déploiement sur Railway

### 1. Préparer le projet

```bash
git init
git add .
git commit -m "init: RIAL AI backend"
```

### 2. Créer un projet Railway

1. Allez sur [railway.app](https://railway.app)
2. **New Project → Deploy from GitHub repo**
3. Sélectionnez votre repository

### 3. Configurer les variables d'environnement

Dans Railway → **Variables**, ajoutez :

| Variable | Valeur |
|---|---|
| `PORT` | `3000` |
| `NODE_ENV` | `production` |
| `API_SECRET` | `votre-clé-secrète-longue` |
| `ANTHROPIC_API_KEY` | `sk-ant-...` |
| `GOOGLE_SHEET_ID` | *(optionnel)* |
| `GOOGLE_SERVICE_ACCOUNT_EMAIL` | *(optionnel)* |
| `GOOGLE_PRIVATE_KEY` | *(optionnel)* |
| `HUBSPOT_ACCESS_TOKEN` | *(optionnel)* |

### 4. Railway déploie automatiquement ✅

---

## 📡 API Reference

Toutes les routes protégées nécessitent le header :
```
x-api-key: votre-API_SECRET
```

### Sessions

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/api/sessions` | Créer une session |
| `GET` | `/api/sessions/:id/qr` | Obtenir le QR code |
| `GET` | `/api/sessions` | Lister toutes les sessions |
| `GET` | `/api/sessions/:id` | Détail d'une session |
| `DELETE` | `/api/sessions/:id` | Déconnecter une session |

### Webhooks

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/api/webhooks` | Configurer un webhook |
| `GET` | `/api/webhooks` | Lister les webhooks |
| `DELETE` | `/api/webhooks/:sessionId` | Supprimer un webhook |

### Health

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/health` | Statut du serveur |

---

## 🔄 Flux complet

```
Client WhatsApp → Message entrant
    → Baileys reçoit le message
    → Claude API génère une réponse
    → Réponse envoyée au client WhatsApp
    → Google Sheets: nouvelle ligne ajoutée
    → HubSpot: contact créé/note ajoutée
    → Webhook sortant notifié
```

---

## 🧪 Tester en local

```bash
npm install
cp .env.example .env
# Remplissez .env avec vos clés
npm run dev
```

Créer une session :
```bash
curl -X POST http://localhost:3000/api/sessions \
  -H "x-api-key: votre-secret" \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "client_001", "aiPrompt": "Tu es lassistant de la boutique Merci, réponds en français."}'
```

Récupérer le QR code :
```bash
curl http://localhost:3000/api/sessions/client_001/qr \
  -H "x-api-key: votre-secret"
```
