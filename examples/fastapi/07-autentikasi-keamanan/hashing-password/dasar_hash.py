import time

from pwdlib import PasswordHash

# Konfigurasi yang direkomendasikan pwdlib (Argon2)
password_hash = PasswordHash.recommended()

kata_sandi = "rahasia-saya-123"

# 1. Hash: hasilnya bukan kata sandi asli
hash_1 = password_hash.hash(kata_sandi)
hash_2 = password_hash.hash(kata_sandi)
print("hash 1 :", hash_1)
print("hash 2 :", hash_2)
print("kedua hash sama?", hash_1 == hash_2)

# 2. Verifikasi: cocokkan kata sandi yang diketik dengan hash tersimpan
print("kata sandi benar :", password_hash.verify(kata_sandi, hash_1))
print("kata sandi salah :", password_hash.verify("salah-total-999", hash_1))
print("verifikasi hash 2:", password_hash.verify(kata_sandi, hash_2))

# 3. Hashing sengaja lambat
mulai = time.perf_counter()
password_hash.hash(kata_sandi)
print(f"waktu 1 kali hash: {(time.perf_counter() - mulai) * 1000:.0f} ms")

# 4. Apakah hash perlu diperbarui? (misalnya setelah pengaturan algoritma diubah)
print("perlu hash ulang?", password_hash.verify_and_update(kata_sandi, hash_1)[1] is not None)
