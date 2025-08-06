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

## Gambaran Umum

**Possibility of Falling in Love** adalah aplikasi berbasis **Flask** dan **Machine Learning** yang dikembangkan untuk memprediksi kemungkinan kecocokan romantis berdasarkan data dari *Speed Dating Experiment*.

Proyek ini tidak hanya berfokus pada akurasi model, tetapi juga pada pengalaman pengguna yang unik, interaktif, dan informatif.

---

## Struktur Proyek

Berikut adalah arsitektur folder dan file yang membentuk proyek ini:

- [possibility-of-falling-in-love/](https://github.com/zerocool979/possibility-of-falling-in-love)
  - `./app.py` – Backend Flask & logic prediksi utama
  - `./improve_model.py` – Script untuk data preprocessing dan tuning model
  - `./best_model.pkl` – Model RandomForestClassifier yang telah dioptimalkan
  - `imputer_improved.pkl` – Objek Imputer untuk menangani missing values
  - `./feedback.log` – Log untuk menyimpan umpan balik dari pengguna
  - `./Speed-Dating-Data.csv` – Dataset asli yang digunakan
- [templates](./templates/)
  - `./index.html` – Halaman antarmuka pengguna (UI)

---

## Fitur-fitur Unggulan

Proyek ini dibangun dengan serangkaian fitur yang membuatnya fungsional, akurat, dan menarik.

### Model & Data
- ✅   **Model Terbaik**: Menggunakan `RandomForestClassifier` yang telah di-*tune* untuk akurasi optimal.
- ✅   **Data Lengkap**: Selain data preferensi, model juga mempertimbangkan fitur-fitur penting seperti `imprace`, `imprelig`, dan `go_out`.
- ✅   **Optimasi Otomatis**: Dilatih menggunakan `GridSearchCV` untuk menemukan *hyperparameter* terbaik secara sistematis.

### Antarmuka Pengguna (UI)
- ✅   **Desain Modern**: Antarmuka web yang bersih, responsif, dan mudah digunakan.
- ✅   **Formulir Multi-Langkah**: Input dibagi menjadi beberapa bagian untuk pengalaman yang intuitif dan tidak membosankan.
- ✅   **Visualisasi Interaktif**:
    - **Progress Bar**: Menampilkan probabilitas kecocokan secara visual.
    - **Diagram Batang**: Menunjukkan 3 faktor terpenting yang memengaruhi prediksi secara keseluruhan.
- ✅   **Sistem Umpan Balik**: Fitur unik yang memungkinkan pengguna memberikan *feedback* tentang akurasi prediksi, yang datanya disimpan sebagai log untuk pengembangan di masa depan.

---

## Cara Menjalankan Secara Lokal

1.  Clone repository ini ke komputer kamu:
    ```bash
    git clone [https://github.com/zerocool979/possibility-of-falling-in-love.git](https://github.com/zerocool979/possibility-of-falling-in-love.git)
    cd possibility-of-falling-in-love
    ```

2.  Pastikan semua dependensi sudah terinstall. Jika belum, kamu bisa menginstal library yang diperlukan:
    ```bash
    pip install pandas scikit-learn Flask
    ```

3.  Jalankan *script* untuk melatih model yang optimal:
    ```bash
    python improve_model.py
    ```

4.  Setelah model selesai dilatih dan disimpan, jalankan server Flask:
    ```bash
    python app.py
    ```

5.  Buka browser web kamu dan akses:
    ```
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
    ```

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