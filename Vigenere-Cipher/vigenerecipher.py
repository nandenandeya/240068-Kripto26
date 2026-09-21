def bersihkan_teks(teks):
    #Ambil huruf saja dan ubah ke huruf besar.
    return "".join(h for h in teks.upper() if h.isalpha())


def huruf_ke_angka(huruf):
    return ord(huruf) - ord("A")


def angka_ke_huruf(angka):
    return chr(angka % 26 + ord("A"))


def buat_kunci(kunci, panjang):
    # Ulang kunci sampai sepanjang teks (dipotong jika lebih panjang)
    kunci_panjang = ""
    for i in range(panjang):
        kunci_panjang += kunci[i % len(kunci)]
    return kunci_panjang


def enkripsi(plaintext, kunci):
    plaintext = bersihkan_teks(plaintext)
    kunci = bersihkan_teks(kunci)
    kunci_panjang = buat_kunci(kunci, len(plaintext))

    ciphertext = ""
    for huruf_p, huruf_k in zip(plaintext, kunci_panjang):
        angka = huruf_ke_angka(huruf_p) + huruf_ke_angka(huruf_k)
        ciphertext += angka_ke_huruf(angka)
    return ciphertext


def dekripsi(ciphertext, kunci):
    ciphertext = bersihkan_teks(ciphertext)
    kunci = bersihkan_teks(kunci)
    kunci_panjang = buat_kunci(kunci, len(ciphertext))

    plaintext = ""
    for huruf_c, huruf_k in zip(ciphertext, kunci_panjang):
        angka = huruf_ke_angka(huruf_c) - huruf_ke_angka(huruf_k)
        plaintext += angka_ke_huruf(angka)
    return plaintext


def main():
    print("=== Vigenere Cipher ===")
    print("1. Enkripsi")
    print("2. Dekripsi")
    pilihan = input("Pilih (1/2): ")

    teks = input("Masukkan teks : ")
    kunci = input("Masukkan kunci: ")

    if not bersihkan_teks(kunci):
        print("Kunci harus berisi huruf.")
        return

    if pilihan == "1":
        print("Ciphertext:", enkripsi(teks, kunci))
    elif pilihan == "2":
        print("Plaintext :", dekripsi(teks, kunci))
    else:
        print("Pilihan tidak valid.")


main()