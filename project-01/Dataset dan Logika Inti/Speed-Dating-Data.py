import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
import joblib

# ----------------------------------------------------------------------------------
# 2.2. Memuat dan Membersihkan Dataset
# ----------------------------------------------------------------------------------

print("Memuat dan membersihkan data...")
# Muat dataset
try:
    data = pd.read_csv('Speed-Dating-Data.csv', encoding='latin1')
except UnicodeDecodeError:
    print("Error: Encoding 'utf-8' gagal, mencoba 'latin1'.")
    data = pd.read_csv('Speed-Dating-Data.csv', encoding='latin1')

# Kolom 'match' adalah target kita. Mari kita periksa distribusinya.
print(f"Distribusi target 'match':\n{data['match'].value_counts()}")

# Kita akan fokus pada beberapa fitur utama yang mungkin relevan.
# Fitur-fitur ini mencakup preferensi pribadi, usia, dan etnis.
# Kita juga akan menggunakan 'int_corr' (korelasi minat) yang sudah dihitung di dataset.

# Kolom-kolom yang akan kita gunakan sebagai fitur:
features_to_use = [
    'int_corr',  # Korelasi minat antara dua orang
    'age',       # Usia individu 1
    'age_o',     # Usia individu 2
    'samerace',  # Apakah etnisnya sama (0=tidak, 1=ya)
    'pf_o_att',  # Seberapa penting daya tarik fisik bagi orang lain (partner)
    'pf_o_sin',  # Seberapa penting ketulusan bagi orang lain
    'pf_o_int',  # Seberapa penting kecerdasan bagi orang lain
    'pf_o_fun',  # Seberapa penting kesenangan bagi orang lain
    'pf_o_amb',  # Seberapa penting ambisi bagi orang lain
    'pf_o_sha',  # Seberapa penting hobi yang sama bagi orang lain
    # Kita bisa menambahkan lebih banyak fitur dari kuesioner pribadi jika diperlukan
    'attr1_1', 'sinc1_1', 'intel1_1', 'fun1_1', 'amb1_1', 'shar1_1'
]

# Menghapus baris dengan nilai yang hilang pada kolom target 'match'
data.dropna(subset=['match'], inplace=True)

# Memilih fitur dan target
X = data[features_to_use]
y = data['match']

# Mengatasi nilai yang hilang (missing values)
# Menggunakan SimpleImputer untuk mengisi nilai NaN dengan rata-rata dari kolom
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)
X = pd.DataFrame(X_imputed, columns=X.columns)

# Periksa kembali apakah masih ada NaN
print(f"Jumlah nilai NaN setelah imputasi: {X.isnull().sum().sum()}")

# ----------------------------------------------------------------------------------
# 2.3. Membangun dan Melatih Model Machine Learning
# ----------------------------------------------------------------------------------

print("\nMemisahkan data dan melatih model...")
# Memisahkan data menjadi data pelatihan (training) dan data uji (testing)
# Data pelatihan akan digunakan untuk melatih model, data uji untuk menguji performa
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Menggunakan algoritma RandomForestClassifier
# Ini adalah pilihan yang baik karena efektif untuk banyak kasus dan mudah digunakan
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("Model berhasil dilatih!")

# Menguji performa model (opsional tapi disarankan)
from sklearn.metrics import accuracy_score
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Akurasi model pada data uji: {accuracy * 100:.2f}%")

# ----------------------------------------------------------------------------------
# 2.4. Menyimpan Model untuk Digunakan Nanti
# ----------------------------------------------------------------------------------

print("\nMenyimpan model dan imputer...")
# Simpan model yang sudah dilatih dan imputer
# Imputer diperlukan saat memprediksi data baru agar data input diolah dengan cara yang sama
joblib.dump(model, 'model_prediksi_cinta.pkl')
joblib.dump(imputer, 'imputer_cinta.pkl')

print("Model dan imputer berhasil disimpan.")
print("Sekarang kamu bisa melanjutkan ke Langkah 3 untuk membuat antarmuka program.")
