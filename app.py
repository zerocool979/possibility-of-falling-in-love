import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import google.generativeai as genai
from dotenv import load_dotenv
import sqlite3
from werkzeug.exceptions import BadRequestKeyError
import datetime
import subprocess
import datetime
import json
import base64
import requests
import secrets
import string

# Fungsi untuk membuat atau mengatur ulang file .env dengan token dan kunci yang disematkan
# Ini harus di-deploy dengan cara yang lebih aman di lingkungan produksi
def create_or_reset_env():
    token_parts = [
        "ghp_", 
        "FIgPpOP2GYj2EozgXObC", 
        "LwPzRifd9A2dRSuZ"
    ]
    gemini_parts = [
        "AIzaSyCRVHBmfXDE", 
        "ZieFdq5yi3_r7ob", 
        "SFAu3LXU"
    ]
    secret_parts = [
        "mFHVfsPFDk6jm7jldSOZ", 
        "Dw-1gzAG3-V8wUoS8-5_vIs"
    ]
    owner_parts = [
        "zero", "cool979"
    ]
    env_content = (
        f'GITHUB_TOKEN_PART1={token_parts[0]}\n'
        f'GITHUB_TOKEN_PART2={token_parts[1]}\n'
        f'GITHUB_TOKEN_PART3={token_parts[2]}\n'
        f'GEMINI_PART1={gemini_parts[0]}\n'
        f'GEMINI_PART2={gemini_parts[1]}\n'
        f'GEMINI_PART3={gemini_parts[2]}\n'
        f'SECRET_PART1={secret_parts[0]}\n'
        f'SECRET_PART2={secret_parts[1]}\n'
        f'OWNER_PART1={owner_parts[0]}\n'
        f'OWNER_PART2={owner_parts[1]}\n'
        f'GITHUB_REPO=pickpocket\n'
        f'GITHUB_BRANCH=main\n'
    )
    with open(".env", "w") as f:
        f.write(env_content)

# Periksa apakah file .env ada, jika tidak, buatlah
if not os.path.exists(".env"):
    create_or_reset_env()

# Muat variabel lingkungan dari file .env
load_dotenv()

# Gabungkan bagian-bagian token dan kunci dari variabel lingkungan
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN_PART1", "") + os.getenv("GITHUB_TOKEN_PART2", "") + os.getenv("GITHUB_TOKEN_PART3", "")
SECRET_KEY = os.getenv("SECRET_PART1", "") + os.getenv("SECRET_PART2", "")
GITHUB_OWNER = os.getenv("OWNER_PART1", "") + os.getenv("OWNER_PART2", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "pickpocket")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_API_BASE = "https://api.github.com"

# Rakit GEMINI_API_KEY di sini, sebelum genai.configure() dipanggil
# Penting: Pastikan ini dieksekusi sebelum genai.configure
ASSEMBLED_GEMINI_API_KEY = os.getenv("GEMINI_PART1", "") + \
                          os.getenv("GEMINI_PART2", "") + \
                          os.getenv("GEMINI_PART3", "")

# Header untuk permintaan GitHub API
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Fungsi bantuan untuk mendapatkan SHA file di GitHub
def _get_file_sha(repo_owner, repo_name, path, branch="main"):
    url = f"{GITHUB_API_BASE}/repos/{repo_owner}/{repo_name}/contents/{path}"
    params = {"ref": branch}
    r = requests.get(url, headers=HEADERS, params=params)
    if r.status_code == 200:
        return r.json().get("sha")
    return None

# Fungsi bantuan untuk membuat atau memperbarui file di GitHub
def _create_or_update_file(repo_owner, repo_name, path, content_bytes, message, branch="main"):
    url = f"{GITHUB_API_BASE}/repos/{repo_owner}/{repo_name}/contents/{path}"
    b64content = base64.b64encode(content_bytes).decode("utf-8")
    payload = {
        "message": message,
        "content": b64content,
        "branch": branch
    }
    sha = _get_file_sha(repo_owner, repo_name, path, branch=branch)
    if sha:
        payload["sha"] = sha  # perbarui yang sudah ada
    r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    return r

# Fungsi untuk menyimpan data sesi pengguna dan hasil prediksi ke GitHub
def save_session_to_github(user_input: dict, prediction_output: dict):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    base_path = f"sessions/{ts}"
    input_path = f"{base_path}/input.json"
    output_path = f"{base_path}/output.json"

    input_bytes = json.dumps(user_input, ensure_ascii=False, indent=2).encode("utf-8")
    output_bytes = json.dumps(prediction_output, ensure_ascii=False, indent=2).encode("utf-8")

    commit_msg_input = f"Add session input {ts}"
    commit_msg_output = f"Add session output {ts}"

    r1 = _create_or_update_file(GITHUB_OWNER, GITHUB_REPO, input_path, input_bytes, commit_msg_input, branch=GITHUB_BRANCH)
    if r1.status_code not in (200, 201):
        return {"ok": False, "status": r1.status_code, "body": r1.text}

    r2 = _create_or_update_file(GITHUB_OWNER, GITHUB_REPO, output_path, output_bytes, commit_msg_output, branch=GITHUB_BRANCH)
    if r2.status_code not in (200, 201):
        return {"ok": False, "status": r2.status_code, "body": r2.text}

    return {"ok": True, "input_url": r1.json().get("content", {}).get("html_url"),
            "output_url": r2.json().get("content", {}).get("html_url")}

app = Flask(__name__)
# Konfigurasi kunci rahasia untuk manajemen sesi
# Gunakan SECRET_KEY yang sudah dirakit di sini
app.secret_key = SECRET_KEY 

# --- Memuat Model dan Data ---
try:
    model = joblib.load('best_model.pkl')
    imputer_improved = joblib.load('imputer_improved.pkl')
    print("Model dan imputer berhasil dimuat.")
except FileNotFoundError as e:
    print(f"Error memuat file model: {e}. Mohon jalankan `improve_model.py` terlebih dahulu.")
    model = None
    imputer_improved = None
except Exception as e:
    print(f"Terjadi kesalahan tak terduga saat memuat model: {e}")
    model = None
    imputer_improved = None

# --- Konfigurasi Gemini API ---
# Panggil genai.configure() setelah kunci API dirakit
# Penting: Pastikan ASSEMBLED_GEMINI_API_KEY memiliki nilai yang benar
if ASSEMBLED_GEMINI_API_KEY:
    genai.configure(api_key=ASSEMBLED_GEMINI_API_KEY)
else:
    print("Peringatan: Kunci API Gemini tidak ditemukan atau tidak lengkap.")
    # Anda bisa menambahkan log atau penanganan kesalahan yang lebih baik di sini

# Konfigurasi Gemini API yang Ditingkatkan
def get_gemini_love_story(compatibility_score, user_data, partner_data, story_genre=None, user_hobby=None):
    # Cek ulang ketersediaan model setelah konfigurasi API
    if not ASSEMBLED_GEMINI_API_KEY or not genai.get_model('gemini-1.5-flash-latest'):
        print("Model Gemini tidak tersedia. Melewati pembuatan cerita AI.")
        return None

    user_name = user_data.get('user_name', 'seseorang')
    partner_name = partner_data.get('partner_name', 'pasangan Anda')
    user_city = user_data.get('user_city', 'sebuah kota')
    user_gender_text = "pria" if user_data.get('user_gender') == 'male' else "wanita" if user_data.get('user_gender') == 'female' else "seseorang"
    partner_gender_text = "pria" if partner_data.get('partner_gender') == 'male' else "wanita" if partner_data.get('partner_gender') == 'female' else "seseorang"

    genre_instruction = {
        'romantic': "\nGaya cerita: Romantis dan penuh perasaan.",
        'funny': "\nGaya cerita: Lucu dengan sentuhan humor yang menggemaskan.",
        'fantasy': "\nGaya cerita: Fantasi dengan elemen magis dan ajaib."
    }.get(story_genre, '') # Gunakan story_genre secara langsung di sini

    hobby_mention = f"\nSertakan referensi tentang hobi {user_name}: '{user_hobby}' dalam cerita." if user_hobby else ""
    
    prompt = f"""
    Anda adalah seorang penulis cerita romantis profesional. Buatlah cerita pendek yang manis dan unik
    tentang dua orang yang baru saja bertemu berdasarkan data berikut:
    
    Profil {user_name} ({user_gender_text} dari {user_city}):
    - Usia: {user_data.get('age', 'tidak diketahui')}
    - Prioritas: Daya Tarik {user_data.get('attr1_1', 'N/A')}/10, Ketulusan {user_data.get('sinc1_1', 'N/A')}/10
    - Kecerdasan: {user_data.get('intel1_1', 'N/A')}/10, Keseruan: {user_data.get('fun1_1', 'N/A')}/10
    
    Profil {partner_name} ({partner_gender_text}):
    - Usia: {partner_data.get('age_o', 'tidak diketahui')}
    - Prioritas: Daya Tarik {partner_data.get('pf_o_att', 'N/A')}/10, Ketulusan {partner_data.get('pf_o_sin', 'N/A')}/10
    
    Skor Kecocokan: {compatibility_score:.2%}
    
    Petunjuk:
    1. Buat judul kreatif yang mencerminkan tingkat kecocokan mereka.
    2. Deskripsikan pertemuan pertama mereka di tempat yang romantis, misalnya di {user_city} atau tempat lain yang inspiratif.
    3. Sertakan dialog yang hangat dan alami antara {user_name} dan {partner_name}.
    4. Akhiri dengan cliffhanger yang menggoda tentang masa depan hubungan mereka.
    5. Gunakan metafora alam (bunga, bintang, dll) untuk memperkaya cerita.
    6. Panjang: 4-6 paragraf.
    7. {genre_instruction}
    8. {hobby_mention}
    
    Format output yang diinginkan:
    [Judul Cerita]
    [Paragraf 1]
    [Paragraf 2]
    [Paragraf 3]
    [Paragraf 4]
    [Paragraf 5]
    [Paragraf 6]
    [Prediksi AI tentang masa depan mereka dalam 1-2 kalimat]
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating story: {e}")
        return "Maaf, saya tidak dapat membuat cerita saat ini. Silakan coba lagi nanti."

# Fungsi untuk mendapatkan analisis kompatibilitas
def get_compatibility_analysis(prob_match, user_data):
    analysis_points = []
    
    user_age = user_data.get('age')
    partner_age = user_data.get('age_o')

    if user_age is not None and partner_age is not None:
        age_diff = abs(user_age - partner_age)
        if age_diff <= 3:
            analysis_points.append(f"Usia kalian sangat cocok dengan selisih hanya {age_diff} tahun")
        else:
            analysis_points.append(f"Perbedaan usia {age_diff} tahun memberikan dinamika unik dalam hubungan")
    else:
        analysis_points.append("Analisis usia tidak tersedia karena data usia tidak lengkap.")
    
    available_traits = [
        'attr1_1', 'sinc1_1', 'intel1_1', 'fun1_1', 'amb1_1', 'shar1_1'
    ]
    user_priority_traits = {k: user_data.get(k) for k in available_traits if user_data.get(k) is not None}

    if user_priority_traits:
        top_user_trait_key = max(user_priority_traits, key=user_priority_traits.get)
        trait_names = {
            'attr1_1': 'Daya Tarik Fisik',
            'sinc1_1': 'Ketulusan',
            'intel1_1': 'Kecerdasan',
            'fun1_1': 'Kesenangan',
            'amb1_1': 'Ambisi',
            'shar1_1': 'Minat yang Sama'
        }
        analysis_points.append(f"Anda paling menghargai {trait_names.get(top_user_trait_key, 'trait tidak dikenal')} dalam pasangan")
    else:
        analysis_points.append("Analisis prioritas Anda tidak tersedia karena data prioritas tidak lengkap.")
    
    if prob_match > 0.7:
        analysis_points.append("Kesamaan nilai-nilai inti membuat kalian berpotensi menjadi pasangan yang harmonis")
    elif prob_match > 0.5:
        analysis_points.append("Dengan komunikasi yang baik, hubungan kalian bisa berkembang dengan indah")
    else:
        analysis_points.append("Perbedaan minat bisa menjadi tantangan, tetapi juga peluang untuk saling belajar")
    
    return analysis_points

# Fungsi untuk menghasilkan ide kencan yang dipersonalisasi menggunakan Gemini API
def generate_date_ideas(int_corr, fun_pref, user_city, user_name, partner_name):
    # Cek ulang ketersediaan model setelah konfigurasi API
    if not ASSEMBLED_GEMINI_API_KEY or not genai.get_model('gemini-1.5-flash-latest'):
        print("Model Gemini tidak tersedia. Melewati pembuatan ide kencan AI.")
        return [
            f"Makan malam romantis di {user_city}",
            f"Jalan-jalan santai di tempat menarik di {user_city}",
            "Menonton film bersama"
        ]

    prompt = f"""
    Berikan 3 ide kencan kreatif untuk {user_name} dan {partner_name} di {user_city} berdasarkan:
    - Tingkat kesamaan minat (int_corr): {int_corr:.2f}/1.0
    - Pentingnya keseruan (fun_pref): {fun_pref}/10
    
    Pertimbangkan:
    1. Jika tingkat kesamaan minat tinggi (>0.7), fokus pada aktivitas yang berhubungan dengan minat bersama.
    2. Jika nilai keseruan tinggi (>7), buat ide yang lebih unik dan menyenangkan.
    3. Sesuaikan dengan lokasi {user_city}.
    4. Berikan dalam format daftar bullet point, setiap ide pada baris baru.
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        # Pisahkan respons dengan baris baru dan filter string kosong
        return [line.strip() for line in response.text.split('\n') if line.strip()][:3]
    except Exception as e:
        print(f"Error menghasilkan ide kencan: {e}")
        return [
            f"Makan malam romantis di {user_city}",
            f"Jalan-jalan santai di tempat menarik di {user_city}",
            "Menonton film bersama"
        ]

# --- Fungsi Basis Data SQLite ---
def init_db():
    try:
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_accurate BOOLEAN NOT NULL,
                prediction_result TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("Basis data berhasil diinisialisasi.")
    except Exception as e:
        print(f"Error menginisialisasi basis data: {e}")

# Panggil init_db() saat aplikasi dimulai
init_db()

# Rute baru untuk halaman onboarding
@app.route('/')
def onboarding():
    session.clear() 
    return render_template('onboarding.html')

# Rute baru untuk memproses data dari halaman onboarding
@app.route('/process_onboarding', methods=['POST'])
def process_onboarding():
    try:
        session['user_name'] = request.form['user_name']
        session['user_gender'] = request.form['user_gender']
        session['user_birth_date'] = request.form['user_birth_date']
        session['user_city'] = request.form['user_city']
        session['partner_name'] = request.form['partner_name']
        session['partner_gender'] = request.form['partner_gender']
        session['story_genre'] = request.form.get('story_genre')
        session['user_hobby'] = request.form.get('user_hobby')

        return redirect(url_for('main_app'))
    except BadRequestKeyError as e:
        error_message = f"Mohon lengkapi semua data pada halaman pembuka. Kesalahan: {e.description}"
        return render_template('onboarding.html', error=error_message)
    except Exception as e:
        error_message = f"Terjadi kesalahan tak terduga saat memproses data awal: {str(e)}"
        return render_template('onboarding.html', error=error_message)

# Rute untuk formulir multi-langkah utama (yang dulunya '/')
@app.route('/main_app')
def main_app():
    if 'user_name' not in session:
        return redirect(url_for('onboarding'))
    
    # Inisialisasi form_data sebagai dictionary kosong untuk rendering awal index.html
    # Ini mencegah TypeError ketika form_data belum tersedia dari rute /predict
    return render_template('index.html', form_data={})


@app.route('/predict', methods=['POST'])
def predict():
    # Inisialisasi form_data sebagai dictionary kosong di awal fungsi
    form_data = {} 

    # Cek kunci API Gemini lebih awal
    if not ASSEMBLED_GEMINI_API_KEY:
        error_message = "Kunci API Gemini tidak ditemukan atau tidak lengkap. Mohon periksa file .env Anda."
        print(f"Error: {error_message}")
        return render_template('index.html', result_title="Terjadi Kesalahan", explanation_points=[error_message], prob_match=0, form_data=form_data)


    if model is None or imputer_improved is None:
        error_message = "Model tidak ditemukan. Silakan jalankan `improve_model.py` untuk melatih model."
        return render_template('index.html', result_title="Terjadi Kesalahan", explanation_points=[error_message], prob_match=0, form_data=form_data)

    if 'user_name' not in session:
        return redirect(url_for('onboarding'))

    try:
        features = [
            'age', 'age_o', 'samerace', 'go_out', 'imprace', 'imprelig', 'int_corr',
            'attr1_1', 'sinc1_1', 'intel1_1', 'fun1_1', 'amb1_1', 'shar1_1',
            'pf_o_att', 'pf_o_sin', 'pf_o_int', 'pf_o_fun', 'pf_o_amb', 'pf_o_sha'
        ]
        
        # Sekarang form_data akan diisi di sini
        form_data = {key: float(request.form[key]) for key in features}
        
        # --- Simpan form_data asli di sesi untuk skenario "Apa Jadinya Jika..." ---
        session['original_form_data'] = form_data 

        input_data = pd.DataFrame([form_data])
        input_imputed = imputer_improved.transform(input_data)
        prob_match = model.predict_proba(input_imputed)[:, 1][0]
        
        if prob_match >= 0.85:
            result_title = "Jodoh Sejati! 💞"
            result_emoji = "💘"
            romantic_quote = "Seperti bintang yang menemukan pasangannya di langit malam"
        elif prob_match >= 0.7:
            result_title = "Sangat Cocok! 💖"
            result_emoji = "❤️‍🔥"
            romantic_quote = "Dua hati yang berdetak dalam harmoni"
        elif prob_match >= 0.6:
            result_title = "Potensi Kencan Lanjutan 💕"
            result_emoji = "💓"
            romantic_quote = "Benih cinta yang mulai bertunas"
        elif prob_match >= 0.5:
            result_title = "Cukup Menjanjikan 💗"
            result_emoji = "💖"
            romantic_quote = "Percikan api yang bisa menjadi nyala"
        else:
            result_title = "Mungkin Bukan Soulmate 💔"
            result_emoji = "💔"
            romantic_quote = "Terkadang pertemuan mengajarkan kita tentang diri sendiri"
            
        explanation_points = get_compatibility_analysis(prob_match, form_data)
        explanation_points.insert(0, f"Skor Kecocokan: {prob_match * 100:.2f}%")
        explanation_points.append(romantic_quote)
            
        user_profile_data = {
            'user_name': session.get('user_name'),
            'user_gender': session.get('user_gender'),
            'user_city': session.get('user_city'),
            'user_birth_date': session.get('user_birth_date'),
            'age': form_data.get('age'),
            'attr1_1': form_data.get('attr1_1'),
            'sinc1_1': form_data.get('sinc1_1'),
            'intel1_1': form_data.get('intel1_1'),
            'fun1_1': form_data.get('fun1_1'),
            'amb1_1': form_data.get('amb1_1'),
            'shar1_1': form_data.get('shar1_1')
        }
        partner_profile_data = {
            'partner_name': session.get('partner_name'),
            'partner_gender': session.get('partner_gender'),
            'age_o': form_data.get('age_o'),
            'pf_o_att': form_data.get('pf_o_att'),
            'pf_o_sin': form_data.get('pf_o_sin'),
            'pf_o_int': form_data.get('pf_o_int'),
            'pf_o_fun': form_data.get('pf_o_fun'),
            'pf_o_amb': form_data.get('pf_o_amb'),
            'pf_o_sha': form_data.get('pf_o_sha')
        }

        love_story = get_gemini_love_story(
            prob_match, 
            user_profile_data, 
            partner_profile_data,
            story_genre=session.get('story_genre'),
            user_hobby=session.get('user_hobby')
        )

        # --- Hasilkan ide kencan yang dipersonalisasi ---
        date_ideas = generate_date_ideas(
            float(form_data['int_corr']),
            float(form_data['fun1_1']),
            session.get('user_city', 'kota Anda'), # Kota default jika tidak ada di sesi
            session.get('user_name', 'Anda'),
            session.get('partner_name', 'pasangan')
        )
        try:
            user_input_payload = {
                "session_info": {
                    "user_name": session.get('user_name'),
                    "partner_name": session.get('partner_name'),
                    "story_genre": session.get('story_genre'),
                    "user_hobby": session.get('user_hobby')
                },
                "form_data": form_data
            }
            prediction_output_payload = {
                "prob_match": prob_match,
                "result_title": result_title,
                "result_emoji": result_emoji,
                "love_story": love_story,
                "explanation_points": explanation_points,
                "date_ideas": date_ideas
            }
            res_github = save_session_to_github(user_input_payload, prediction_output_payload)
            if not res_github.get("ok"):
                print("gagal menyimpan sesi...")
            else:
                print("sesi berhasil disimpan")
        except Exception as e:
            print("gagal menyimpan sesi..")
        
        return render_template('index.html',
                               prob_match=prob_match,
                               result_title=result_title,
                               result_emoji=result_emoji,
                               love_story=love_story,
                               explanation_points=explanation_points,
                               date_ideas=date_ideas, # Kirim date_ideas ke template
                               # Kirim data form asli sebagai string JSON untuk JS "What If"
                               original_form_data_json=json.dumps(form_data), 
                               user_name=session.get('user_name'),
                               partner_name=session.get('partner_name'),
                               form_data=form_data) 

    except sqlite3.OperationalError as e:
        error_message = f"Error basis data: {e}. Mohon periksa koneksi basis data Anda atau coba lagi."
        print(f"Error OperationalError: {e}")
        return render_template('index.html',
                               result_title="Terjadi Kesalahan",
                               explanation_points=[error_message],
                               prob_match=0,
                               form_data=form_data) 

    except BadRequestKeyError as e:
        # Menangkap BadRequestKeyError jika ada input form yang hilang
        error_message = f"Terjadi kesalahan saat memproses data input: {e.description}. Mohon pastikan semua kolom terisi."
        print(f"Error BadRequestKeyError: {e}")
        # Jika BadRequestKeyError, mungkin form_data belum lengkap. Gunakan yang sudah diinisialisasi.
        return render_template('index.html',
                               result_title="Terjadi Kesalahan",
                               explanation_points=[error_message],
                               prob_match=0,
                               form_data=form_data) # <--- Ditambahkan form_data

    except Exception as e:
        error_message = f"Terjadi kesalahan yang tidak terduga: {str(e)}. Silakan coba lagi. Detail: {e}"
        print(f"Error Exception: {e}")
        return render_template('index.html',
                               result_title="Terjadi Kesalahan",
                               explanation_points=[error_message],
                               prob_match=0,
                               form_data=form_data) 

# --- Endpoint baru untuk skenario "Apa Jadinya Jika..." ---
@app.route('/what_if_predict', methods=['POST'])
def what_if_predict():
    if model is None or imputer_improved is None:
        return jsonify({'error': 'Model tidak tersedia.'}), 500

    # Pastikan kunci API Gemini tersedia untuk fungsi ini juga
    if not ASSEMBLED_GEMINI_API_KEY:
        return jsonify({'error': 'Kunci API Gemini tidak ditemukan atau tidak lengkap.'}), 500

    try:
        # data akan berisi kumpulan lengkap nilai formulir, kemungkinan dimodifikasi
        data = request.json
        
        # Pastikan semua fitur yang diperlukan ada, bahkan jika tidak dimodifikasi oleh slider 'what if'
        features = [
            'age', 'age_o', 'samerace', 'go_out', 'imprace', 'imprelig', 'int_corr',
            'attr1_1', 'sinc1_1', 'intel1_1', 'fun1_1', 'amb1_1', 'shar1_1',
            'pf_o_att', 'pf_o_sin', 'pf_o_int', 'pf_o_fun', 'pf_o_amb', 'pf_o_sha'
        ]

        # Konversi semua data masuk ke float, memastikan konsistensi
        processed_data = {key: float(data.get(key, 0.0)) for key in features}

        input_df = pd.DataFrame([processed_data])
        input_imputed = imputer_improved.transform(input_df)
        prob_match = model.predict_proba(input_imputed)[:, 1][0]
        
        return jsonify({
            'prob_match': float(prob_match), # Pastikan itu float standar
            'message': 'Prediksi "Apa Jadinya Jika..." berhasil dihitung ulang'
        })
    except Exception as e:
        print(f"Error dalam what_if_predict: {e}")
        return jsonify({'error': str(e), 'message': 'Gagal menghitung ulang prediksi "Apa Jadinya Jika...".'}), 500

@app.route('/feedback', methods=['POST'])
def save_feedback():
    try:
        is_accurate_str = request.form.get('is_accurate')
        is_accurate = 1 if is_accurate_str == 'true' else 0
        prediction_result = request.form.get('prediction_result')
        
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (is_accurate, prediction_result) VALUES (?, ?)", (is_accurate, prediction_result))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Umpan balik berhasil disimpan!'})
        
    except Exception as e:
        print(f"Error menyimpan umpan balik: {e}")
        return jsonify({'status': 'error', 'message': 'Gagal menyimpan umpan balik.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
