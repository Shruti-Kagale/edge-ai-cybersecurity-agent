import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("../data/combined_cleaned.csv")

print("Dataset Shape:", df.shape)

# =========================
# REMOVE DUPLICATES
# =========================
duplicates = df.duplicated().sum()
print("Duplicate Rows:", duplicates)

df = df.drop_duplicates()

print("Shape After Removing Duplicates:", df.shape)

# =========================
# CHECK CLASS BALANCE
# =========================
print("\nClass Distribution:")
print(df["Label"].value_counts())

# =========================
# SPLIT FEATURES & LABEL
# =========================
X = df.drop("Label", axis=1)
y = df["Label"]

# =========================
# TRAIN-TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# =========================
# FAST + OPTIMIZED MODEL
# =========================
model = RandomForestClassifier(
    n_estimators=50,
    max_depth=15,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

# =========================
# TRAIN MODEL
# =========================
print("\nTraining Model...")

model.fit(X_train, y_train)

print("Training Completed!")

# =========================
# PREDICTION
# =========================
y_pred = model.predict(X_test)

# =========================
# EVALUATION
# =========================
print("\nTest Accuracy:")
print(accuracy_score(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# =========================
# TRAIN vs TEST CHECK
# =========================
train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)

print("\nTrain Accuracy:", train_acc)
print("Test Accuracy:", test_acc)

# =========================
# FEATURE CORRELATION CHECK
# =========================
print("\nTop Correlated Features With Label:")

corr = df.corr(numeric_only=True)["Label"].sort_values(ascending=False)

print(corr.head(10))

# =========================
# CROSS VALIDATION
# =========================
print("\nRunning Cross Validation...")

scores = cross_val_score(
    model,
    X,
    y,
    cv=3,          # reduced for speed
    scoring='accuracy'
)

print("Cross Validation Scores:", scores)
print("Average CV Accuracy:", scores.mean())

# =========================
# SAVE MODEL
# =========================
os.makedirs("models", exist_ok=True)

# SAVE MODEL
joblib.dump(model, "models/model.pkl")

# SAVE COLUMN NAMES
joblib.dump(X.columns.tolist(), "models/columns.pkl")

print("\nModel Saved Successfully!")