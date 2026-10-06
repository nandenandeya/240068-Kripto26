# Steganografi LSB pada Citra PNG

Program Python untuk menyembunyikan (encode) dan mengekstrak (decode) pesan teks atau file apa pun ke dalam citra PNG menggunakan metode **Least Significant Bit (LSB)**. Dibuat untuk Tugas Praktikum Kriptografi Pertemuan 05.

## Fitur

- Menyembunyikan **teks** atau **file** (gambar, `.txt`, dan lainnya).
- Dua mode penyisipan:
  - **Sequential**: bit pesan disisipkan berurutan dari pixel pertama.
  - **Acak**: urutan penyisipan diacak dengan PRNG, dan stego-key menjadi seed.
- Validasi otomatis: kapasitas cover dan keberadaan pesan tersembunyi.
- Hasil ekstraksi identik dengan pesan asli (lossless).

## Persyaratan

- Python 3.8 atau lebih baru
- Library `pillow` dan `numpy`

```bash
pip install pillow numpy
```

## Cara Penggunaan

### Encode

```bash
# Menyembunyikan teks
python LSB.py encode -c cover.png -t "pesan rahasia" -o stego.png

# Menyembunyikan file (gambar, txt, dll.)
python LSB.py encode -c cover.png -f pesan.txt -o stego.png

# Dengan stego-key (mode acak)
python LSB.py encode -c cover.png -t "pesan rahasia" -o stego.png -k kunci
```

### Decode

```bash
# Tanpa key
python LSB.py decode -s stego.png

# Dengan key (harus sama dengan saat encode)
python LSB.py decode -s stego.png -k kunci

# Menentukan folder output untuk file hasil ekstraksi
python LSB.py decode -s stego.png -o hasil
```

### Parameter

| Parameter | Fungsi |
|-----------|--------|
| `-c`, `--cover` | Gambar cover (PNG) |
| `-s`, `--stego` | Gambar stego yang akan di-decode |
| `-t`, `--text` | Pesan teks yang disisipkan |
| `-f`, `--file` | File yang disisipkan |
| `-o`, `--out` | Output encode: nama stego-image. Output decode: folder hasil |
| `-k`, `--key` | Stego-key (opsional) |

> Catatan: key saat decode harus **sama persis** dengan saat encode. Jika encode tanpa key, decode juga tanpa key.

## Cara Kerja Program

### 1. Dasar Metode LSB

Citra true color 24-bit menyimpan setiap pixel sebagai 3 byte (R, G, B). Bit paling kanan (LSB) tiap byte diganti dengan 1 bit pesan. Perubahan nilai hanya sebesar 1 (misalnya 202 menjadi 203), sehingga tidak terlihat oleh mata manusia.

```
Byte asli     : 1100101 0   (202)
Bit pesan     : 1
Byte stego    : 1100101 1   (203)
```

### 2. Format Data yang Disisipkan

Program menyisipkan dua bagian data.

**Header (8 byte, selalu sekuensial di awal citra)**

| Bagian | Ukuran | Isi |
|--------|--------|-----|
| Magic | 4 byte | `STG1`, penanda adanya pesan |
| Panjang payload | 4 byte | Jumlah byte payload (big-endian) |

**Payload**

| Bagian | Ukuran | Isi |
|--------|--------|-----|
| Tipe | 1 byte | `0` = teks, `1` = file |
| Panjang nama | 1 byte | Panjang nama file (0 untuk teks) |
| Nama file | variabel | Nama file asli (kosong untuk teks) |
| Data | variabel | Isi pesan atau file |

### 3. Proses Encode

1. Buka cover dan ubah ke mode RGB, lalu ratakan menjadi array 1 dimensi berisi byte.
2. Bentuk payload dari teks atau file, lalu buat header dari magic dan panjang payload.
3. Ubah header dan payload menjadi deretan bit.
4. Periksa kapasitas. Jika jumlah bit melebihi jumlah byte citra, program berhenti dengan pesan error.
5. Sisipkan bit header ke LSB 64 byte pertama.
6. Tentukan urutan byte untuk payload:
   - Tanpa key: berurutan setelah header.
   - Dengan key: urutan indeks diacak memakai `random.Random(key)`.
7. Ganti LSB byte pada urutan tersebut dengan bit payload (`byte & 0xFE | bit`).
8. Simpan sebagai PNG. Format PNG bersifat lossless sehingga LSB tidak rusak.

### 4. Proses Decode

1. Buka stego-image dan ratakan menjadi array byte.
2. Baca LSB 64 byte pertama menjadi header, lalu validasi magic `STG1`. Jika tidak cocok, program menyatakan tidak ada pesan tersembunyi.
3. Ambil panjang payload dari header.
4. Bangkitkan urutan byte yang sama seperti saat encode (sequential atau acak dengan key yang sama).
5. Baca LSB pada urutan tersebut, lalu susun menjadi byte payload.
6. Pisahkan tipe, nama, dan data:
   - Tipe 0: tampilkan sebagai teks.
   - Tipe 1: simpan sebagai file `extracted_<nama_asli>` di folder output.

### 5. Kapasitas

```
Kapasitas (byte) = (lebar x tinggi x 3 - 64) / 8
```

Contoh: cover 500 x 500 piksel dapat menampung sekitar 93 KB data.

## Keamanan dan Batasan

- **Mode acak** membuat posisi bit tersebar dan tidak dapat diekstrak tanpa key yang benar, tetapi pesan tidak dienkripsi. Untuk keamanan lebih, enkripsi pesan terlebih dahulu sebelum disisipkan.
- Stego-image **harus tetap PNG**. Konversi ke JPG, kompresi, atau resize akan merusak bit LSB dan pesan tidak dapat diekstrak.
- Metode LSB 1-bit masih dapat dideteksi dengan steganalysis seperti Enhanced LSB Attack atau analisis chi-square.

## Pengujian

| Skenario | Hasil |
|----------|-------|
| Teks tanpa key | Pesan terekstrak sama dengan asli |
| Teks dengan key | Pesan terekstrak sama dengan asli |
| File gambar dengan key | File hasil ekstraksi identik dengan file asli |
| Decode dengan key salah | Gagal (data acak) |
| Pesan melebihi kapasitas | Ditolak dengan pesan error |

Screenshot hasil running tersedia pada folder `screenshots/`.
