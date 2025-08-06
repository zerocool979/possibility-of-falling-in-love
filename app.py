from flask import Flask, render_template, request, redirect, url_for
import joblib
import numpy as np
import datetime

app = Flask(__name__)

# Memuat model, imputer, dan list fitur
try:
    model = joblib.load('best_model.pkl')
    imputer = joblib.load('imputer_improved.pkl')
    
    # Ambil bobot fitur dari model untuk penjelasan
    features = [
        'int_corr', 'age', 'age_o', 'samerace', 'pf_o_att', 'pf_o_sin', 
        'pf_o_int', 'pf_o_fun', 'pf_o_amb', 'pf_o_sha', 'attr1_1', 'sinc1_1', 
        'intel1_1', 'fun1_1', 'amb1_1', 'shar1_1', 'imprace', 'imprelig', 'go_out'
    ]
    feature_importances = model.feature_importances_
    
    # Gabungkan nama fitur dan bobotnya, lalu urutkan
    feature_weights = sorted(zip(features, feature_importances), key=lambda x: x[1], reverse=True)
    
except FileNotFoundError:
    print("Error: File model atau imputer tidak ditemukan. Pastikan sudah menjalankan improve_model.py.")
    exit()

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

        # --- Membuat Penjelasan yang Lebih Dinamis ---
        result_title = ""
        prob_match = prediction_proba[1]
        
        if prediction[0] == 1:
            result_title = f"Hasil Analisis: Kemungkinan Kecocokan Tinggi"
        else:
            result_title = f"Hasil Analisis: Kemungkinan Kecocokan Rendah"

        explanation_points = []
        explanation_points.append(f"**Probabilitas Kecocokan:** {prob_match * 100:.2f}%")
        
        explanation_points.append(f"**Analisis Input Anda:**")
        
        int_corr_val = form_data['int_corr']
        if int_corr_val >= 0.6:
            explanation_points.append(f"- **Korelasi Minat:** Nilai korelasi minat Anda ({int_corr_val}) sangat tinggi, menunjukkan kesamaan yang kuat.")
        else:
            explanation_points.append(f"- **Korelasi Minat:** Nilai korelasi minat Anda ({int_corr_val}) cenderung rendah, yang bisa menjadi hambatan.")
        
        user_att_pref = form_data['attr1_1']
        partner_att_pref = form_data['pf_o_att']
        if abs(user_att_pref - partner_att_pref) <= 2:
            explanation_points.append(f"- **Daya Tarik Fisik:** Preferensi Anda ({user_att_pref}) dan calon pasangan ({partner_att_pref}) cukup selaras.")
        else:
            explanation_points.append(f"- **Daya Tarik Fisik:** Ada perbedaan besar dalam preferensi daya tarik fisik Anda ({user_att_pref}) dan calon pasangan ({partner_att_pref}).")

        age_diff = abs(form_data['age'] - form_data['age_o'])
        if age_diff <= 5:
            explanation_points.append(f"- **Perbedaan Usia:** Perbedaan usia ({age_diff} tahun) tergolong kecil, yang seringkali mempermudah komunikasi.")
        else:
            explanation_points.append(f"- **Perbedaan Usia:** Perbedaan usia ({age_diff} tahun) cukup signifikan, yang mungkin mempengaruhi dinamika hubungan.")
        
        # Kirim data bobot fitur ke template
        top_3_features = feature_weights[:3]

        return render_template('index.html', result_title=result_title, explanation_points=explanation_points, 
                               prob_match=prob_match, top_3_features=top_3_features, form_data=form_data)

    except Exception as e:
        error_message = f"Terjadi kesalahan: {e}. Pastikan semua input diisi dengan benar."
        return render_template('index.html', result_title="Terjadi Kesalahan", explanation_points=[error_message])

# --- Bagian Baru: Route untuk Umpan Balik ---
@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        is_accurate = request.form.get('is_accurate')
        prediction_result = request.form.get('prediction_result')
        
        # Simpan feedback ke dalam file log
        with open('feedback.log', 'a') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Prediksi: {prediction_result}, Akurat: {is_accurate}\n")

        return redirect(url_for('home'))
        
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return "Terjadi kesalahan saat menyimpan umpan balik.", 500

if __name__ == '__main__':
    app.run(debug=True)