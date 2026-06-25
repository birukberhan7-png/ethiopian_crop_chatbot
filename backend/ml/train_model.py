"""
Ethiopian Crop Recommendation - ML Training Script
Trains a Random Forest model on the Ethiopian crop dataset.
Run this once before starting the Flask server.
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "ethiopian_crop_recommendation_dataset.xlsx")
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ─── Load Dataset ─────────────────────────────────────────────────────────────
print("📦 Loading dataset...")
df = pd.read_excel(DATASET_PATH)
print(f"   Rows: {len(df)}  |  Columns: {df.columns.tolist()}")

# ─── Encode Categorical Features ──────────────────────────────────────────────
soil_encoder = LabelEncoder()
region_encoder = LabelEncoder()
crop_encoder = LabelEncoder()

df["Soil_Encoded"] = soil_encoder.fit_transform(df["Soil_Type"])
df["Region_Encoded"] = region_encoder.fit_transform(df["Region"])
df["Crop_Encoded"] = crop_encoder.fit_transform(df["Crop"])

# ─── Feature / Label Split ────────────────────────────────────────────────────
FEATURES = [
    "Temperature_C", "Humidity_%", "Rainfall_mm",
    "pH", "Altitude_m",
    "Nitrogen", "Phosphorus", "Potassium",
    "Soil_Encoded", "Region_Encoded"
]

X = df[FEATURES]
y = df["Crop_Encoded"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ─── Train ────────────────────────────────────────────────────────────────────
print("🤖 Training Random Forest Classifier...")
clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
clf.fit(X_train, y_train)

# ─── Evaluate ─────────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy: {acc * 100:.2f}%")
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred, target_names=crop_encoder.classes_))

# ─── Save Artifacts ───────────────────────────────────────────────────────────
joblib.dump(clf,            os.path.join(MODEL_DIR, "crop_model.pkl"))
joblib.dump(soil_encoder,   os.path.join(MODEL_DIR, "soil_encoder.pkl"))
joblib.dump(region_encoder, os.path.join(MODEL_DIR, "region_encoder.pkl"))
joblib.dump(crop_encoder,   os.path.join(MODEL_DIR, "crop_encoder.pkl"))

# Save metadata (feature list, unique values)
meta = {
    "features": FEATURES,
    "soil_types":   soil_encoder.classes_.tolist(),
    "regions":      region_encoder.classes_.tolist(),
    "crops":        crop_encoder.classes_.tolist(),
    "accuracy":     round(acc * 100, 2)
}
with open(os.path.join(MODEL_DIR, "meta.json"), "w") as f:
    json.dump(meta, f, indent=2)

print("\n💾 Model and encoders saved to backend/models/")
print("🚀 You can now start the Flask server: python app.py")
