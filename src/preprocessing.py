import pandas as pd
import numpy as np
import glob

# =========================
# STEP 1: LOAD ALL CSV FILES
# =========================
files = glob.glob("../data/raw/*.csv")

print("Files found:", files)

df_list = []

for file in files:
    print("Loading:", file)
    temp = pd.read_csv(file, encoding='latin1', low_memory=False)
    df_list.append(temp)

df = pd.concat(df_list, ignore_index=True)

print("\nInitial Shape:", df.shape)


# =========================
# STEP 2: CLEAN DATA
# =========================
df.columns = df.columns.str.strip()

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

df.drop_duplicates(inplace=True)

print("After Cleaning Shape:", df.shape)


# =========================
# STEP 3: LABEL PROCESSING
# =========================
# BENIGN = 0, Attack = 1
df['Label'] = df['Label'].apply(lambda x: 0 if x == 'BENIGN' else 1)

print("\nLabel distribution:")
print(df['Label'].value_counts())


# =========================
# STEP 4: DROP UNNECESSARY COLUMNS
# =========================
df.drop(columns=[
    'Flow ID',
    'Source IP',
    'Destination IP',
    'Timestamp'
], errors='ignore', inplace=True)


# =========================
# STEP 5: KEEP ONLY NUMERIC DATA
# =========================
df = df.select_dtypes(include=['number'])


# =========================
# STEP 6: FINAL CHECK
# =========================
print("\nFinal Shape:", df.shape)
print(df.head())


# =========================
# STEP 7: SAVE CLEAN DATASET
# =========================
df.to_csv("../data/combined_cleaned.csv", index=False)

print("\n✅ Preprocessing Completed Successfully!")
print("Saved as: data/combined_cleaned.csv")