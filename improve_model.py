import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
import joblib

print("### Mulai Proses Penyempurnaan Model dan Data ###")

# ----------------------------------------------------------------------------------
# 1. Memuat dan Membersihkan Dataset (dengan fitur tambahan)
# ----------------------------------------------------------------------------------

print("Memuat dan membersihkan data dengan fitur-fitur baru...")
try:
    data = pd.read_csv('Speed-Dating-Data.csv', encoding='latin1')
except FileNotFoundError:
    print("Error: File 'Speed-Dating-Data.csv' tidak ditemukan. Pastikan file ada di direktori yang sama.")
    exit()

# Kolom 'match' adalah target kita
data.dropna(subset=['match'], inplace=True)

# Memilih fitur-fitur yang lebih lengkap, termasuk yang baru
features_to_use = [
    'int_corr', 'age', 'age_o', 'samerace', 'pf_o_att', 'pf_o_sin', 
    'pf_o_int', 'pf_o_fun', 'pf_o_amb', 'pf_o_sha', 'attr1_1', 'sinc1_1', 
    'intel1_1', 'fun1_1', 'amb1_1', 'shar1_1',
    # Fitur-fitur baru yang ditambahkan
    'imprace', 'imprelig', 'go_out'
]

X = data[features_to_use]
y = data['match']

# Mengatasi nilai yang hilang (missing values)
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)
X = pd.DataFrame(X_imputed, columns=X.columns)

print(f"Jumlah nilai NaN setelah imputasi: {X.isnull().sum().sum()}")
print(f"Jumlah fitur yang digunakan: {len(X.columns)}")

# ----------------------------------------------------------------------------------
# 2. Hyperparameter Tuning dengan GridSearchCV
# ----------------------------------------------------------------------------------

print("\nMencari parameter terbaik untuk model menggunakan GridSearchCV...")
# Tentukan rentang parameter yang ingin diuji
param_grid = {
    'n_estimators': [100, 200, 300],  # Jumlah pohon dalam forest
    'max_depth': [10, 20, None],       # Kedalaman maksimum pohon
    'min_samples_split': [2, 5, 10],   # Jumlah minimum sampel untuk memisahkan node
}

# Inisialisasi model dan GridSearchCV
rf = RandomForestClassifier(random_state=42)
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)

# Lakukan pencarian
grid_search.fit(X, y)

print("\n--- Hasil GridSearchCV ---")
print(f"Parameter terbaik: {grid_search.best_params_}")
print(f"Skor akurasi terbaik: {grid_search.best_score_:.4f}")

# ----------------------------------------------------------------------------------
# 3. Validasi Model dengan Cross-Validation
# ----------------------------------------------------------------------------------

print("\nMelakukan validasi silang (cross-validation) untuk model terbaik...")
best_model = grid_search.best_estimator_
cv_scores = cross_val_score(best_model, X, y, cv=5, n_jobs=-1)

print(f"Skor akurasi cross-validation (5-fold): {cv_scores}")
print(f"Rata-rata akurasi cross-validation: {np.mean(cv_scores):.4f}")

# ----------------------------------------------------------------------------------
# 4. Menyimpan Model Baru
# ----------------------------------------------------------------------------------

print("\nMenyimpan model terbaik dan imputer...")
joblib.dump(best_model, 'best_model.pkl')
joblib.dump(imputer, 'imputer_improved.pkl')

print("Model dan imputer baru berhasil disimpan.")
print("### Proses Penyempurnaan Selesai ###")