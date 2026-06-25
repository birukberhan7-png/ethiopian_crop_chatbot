# 🌿 Ethiopian Crop Recommendation Chatbot
### AI-Powered System for Endemic Plants in Ethiopia

---

## 📋 Project Overview

This is a complete AI-powered chatbot that recommends the best **endemic Ethiopian crops**
based on soil conditions, climate, altitude, and region — using a **Random Forest ML model**
trained on real Ethiopian agro-ecological data (1,500 rows).

### Supported Crops
| Crop | Amharic | Type |
|------|---------|------|
| Teff | ጤፍ | Highland grain |
| Enset | እንሰት | Highland staple |
| Coffee Arabica | ቡና | Export crop |
| Noug | ኑግ | Oilseed |
| Barley | ገብስ | Highland grain |
| Sorghum | ማሾ | Lowland grain |
| Finger Millet | ዳጉሣ | Nutritious grain |
| Chickpea | ሽምብራ | Legume |
| Linseed | ተልባ | Oilseed |
| Maize | በቆሎ | Staple grain |

---

## 🗂️ Project Structure

```
ethiopian_crop_chatbot/
├── backend/
│   ├── app.py                  ← Flask server + chatbot engine
│   ├── requirements.txt        ← Python dependencies
│   ├── ml/
│   │   └── train_model.py      ← ML training script (run once)
│   ├── models/                 ← Saved ML models (auto-generated)
│   │   ├── crop_model.pkl
│   │   ├── soil_encoder.pkl
│   │   ├── region_encoder.pkl
│   │   ├── crop_encoder.pkl
│   │   └── meta.json
│   └── dataset/
│       └── ethiopian_crop_recommendation_dataset.xlsx
├── frontend/
│   └── index.html              ← Full chatbot UI (pure HTML/JS)
└── database/
    └── schema.sql              ← SQL Server schema + seed data
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Step 1 — Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — Train the ML model (run once)
```bash
python ml/train_model.py
```
This reads the Excel dataset, trains a Random Forest classifier, and saves:
- `models/crop_model.pkl`
- `models/soil_encoder.pkl`
- `models/region_encoder.pkl`
- `models/crop_encoder.pkl`
- `models/meta.json`

Expected output:
```
✅ Accuracy: ~68%
💾 Model and encoders saved to backend/models/
```

### Step 3 — Start the Flask server
```bash
python app.py
```

### Step 4 — Open the chatbot
Open your browser and go to: **http://localhost:5000**

---

## 💬 How to Use the Chatbot

### Get a Crop Recommendation
Type naturally, for example:
```
My altitude is 2200m, temperature is 20°C, humidity 65%, rainfall 750mm, 
soil pH 6.2, loam soil
```

Or click **"Get Crop Recommendation"** in the sidebar and the bot will
guide you step by step, asking for each parameter.

### Ask About a Specific Crop
```
Tell me about Teff
Tell me about Coffee
What is Enset?
```

### Ask by Region
```
What crops grow in Oromia?
Best crops for Amhara region
Tigray farming
```

### Ask by Altitude
```
Best crop for altitude 2500m
What grows in highland Ethiopia?
Crops for lowland 800m
```

### Use Sidebar Shortcuts
- **Quick Actions** — common queries in one click
- **Explore Crops** — colored chips for each crop
- **Sample Data Entry** — pre-filled Highland / Lowland / Coffee zone examples

---

## 🌐 API Reference

### POST /api/chat
Chatbot conversation endpoint.
```json
Request:
{
  "message": "Tell me about Teff",
  "session_id": "abc123"
}

Response:
{
  "reply": "## 🌿 Teff\n\n...",
  "session_id": "abc123",
  "timestamp": "2025-01-01T12:00:00"
}
```

### POST /api/predict
Direct ML prediction (for integrations).
```json
Request:
{
  "temperature": 20,
  "humidity": 65,
  "rainfall": 750,
  "ph": 6.2,
  "altitude": 2200,
  "soil_type": "Loam",
  "nitrogen": 90,
  "phosphorus": 45,
  "potassium": 40,
  "region": "Amhara"
}

Response:
{
  "recommended_crop": "Teff",
  "confidence": "72.5%",
  "advice": "Plant at onset of main rains (June-July)...",
  "harvest": "85-95 days after sowing",
  "altitude_zone": "Mid Montane"
}
```

### GET /api/crops
Returns all 10 supported crops with full info.

### GET /api/meta
Returns model status, accuracy, and supported values.

---

## 🗄️ Database Setup (Optional)

To enable recommendation logging in SQL Server:
1. Open SQL Server Management Studio (SSMS)
2. Connect to your SQL Server instance
3. Open and run `database/schema.sql`
4. Install the `pyodbc` driver and update `app.py` with your connection string

---

## 🧠 ML Model Details

| Parameter | Value |
|-----------|-------|
| Algorithm | Random Forest Classifier |
| Training rows | 1,200 (80% of 1,500) |
| Test rows | 300 (20%) |
| Features | 10 (temp, humidity, rainfall, pH, altitude, N, P, K, soil, region) |
| Accuracy | ~68% |
| Fallback | Rule-based altitude logic when confidence < 45% |

### Altitude Zones
| Zone | Altitude | Primary Crops |
|------|----------|---------------|
| Afro-alpine | >3200m | Barley, Potato |
| Upper Montane | 2500–3200m | Barley, Linseed, Wheat |
| Mid Montane | 1800–2500m | Teff, Coffee, Maize |
| Lower Montane | 1200–1800m | Maize, Coffee, Enset |
| Lowland | <1200m | Sorghum, Finger Millet |

---

## 🇪🇹 Ethiopian Agro-ecological Zones

The system covers all major Ethiopian regions:
- **Oromia** — Teff, Coffee, Maize, Chickpea, Sorghum
- **Amhara** — Teff, Barley, Wheat, Chickpea, Linseed
- **Tigray** — Teff, Barley, Sorghum, Chickpea, Noug
- **Sidama** — Enset, Coffee, Teff, Maize
- **SNNPR** — Enset, Finger Millet, Coffee, Maize, Teff
- **Afar** — Sorghum, Finger Millet
- **Somali** — Sorghum, Finger Millet
- **Benishangul-Gumuz** — Maize, Sorghum, Teff

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Model | scikit-learn (Random Forest) |
| Backend | Python Flask |
| Frontend | Pure HTML5 + CSS3 + Vanilla JS |
| Data | pandas + openpyxl |
| Database | Microsoft SQL Server |
| Model Storage | joblib |

---

## 📞 Support

For issues or questions, check that:
1. Python 3.9+ is installed: `python --version`
2. All packages are installed: `pip install -r requirements.txt`
3. Model is trained: run `python ml/train_model.py`
4. Server is running: `python app.py`
5. Browser points to: `http://localhost:5000`
6. cont