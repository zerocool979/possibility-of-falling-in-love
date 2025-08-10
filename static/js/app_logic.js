// Enhanced form navigation with animations
let currentTab = 0;
const formSections = document.querySelectorAll('.form-section');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const totalSteps = formSections.length;

// Fungsi untuk menampilkan tab berdasarkan indeks (n)
function showTab(n) {
    // Memperbarui indikator progres
    document.getElementById('current-step').textContent = n + 1;
    document.getElementById('total-steps').textContent = totalSteps; // Pastikan totalSteps di-set di HTML atau di sini
    document.querySelector('.progress-bar').style.width = `${((n + 1) / totalSteps) * 100}%`;
    
    // Sembunyikan semua bagian formulir
    formSections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Tampilkan bagian formulir saat ini
    if (formSections[n]) {
        formSections[n].style.display = 'block';
    }

    // Perbarui status tombol navigasi
    if (n === 0) {
        prevBtn.style.display = 'none';
    } else {
        prevBtn.style.display = 'inline-block';
    }

    if (n === (totalSteps - 1)) {
        nextBtn.innerHTML = '<i class="fas fa-heart"></i> Prediksi';
    } else {
        nextBtn.innerHTML = 'Selanjutnya <i class="fas fa-arrow-right"></i>';
    }
}

// Fungsi untuk validasi formulir
function validateForm() {
    let valid = true;
    const currentInputs = formSections[currentTab].querySelectorAll('input, select');
    for (let i = 0; i < currentInputs.length; i++) {
        if (!currentInputs[i].checkValidity()) {
            currentInputs[i].reportValidity();
            valid = false;
        }
    }
    return valid;
}

// Fungsi untuk navigasi antar tab (sebelumnya/selanjutnya)
function nextPrev(n) {
    if (n === 1 && !validateForm()) return false;

    // Tambahkan animasi keluar untuk tab saat ini
    const currentSection = formSections[currentTab];
    currentSection.classList.add(n === 1 ? 'slide-out-left' : 'slide-out-right');
    
    // Tunggu animasi keluar selesai sebelum melanjutkan
    setTimeout(() => {
        currentSection.style.display = 'none';
        currentSection.classList.remove('slide-out-left', 'slide-out-right');
        
        currentTab += n;
        
        if (currentTab >= totalSteps) {
            // Tampilkan overlay loading sebelum submit form
            document.getElementById('loadingOverlay').style.display = 'flex';
            // Beri sedikit jeda agar animasi loading terlihat sebelum halaman di-reload
            setTimeout(() => {
                document.getElementById('predictionForm').submit();
            }, 500); // Sesuaikan dengan durasi animasi loading
            return false;
        }
        
        // Tampilkan tab berikutnya dengan animasi masuk
        showTab(currentTab);
        const nextSection = formSections[currentTab];
        nextSection.classList.add(n === 1 ? 'slide-in-right' : 'slide-in-left');
        
        // Hapus kelas animasi masuk setelah selesai
        setTimeout(() => {
            nextSection.classList.remove('slide-in-left', 'slide-in-right');
        }, 600); // Sesuaikan dengan durasi animasi masuk
    }, 500); // Sesuaikan dengan durasi animasi keluar
}


// Fungsi untuk membuat hati mengambang di latar belakang
function createFloatingHearts() {
    const container = document.getElementById('floating-hearts-container'); // Container khusus untuk hati
    if (!container) return; // Pastikan container ada

    const heartIcons = ['❤', '💕', '�', '💗', '💓', '💞'];
    
    for (let i = 0; i < 12; i++) { // Buat 12 hati
        const heart = document.createElement('div');
        heart.className = 'floating-heart';
        heart.innerHTML = heartIcons[Math.floor(Math.random() * heartIcons.length)];
        
        // Atur posisi dan animasi acak
        heart.style.left = `${Math.random() * 100}%`;
        heart.style.top = `${Math.random() * 100}%`;
        heart.style.fontSize = `${20 + Math.random() * 30}px`; // Ukuran acak antara 20px dan 50px
        heart.style.animationDelay = `${Math.random() * 4}s`; // Penundaan acak untuk animasi bertahap
        heart.style.animationDuration = `${8 + Math.random() * 8}s`; // Durasi animasi acak (lebih lambat dan bervariasi)
        heart.style.opacity = 0.3 + Math.random() * 0.5; // Opasitas acak untuk kedalaman
        
        container.appendChild(heart);
    }
}

// Fungsi untuk menganimasikan hati hasil berdasarkan skor kecocokan
function animateHeart(probMatch) {
    const heart = document.querySelector('.heart-progress');
    const heartContainer = document.querySelector('.heart-container'); // Ambil kontainer hati
    if (!heart || !heartContainer) return;
    
    const scale = 0.6 + (probMatch * 0.6); // Skala yang lebih dramatis
    heart.style.transform = `scale(${scale})`;
    
    // Variasi warna berdasarkan skor
    if (probMatch > 0.7) {
        heart.style.color = '#ff1493'; // Merah muda tua untuk kecocokan tinggi
        heartContainer.classList.add('high-compatibility'); // Tambahkan kelas untuk animasi pulse-glow
    } else if (probMatch > 0.5) {
        heart.style.color = '#ff6b8b'; // Warna asli untuk sedang
        heartContainer.classList.remove('high-compatibility');
    } else {
        heart.style.color = '#ffb6c1'; // Merah muda terang untuk rendah
        heartContainer.classList.remove('high-compatibility');
    }
}

// Pastikan skrip ini berjalan setelah DOM dimuat sepenuhnya
document.addEventListener('DOMContentLoaded', () => {
    // Event listeners untuk tombol navigasi
    if (prevBtn) {
        prevBtn.addEventListener('click', () => nextPrev(-1));
    }
    if (nextBtn) {
        nextBtn.addEventListener('click', () => nextPrev(1));
    }

    // Tampilkan tab pertama saat halaman dimuat
    showTab(currentTab);

    // Inisialisasi tampilan nilai slider
    document.querySelectorAll('input[type="range"]').forEach(slider => {
        const valueSpan = document.getElementById(slider.id + '_val');
        if (valueSpan) {
            slider.addEventListener('input', (event) => {
                valueSpan.textContent = event.target.value;
            });
            // Set initial value display on load
            valueSpan.textContent = slider.value;
        }
    });

    // Inisialisasi tooltip
    const tooltipTriggers = document.querySelectorAll('.tooltip-trigger');
    const tooltip = document.getElementById('tooltip');
    
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', (e) => {
            const tooltipText = e.target.getAttribute('data-tooltip');
            tooltip.textContent = tooltipText;
            tooltip.style.opacity = '1';
            
            // Posisi tooltip relatif terhadap trigger
            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = `${rect.right + 10}px`; // Di kanan ikon
            tooltip.style.top = `${rect.top}px`;
        });
        
        trigger.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
        });
    });

    // Panggil fungsi untuk membuat hati mengambang
    createFloatingHearts();
    
    // Animasikan hati hasil jika ada probMatchHidden (artinya ada hasil prediksi)
    const probMatchElement = document.getElementById('probMatchHidden');
    if (probMatchElement) {
        const probMatch = parseFloat(probMatchElement.value);
        if (!isNaN(probMatch)) {
            animateHeart(probMatch);
        }
    }

    // Tangani autoplay audio (jika browser mengizinkan)
    const audio = document.getElementById('audio');
    if (audio) {
        audio.play().catch(e => {
            console.log("Autoplay was prevented. User needs to interact with the page to play audio.");
        });
    }

    // Efek confetti untuk hasil kecocokan tinggi
    if (typeof ConfettiGenerator !== 'undefined') {
        const confettiCanvas = document.getElementById('confetti-canvas');
        if (probMatchElement && confettiCanvas) {
            const probMatch = parseFloat(probMatchElement.value);
            if (probMatch > 0.7) {
                const confettiSettings = {
                    target: 'confetti-canvas',
                    max: 150,
                    size: 1.5,
                    animate: true,
                    props: ['heart', 'circle', 'square'],
                    colors: [[255, 107, 139], [255, 142, 83], [255, 203, 164]],
                    clock: 25,
                    rotate: true,
                    start_from_edge: true,
                    respawn: true
                };
                
                const confetti = new ConfettiGenerator(confettiSettings);
                confetti.render();
                
                setTimeout(() => {
                    confetti.clear();
                }, 8000);
            }
        }
    }

    // Inisialisasi salju (jika ada)
    if (typeof snowStorm !== 'undefined') {
        snowStorm.flakesMax = 128;
        snowStorm.flakesMaxActive = 64;
        snowStorm.use = true; 
        snowStorm.vMaxX = 2;
        snowStorm.vMaxY = 2;
        snowStorm.excludeMobile = true;
        snowStorm.freezeOnBlur = true;
        snowStorm.snowColor = '#ddd';
        snowStorm.animationInterval = 33;
        snowStorm.start();
    }

    // --- What If Scenario Implementation ---
    const whatIfSection = document.querySelector('.what-if-section');
    const whatIfSubmit = document.getElementById('what-if-submit');
    const whatIfResults = document.getElementById('what-if-results');

    // Get the original form data from a hidden input, assuming Flask provides it
    // IMPORTANT: app.py must render a hidden input with id="originalFormDataHidden"
    // and its value set to JSON.stringify(form_data)
    const originalFormDataInput = document.getElementById('originalFormDataHidden');
    let originalFormData = {};
    if (originalFormDataInput && originalFormDataInput.value) {
        try {
            originalFormData = JSON.parse(originalFormDataInput.value);
            // Ensure the 'what-if' sliders also get their initial value from the original form data
            // This part is already handled by Jinja in index.html, but keeping it for robustness
            // document.getElementById('what-if-attr').value = originalFormData['attr1_1'] || 5;
            // document.getElementById('what-if-attr-val').textContent = originalFormData['attr1_1'] || 5;
            // document.getElementById('what-if-fun').value = originalFormData['fun1_1'] || 5;
            // document.getElementById('what-if-fun-val').textContent = originalFormData['fun1_1'] || 5;

        } catch (e) {
            console.error("Failed to parse original form data:", e);
        }
    } else {
        console.warn("originalFormDataHidden input not found or empty. 'What If' feature may not function correctly.");
    }


    if (whatIfSection && probMatchElement) { // Only show if results are displayed
        whatIfSection.style.display = 'block';
        
        // Update slider value displays for What If section
        document.getElementById('what-if-attr').addEventListener('input', (e) => {
            document.getElementById('what-if-attr-val').textContent = e.target.value;
        });
        document.getElementById('what-if-fun').addEventListener('input', (e) => {
            document.getElementById('what-if-fun-val').textContent = e.target.value;
        });

        // Add this to DOMContentLoaded
        document.getElementById('what-if-submit')?.addEventListener('click', async function() {
            const whatIfData = {
                attr1_1: document.getElementById('what-if-attr').value,
                fun1_1: document.getElementById('what-if-fun').value,
                // Include other original values
                original_data: JSON.parse(document.getElementById('originalFormDataHidden').value) // Correct ID used here
            };

            // Show loading state
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Menghitung...';
            this.disabled = true;

            try {
                const response = await fetch('/what_if_predict', { // Correct endpoint name
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(whatIfData)
                });
                
                const result = await response.json();
                
                // Update UI
                const heart = document.querySelector('#what-if-results .heart-progress');
                const percentage = document.querySelector('#what-if-results .heart-percentage');
                
                // Animate What If heart
                const whatIfProbMatch = result.prob_match;
                const whatIfScale = 0.6 + (whatIfProbMatch * 0.6); // Match main heart scaling
                heart.style.transform = `scale(${whatIfScale})`;
                percentage.textContent = `${Math.round(whatIfProbMatch * 100)}%`;

                // Color variation for what-if heart
                if (whatIfProbMatch > 0.7) {
                    heart.style.color = '#ff1493';
                } else if (whatIfProbMatch > 0.5) {
                    heart.style.color = '#ff6b8b';
                } else {
                    heart.style.color = '#ffb6c1';
                }
                
                whatIfResults.classList.remove('hidden');
            } catch (error) {
                console.error('Error during What If prediction:', error);
                // Optionally, display an error message in the UI
                percentage.textContent = 'Error!';
                heart.style.transform = 'scale(0.5)'; // Reset heart size on error
                heart.style.color = 'var(--danger-color)'; // Red color for error
            } finally {
                this.innerHTML = '<i class="fas fa-calculator"></i> Hitung Ulang';
                this.disabled = false;
            }
        });
    }

    // --- Chart.js Visualization ---
    const priorityChartCanvas = document.getElementById('priorityChart');
    if (priorityChartCanvas && probMatchElement) { // Only draw chart if results are shown
        const formDataInput = document.getElementById('originalFormDataHidden'); // Use the correct ID
        let formData = {};
        if (formDataInput && formDataInput.value) {
            try {
                formData = JSON.parse(formDataInput.value);
            } catch (e) {
                console.error("Failed to parse form data for chart:", e);
                return; // Exit if data is not available
            }
        } else {
            console.warn("originalFormDataHidden input not found or empty for chart. Chart may not display data.");
            return; // Exit if data is not available
        }
        
        const ctx = priorityChartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Daya Tarik', 'Ketulusan', 'Kecerdasan', 'Keseruan', 'Ambisi', 'Minat Sama'],
                datasets: [
                    {
                        label: 'Prioritas Anda',
                        data: [
                            formData.attr1_1,
                            formData.sinc1_1,
                            formData.intel1_1,
                            formData.fun1_1,
                            formData.amb1_1,
                            formData.shar1_1
                        ],
                        backgroundColor: 'rgba(255, 99, 132, 0.4)', // Slightly more opaque
                        borderColor: 'rgba(255, 99, 132, 1)',
                        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 2, // Thicker line
                        fill: true // Fill the radar area
                    },
                    {
                        label: 'Prioritas Pasangan',
                        data: [
                            formData.pf_o_att,
                            formData.pf_o_sin,
                            formData.pf_o_int,
                            formData.pf_o_fun,
                            formData.pf_o_amb,
                            formData.pf_o_sha
                        ],
                        backgroundColor: 'rgba(54, 162, 235, 0.4)', // Slightly more opaque
                        borderColor: 'rgba(54, 162, 235, 1)',
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2, // Thicker line
                        fill: true // Fill the radar area
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // Allows flexible sizing
                scales: {
                    r: {
                        angleLines: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)' // Lighter grid lines
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)' // Lighter grid lines
                        },
                        pointLabels: {
                            font: {
                                size: 12,
                                family: 'Poppins' // Use your app's font
                            },
                            color: 'var(--dark-color)' // Darker text for readability
                        },
                        suggestedMin: 0,
                        suggestedMax: 10,
                        ticks: {
                            beginAtZero: true,
                            stepSize: 2, // Show ticks every 2 units
                            color: 'var(--dark-color)', // Darker text for readability
                            font: {
                                family: 'Poppins'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: 'var(--dark-color)', // Darker text for readability
                            font: {
                                family: 'Poppins'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.raw;
                            }
                        }
                    }
                }
            }
        });
    }
});
