<p align="center">
  <img src="https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif" width="100%" alt="anime banner">
</p>

<h1 align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&duration=3000&pause=1000&color=FF6F61&center=true&vCenter=true&width=440&lines=Possibility+of+Falling+in+Love...;Mencoba+Memprediksi+Cinta;Dengan+Logika+Machine+Learning" alt="Typing SVG" />
</h1>

<p align="center"><i><strong>Apakah cinta bisa diprediksi dengan data?</strong><br>Temui aplikasi web cerdas berbasis Machine Learning yang mencoba menjawab pertanyaan paling klasik dalam sejarah umat manusia: “Apakah dia juga suka aku?”</i></p>

<p align="center">
  <a href="https://github.com/zerocool979/possibility-of-falling-in-love" target="_blank">
    <img src="https://img.shields.io/badge/Deploy%20Link-Coming%20Soon-blueviolet?style=for-the-badge&logo=vercel" alt="Deploy Link">
  </a>
</p>

---

## Cara Menjalankan Secara Lokal

1.  **Gambaran Umum**
2.  **Struktur Proyek**
3.  **Fitur-fitur Unggulan**
4.  **Prasyarat**
5.  **Cara Menjalankan Secara Lokal**
6.  **Referensi dan Dataset**
7.  **Feedback dan Kontribusi**
8.  **Author**

---

---

## Gambaran Umum

**Possibility of Falling in Love** adalah aplikasi berbasis **Flask** dan **Machine Learning** yang dikembangkan untuk memprediksi kemungkinan kecocokan romantis berdasarkan data dari *Speed Dating Experiment*.

Proyek ini tidak hanya berfokus pada akurasi model, tetapi juga pada pengalaman pengguna yang unik, interaktif, dan informatif, termasuk fitur tambahan berbasis AI dari **Google Gemini** untuk menghasilkan kisah cinta personal.

---

## Struktur Proyek

Berikut adalah arsitektur folder dan file yang membentuk proyek ini:

- [possibility-of-falling-in-love/](https://github.com/zerocool979/possibility-of-falling-in-love)
  - `./.env` – Isi kunci API Google Gemini milik mu  (Tidak boleh di-push ke GitHub!)
  - `./.gitignore` – abaikan file yang tidak perlu di-commit, termasuk .env
  - `./app.py` – Backend Flask & logic prediksi utama
  - `./improve_model.py` – Script untuk data preprocessing dan tuning model
  - `./check_models.py` – Skrip ini buat meriksa model Gemini apa saja yang tersedia (isi kunci API Google Gemini milik mu)
  - `./best_model.pkl` – Model RandomForestClassifier yang telah dioptimalkan
  - `imputer_improved.pkl` – Objek Imputer untuk menangani missing values
  - `./feedback.db` – Database SQLite untuk menyimpan umpan balik pengguna (ngayal udah nge-`deploy`...)
  - `./Speed-Dating-Data.csv` – Dataset asli yang digunakan untuk pelatihan
- [templates](./templates/)
  - `./index.html` – Halaman antarmuka pengguna (UI) utama

  ---

> _"Beberapa file mungkin tidak tersedia dan akan otomatis tersedia jika user mempraktekannya langsung. Hal ini dikarenakan kami ingin user dapat merasakan bagaimana rasanya menggunakan proyek ini secara langsung"_

---

## Fitur-fitur Unggulan

Proyek ini dibangun dengan serangkaian fitur yang membuatnya fungsional, akurat, dan menarik.

### Model & Data
- ✅   **Model Terbaik**: Menggunakan `RandomForestClassifier` yang telah di-*tune* untuk akurasi optimal.
- ✅   **Data Lengkap**: Selain data preferensi, model juga mempertimbangkan fitur-fitur penting seperti `imprace`, `imprelig`, dan `go_out`.
- ✅   **Optimasi Otomatis**: Dilatih menggunakan `GridSearchCV` untuk menemukan *hyperparameter* terbaik secara sistematis.

### Fitur Berbasis AI & Analisis
- ✅   **Cerpen ala-ala AI**: Menggunakan API **Google Gemini** untuk secara kreatif menghasilkan kisah romantis personal berdasarkan data kecocokan dan detail pengguna.
- ✅   **Analisis Personalisasi**: Memberikan analisis mendalam tentang faktor-faktor utama yang paling memengaruhi hasil prediksi.
- ✅   **Visualisasi Keselarasan**: Diagram interaktif yang membandingkan prioritas Anda dengan preferensi pasangan.

### Antarmuka Pengguna (UI)
- ✅   **Desain Modern**: Antarmuka web yang bersih, responsif, dan mudah digunakan.
- ✅   **Formulir Multi-Langkah**: Input dibagi menjadi beberapa bagian untuk pengalaman yang intuitif dan tidak membosankan.
- ✅   **Visualisasi Interaktif**:
    - **Progress Bar**: Menampilkan probabilitas kecocokan secara visual.
    - **Diagram Batang**: Menunjukkan 3 faktor terpenting yang memengaruhi prediksi secara keseluruhan.
- ✅   **Sistem Umpan Balik**: Fitur unik yang memungkinkan pengguna memberikan *feedback* tentang akurasi prediksi, yang datanya disimpan sebagai log untuk pengembangan di masa depan.

---

## Prasyarat
- **Python 3.7+**
- **Gitt** (untuk mengkloning repository)

---

## Cara Menjalankan Secara Lokal

1.  Clone repository ini ke komputer kamu:
    ```bash
    git clone https://github.com/zerocool979/possibility-of-falling-in-love.git
    cd possibility-of-falling-in-love
    ```

2.  Pastikan semua dependensi sudah terinstall. Jika belum, kamu bisa menginstal library yang diperlukan:
    ```bash
    pip install -r requirements.txt
    ```

3.  Konfigurasi API Google Gemini:
  Aplikasi ini perlu kunci API dari Google Gemini untuk fitur cerita AI.
  - Dapatkan kunci API dari (https://aistudio.google.com/app/apikey)
  - Buat file `.env` di direktori utama proyek
  - Paste API yang sudah kamu dapatkan sebelumnya kedalam file `.env`
    ```bash
    GEMINI_API_KEY="YOUR_API_KEY"
    ```
> _"Catatan Keamanan API: File .env sudah diabaikan oleh .gitignore, jadi kunci API aman dan tidak akan terunggah ke GitHub."_

4.  Pelatihan Model:
Jalankan skrip `improve_model.py` untuk melatih model Machine Learning dan menyimpan artefak yang diperlukan (`best_model.pkl` dan `imputer_improved.pkl`):
    ```bash
    python improve_model.py
    ```
> _"Catatan: Langkah ini hanya perlu dilakukan satu kali."_

5.  Menjalankan Server Flask:
Setelah model selesai dilatih dan kunci API sudah dikonfigurasi, jalankan server Flask:
    ```
    python app.py
    ```

6.  Buka browser web kamu dan akses:
    ```
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
    ```

7.  (Opsional) Memeriksa Model Gemini yang Tersedia:
kalo misalnya kam mengalami error kuota atau model tidak ditemukan, kamu bisa menjalankan skrip berikut untuk melihat model yang tersedia untuk API key yang kamu punya:
    ```
    python check_models.py
    ```
> _"Catatan: Ganti variable yang mendefinisikan API pada baris kode **(api_key='paste api keynya disini')**. Setelah mendapatkan list, kamu bisa pilih salah satu modelnya untuk digunakan didalam app.py pada fungsi **generate_love_story(form_data, prob_match)** baris code 50 di variable **model**."_

---

## Referensi dan Dataset

- **Dataset**: [Speed Dating Experiment Data](https://www.kaggle.com/datasets/annavictoria/speed-dating-experiment) dari Kaggle, yang merupakan eksperimen nyata untuk mempelajari faktor-faktor ketertarikan romantis.

---

## Feedback dan Kontribusi

Kami percaya cinta itu dinamis — begitu juga dengan proyek ini!
Sangat terbuka untuk setiap saran, laporan *bug*, atau kontribusi kode. Jangan ragu untuk membuat *Pull Request* atau membuka *Issue*.

Terutama, jangan lupa untuk mengisi formulir umpan balik di halaman web — kami membaca semua umpan balik untuk terus meningkatkan akurasi model .

---

## Author

**zerocool979**
GitHub: [@zerocool979](https://github.com/zerocool979)

---

> _"Machine Learning can’t guarantee true love… but hey, at least it can give you a hint!"_ – someone strange