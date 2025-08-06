from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import joblib
import numpy as np
import datetime
import sqlite3
import google.generativeai as genai

app = Flask(__name__)

load_dotenv()
api_key = os.getenv("GENAI_API_KEY")

# --- Inisialisasi Database SQLite ---
def init_db():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  prediction TEXT,
                  accurate TEXT,
                  user_agent TEXT,
                  ip_address TEXT)''')
    conn.commit()
    conn.close()

# Memuat model, imputer, dan list fitur
try:
    model = joblib.load('best_model.pkl')
    imputer = joblib.load('imputer_improved.pkl')
    
    features = [
        'int_corr', 'age', 'age_o', 'samerace', 'pf_o_att', 'pf_o_sin', 
        'pf_o_int', 'pf_o_fun', 'pf_o_amb', 'pf_o_sha', 'attr1_1', 'sinc1_1', 
        'intel1_1', 'fun1_1', 'amb1_1', 'shar1_1', 'imprace', 'imprelig', 'go_out'
    ]
    feature_importances = model.feature_importances_
    
    feature_weights = sorted(zip(features, feature_importances), key=lambda x: x[1], reverse=True)
    
except FileNotFoundError:
    print("Error: File model atau imputer tidak ditemukan. Pastikan sudah menjalankan improve_model.py.")
    exit()

# --- Fungsi untuk AI Generatif (Google Gemini) ---
def generate_love_story(form_data, prob_match):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')  # paste model yang kamu pilih disini yaa :)
    
    prompt = f"""
    Buat cerita romantis singkat dalam bahasa Indonesia tentang bagaimana dua orang ini mungkin bertemu dan jatuh cinta,
    mengingat mereka memiliki skor kecocokan sebesar {prob_match*100:.2f}%. Berikut adalah detail mereka:
    - Usia: {form_data['age']} dan {form_data['age_o']}
    - Sifat utama: Pentingnya daya tarik fisik {form_data['attr1_1']}/10, pentingnya kecerdasan {form_data['intel1_1']}/10
    - Nilai kesamaan minat: {form_data['int_corr']}.
    Buat 2-3 paragraf, bernada ringan dan romantis.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ups! Ada masalah dengan AI: {e}"

# --- Fungsi untuk Analisis Personal dan Heatmap ---
feature_labels = {
    'int_corr': 'Korelasi Minat',
    'age_diff': 'Perbedaan Usia',
    'imprace': 'Pentingnya Ras',
    'imprelig': 'Pentingnya Agama',
    'go_out': 'Frekuensi Pergi Keluar'
}

trait_explanations = {
    'att': 'Daya Tarik Fisik', 'sin': 'Ketulusan', 'int': 'Kecerdasan',
    'fun': 'Kesenangan', 'amb': 'Ambisi', 'sha': 'Hobi yang Sama'
}

# Nilai rata-rata dari dataset (harus diganti dengan nilai aktual)
dataset_averages = {
    'int_corr': 0.5,
    'age': 30,
    'age_o': 30,
    'pf_o_att': 6, 'pf_o_sin': 7, 'pf_o_int': 6, 'pf_o_fun': 7,
    'pf_o_amb': 6, 'pf_o_sha': 5, 'attr1_1': 6, 'sinc1_1': 7,
    'intel1_1': 6, 'fun1_1': 7, 'amb1_1': 6, 'shar1_1': 5,
    'imprace': 5, 'imprelig': 5, 'go_out': 5
}

def get_personalized_analysis(feature, value):
    thresholds = {
        'int_corr': (0.7, 0.4),
        'age_diff': (5, 10),
        'imprace': (8, 5),
        'imprelig': (8, 5)
    }
    
    if feature in thresholds:
        high, medium = thresholds[feature]
        # Menggunakan feature_labels yang didefinisikan di luar fungsi
        label = feature_labels.get(feature, feature)
        if feature == 'age_diff':
            if value <= high: return f" - Perbedaan {label} Anda ({value:.0f} tahun) tergolong kecil, yang sering mempermudah komunikasi."
            else: return f" - Perbedaan {label} Anda ({value:.0f} tahun) cukup signifikan, yang mungkin mempengaruhi dinamika hubungan."
        else:
            if value >= high: return f" - Nilai {label} Anda ({value:.0f}) sangat tinggi, menunjukkan ini adalah nilai utama bagi Anda."
            elif value >= medium: return f" - Nilai {label} Anda ({value:.0f}) cukup tinggi, ini adalah faktor yang penting."
    return ""

def generate_heatmap_data(user_traits, partner_prefs):
    traits = ['att', 'sin', 'int', 'fun', 'amb', 'sha']
    heatmap_data = []
    for trait in traits:
        user_score = user_traits.get(f'attr1_1', 0) if trait == 'att' else user_traits.get(f'{trait}1_1', 0)
        partner_pref = partner_prefs.get(f'pf_o_{trait}', 0)
        alignment = 10 - abs(user_score - partner_pref)
        heatmap_data.append({
            'trait': trait_explanations.get(trait, 'N/A'),
            'alignment': alignment,
            'user_score': user_score,
            'partner_pref': partner_pref
        })
    return heatmap_data


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        form_data = {key: float(request.form[key]) for key in features}
        
        user_traits = {f.replace('1_1', ''): form_data[f] for f in features if f.endswith('1_1')}
        partner_prefs = {f.replace('pf_o_', ''): form_data[f] for f in features if f.startswith('pf_o')}
        
        input_data = np.array([list(form_data.values())])
        imputed_input = imputer.transform(input_data)
        
        prediction_proba = model.predict_proba(imputed_input)[0]
        prob_match = prediction_proba[1]

        if prob_match >= 0.9:
            result_title = "💘 Soulmates! Perfect Match Found"
            result_emoji = "💘"
        elif prob_match >= 0.7:
            result_title = "💖 Amazing Connection! High Potential"
            result_emoji = "💖"
        elif prob_match >= 0.5:
            result_title = "✨ Good Potential With Some Effort"
            result_emoji = "✨"
        elif prob_match >= 0.3:
            result_title = "🤔 Possible With Significant Work"
            result_emoji = "🤔"
        else:
            result_title = "⚠️ Challenging Match - Major Differences"
            result_emoji = "⚠️"

        explanation_points = []
        explanation_points.append(f"**Probabilitas Kecocokan:** {prob_match * 100:.2f}%")
        
        age_diff_val = abs(form_data['age'] - form_data['age_o'])
        explanation_points.append(get_personalized_analysis('int_corr', form_data['int_corr']))
        explanation_points.append(get_personalized_analysis('age_diff', age_diff_val))
        explanation_points.append(get_personalized_analysis('imprace', form_data['imprace']))
        explanation_points.append(get_personalized_analysis('imprelig', form_data['imprelig']))

        love_story = generate_love_story(form_data, prob_match)
        heatmap_data = generate_heatmap_data(form_data, form_data)

        return render_template('index.html', result_title=result_title, result_emoji=result_emoji, 
                               explanation_points=explanation_points, prob_match=prob_match, 
                               top_3_features=feature_weights[:3], form_data=form_data,
                               love_story=love_story, heatmap_data=heatmap_data,
                               feature_labels=feature_labels) # <-- BARIS INI YANG DIPERBAIKI

    except Exception as e:
        error_message = f"Terjadi kesalahan: '{e}'. Pastikan semua input diisi dengan benar."
        return render_template('index.html', result_title="Terjadi Kesalahan", explanation_points=[error_message])

@app.route('/feedback', methods=['POST'])
def feedback():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute("INSERT INTO feedback VALUES (NULL, ?, ?, ?, ?, ?)",
             (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              request.form.get('prediction_result'),
              request.form.get('is_accurate'),
              request.headers.get('User-Agent'),
              request.remote_addr))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)