from flask import Flask, render_template, request
import joblib
import numpy as np

app = Flask(__name__)

# Memuat model, imputer, dan list fitur
model = joblib.load('best_model.pkl')
imputer = joblib.load('imputer_improved.pkl')

# Daftar fitur yang digunakan saat melatih model
features = [
    'int_corr', 'age', 'age_o', 'samerace', 'pf_o_att', 'pf_o_sin', 
    'pf_o_int', 'pf_o_fun', 'pf_o_amb', 'pf_o_sha', 'attr1_1', 'sinc1_1', 
    'intel1_1', 'fun1_1', 'amb1_1', 'shar1_1',
    # New features added
    'imprace', 'imprelig', 'go_out'
]

# Ambil bobot fitur dari model untuk penjelasan
feature_importances = model.feature_importances_
important_features_idx = np.argsort(feature_importances)[::-1]
important_features = [features[i] for i in important_features_idx[:3]] # Ambil 3 teratas

# Definisi halaman utama
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Ambil data dari formulir
        form_data = {key: float(request.form[key]) for key in features}
        input_data = np.array([list(form_data.values())])
        imputed_input = imputer.transform(input_data)
        
        # Lakukan prediksi
        prediction = model.predict(imputed_input)
        prediction_proba = model.predict_proba(imputed_input)[0]

        # --- Bagian Baru: Membuat Penjelasan yang Lebih Dinamis ---
        
        # Tentukan judul hasil
        result_title = ""
        prob_match = prediction_proba[1]
        if prediction[0] == 1:
            result_title = f"Hasil Analisis: Kemungkinan Kecocokan Tinggi"
        else:
            result_title = f"Hasil Analisis: Kemungkinan Kecocokan Rendah"

        # Buat list poin-poin penjelasan
        explanation_points = []
        
        explanation_points.append(f"**Probabilitas Kecocokan:** {prob_match * 100:.2f}%")
        
        # Penjelasan berdasarkan faktor terpenting dari model
        explanation_points.append(f"**Faktor Paling Berpengaruh (berdasarkan model):**")
        for feature_name in important_features:
            # Ganti nama fitur menjadi lebih mudah dibaca
            readable_name = feature_name.replace('_', ' ').replace('pf o ', 'preferensi pasangan untuk ').replace('1 1', 'anda untuk')
            explanation_points.append(f"- {readable_name.title()}")

        # Analisis input pengguna secara personal
        explanation_points.append(f"**Analisis Input Anda:**")
        
        # 1. Korelasi Minat (int_corr)
        int_corr_val = form_data['int_corr']
        if int_corr_val >= 0.6:
            explanation_points.append(f"- **Korelasi Minat:** Nilai korelasi minat Anda ({int_corr_val}) sangat tinggi, menunjukkan kesamaan yang kuat. Ini adalah faktor pendorong kecocokan yang sangat positif.")
        else:
            explanation_points.append(f"- **Korelasi Minat:** Nilai korelasi minat Anda ({int_corr_val}) cenderung rendah, yang bisa menjadi hambatan. Mencari hobi baru bersama dapat membantu.")

        # 2. Preferensi yang Selaras (contoh: daya tarik fisik)
        user_att_pref = form_data['attr1_1']
        partner_att_pref = form_data['pf_o_att']
        if abs(user_att_pref - partner_att_pref) <= 2:
            explanation_points.append(f"- **Daya Tarik Fisik:** Preferensi Anda ({user_att_pref}) dan calon pasangan ({partner_att_pref}) cukup selaras, menunjukkan pandangan yang serupa tentang pentingnya hal ini.")
        else:
            explanation_points.append(f"- **Daya Tarik Fisik:** Ada perbedaan besar dalam preferensi daya tarik fisik Anda ({user_att_pref}) dan calon pasangan ({partner_att_pref}).")

        # 3. Faktor Usia
        age_diff = abs(form_data['age'] - form_data['age_o'])
        if age_diff <= 5:
            explanation_points.append(f"- **Perbedaan Usia:** Perbedaan usia ({age_diff} tahun) tergolong kecil, yang seringkali mempermudah komunikasi dan kesamaan pengalaman hidup.")
        else:
            explanation_points.append(f"- **Perbedaan Usia:** Perbedaan usia ({age_diff} tahun) cukup signifikan, yang mungkin mempengaruhi dinamika hubungan.")

        return render_template('index.html', result_title=result_title, explanation_points=explanation_points)

    except Exception as e:
        error_message = f"Terjadi kesalahan: {e}. Pastikan semua input diisi dengan benar."
        return render_template('index.html', result_title="Terjadi Kesalahan", explanation_points=[error_message])

if __name__ == '__main__':
    app.run(debug=True)
