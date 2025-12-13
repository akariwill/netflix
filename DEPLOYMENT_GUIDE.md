# Panduan Deploy Aplikasi Flask: Ngrok & VPS

Dokumen ini menjelaskan dua cara untuk men-deploy aplikasi Flask Anda:

1.  **Ngrok:** Untuk demo cepat dan sementara dari komputer lokal Anda.
2.  **VPS (Virtual Private Server):** Untuk deployment permanen dan profesional.

---

## Metode 1: Deploy Cepat dengan Ngrok

**Kapan menggunakan ini?**
Sangat cocok untuk demo singkat, berbagi proyek dengan dosen/teman untuk waktu terbatas, atau jika Anda perlu memenuhi syarat "online" tanpa setup server yang rumit.

### Langkah-langkah

1.  **Unduh Ngrok**
    *   Kunjungi halaman unduh Ngrok: [https://ngrok.com/download](https://ngrok.com/download).
    *   Unduh versi untuk sistem operasi Anda (Windows).
    *   Ekstrak file `ngrok.exe` dari file ZIP.

2.  **Hubungkan Akun Ngrok (Penting)**
    *   Daftar akun gratis di [dashboard Ngrok](https://dashboard.ngrok.com/signup).
    *   Setelah login, salin *authtoken* Anda dari halaman "Your Authtoken".
    *   Buka Command Prompt (CMD), masuk ke folder tempat `ngrok.exe` berada, dan jalankan perintah:
        ```bash
        # Ganti YOUR_AUTHTOKEN dengan token yang Anda salin
        ngrok config add-authtoken YOUR_AUTHTOKEN
        ```
    *Langkah ini penting untuk mendapatkan durasi sesi yang lebih lama.*

3.  **Jalankan Aplikasi Flask Anda**
    *   Buka terminal, masuk ke direktori proyek Anda, dan jalankan aplikasi:
        ```bash
        python app.py
        ```
    *   Aplikasi Anda kini berjalan di `http://127.0.0.1:5000`. Biarkan terminal ini tetap terbuka.

4.  **Mulai Ngrok**
    *   Buka **terminal baru** (biarkan terminal Flask tetap berjalan).
    *   Jalankan perintah ini untuk mengekspos port `5000` ke internet:
        ```bash
        ngrok http 5000
        ```

5.  **Dapatkan URL Publik Anda**
    *   Ngrok akan menampilkan URL publik di terminal pada baris `Forwarding`. Contohnya: `https://xxxxxxxx.ngrok-free.app`.
    *   URL inilah yang dapat Anda bagikan. Siapa pun dapat mengaksesnya selama komputer Anda menyala dan kedua terminal (Flask & Ngrok) tetap berjalan.

---

## Metode 2: Deploy Permanen di VPS (Server Linux)

**Kapan menggunakan ini?**
Untuk membuat aplikasi Anda online 24/7, stabil, dan dapat diakses melalui domain/subdomain pribadi. (Contoh: `dashboard.domainanda.com`).

**Asumsi:** Anda menggunakan VPS dengan OS Linux (seperti Ubuntu) dan memiliki akses SSH.

### Langkah 1: Pindahkan Kode Anda ke VPS

Cara paling umum dan disarankan adalah menggunakan `git`.

1.  **Di Komputer Lokal:** Inisialisasi `git`, buat repositori di GitHub/GitLab, lalu push kode Anda.
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git remote add origin <URL_REPO_ANDA>
    git push -u origin master
    ```

2.  **Di VPS Anda (via SSH):** Clone repositori tersebut.
    ```bash
    # Update & instal git jika belum ada
    sudo apt update
    sudo apt install git -y

    # Clone proyek Anda
    git clone <URL_REPO_ANDA>
    cd <NAMA_FOLDER_PROYEK>
    ```

### Langkah 2: Siapkan Lingkungan Server

1.  **Instal Python & Virtual Environment (`venv`)**
    ```bash
    sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv -y
    ```
2.  **Buat dan Aktifkan `venv`**
    ```bash
    # Membuat environment
    python3 -m venv venv

    # Mengaktifkan environment
    source venv/bin/activate
    ```
    *(Anda akan melihat `(venv)` di awal baris terminal).*

3.  **Instal Dependencies & Gunicorn**
    *Gunicorn* adalah server aplikasi WSGI kelas produksi yang akan menjalankan kode Python Anda.
    ```bash
    pip install flask pandas gunicorn
    ```

### Langkah 3: Buat Layanan `systemd`

`systemd` akan memastikan aplikasi Anda berjalan otomatis saat server booting dan me-restartnya jika terjadi crash.

1.  **Buat File Layanan**
    ```bash
    sudo nano /etc/systemd/system/netflix-app.service
    ```

2.  **Isi File Layanan**
    Salin-tempel konfigurasi ini. **PENTING:** Ganti `your_user` dengan username Anda di VPS dan sesuaikan path `WorkingDirectory` & `ExecStart`.

    ```ini
    [Unit]
    Description=Gunicorn instance for Netflix Analysis App
    After=network.target

    [Service]
    User=your_user
    Group=www-data
    WorkingDirectory=/home/your_user/nama_folder_proyek
    Environment="PATH=/home/your_user/nama_folder_proyek/venv/bin"
    ExecStart=/home/your_user/nama_folder_proyek/venv/bin/gunicorn --workers 3 --bind unix:netflix-app.sock -m 007 app:app

    [Install]
    WantedBy=multi-user.target
    ```

3.  **Jalankan dan Aktifkan Layanan**
    ```bash
    sudo systemctl start netflix-app
    sudo systemctl enable netflix-app
    ```

### Langkah 4: Konfigurasi Nginx sebagai Reverse Proxy

Nginx akan bertindak sebagai "pintu depan" yang menerima trafik web (port 80/443) dan meneruskannya ke aplikasi Gunicorn Anda.

1.  **Instal Nginx**
    ```bash
    sudo apt install nginx -y
    ```

2.  **Buat File Konfigurasi Nginx**
    ```bash
    sudo nano /etc/nginx/sites-available/netflix-app
    ```

3.  **Isi File Konfigurasi**
    Ganti `your_domain_or_ip` dengan domain atau alamat IP VPS Anda.
    ```nginx
    server {
        listen 80;
        server_name your_domain_or_ip;

        location / {
            include proxy_params;
            proxy_pass http://unix:/home/your_user/nama_folder_proyek/netflix-app.sock;
        }
    }
    ```

4.  **Aktifkan Konfigurasi**
    ```bash
    # Buat symbolic link
    sudo ln -s /etc/nginx/sites-available/netflix-app /etc/nginx/sites-enabled

    # Hapus konfigurasi default jika perlu
    # sudo rm /etc/nginx/sites-enabled/default

    # Tes konfigurasi dan restart Nginx
    sudo nginx -t
    sudo systemctl restart nginx
    ```

5.  **Buka Firewall (jika aktif)**
    ```bash
    sudo ufw allow 'Nginx Full'
    ```

Aplikasi Anda sekarang seharusnya sudah dapat diakses melalui alamat IP atau domain Anda. Untuk mengamankan koneksi dengan HTTPS, gunakan **Certbot**.
