# crypto_module.py
# Semua algoritma kripto dikumpulkan di sini:
from Crypto.Cipher import DES, AES, Blowfish
from Crypto.Util.Padding import pad, unpad
import hashlib, base64
from PIL import Image

# -----------------------------
# 1) LOGIN: SHA-256
# -----------------------------
def hash_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------
# 2) DATABASE HISTORY: DES (mengembalikan base64)
# -----------------------------
# KUNCI DES harus 8 byte
DES_KEY = b'MySecr3t'  # ganti sesuai kebutuhan (8 bytes)

def des_encrypt_bytes(b: bytes) -> str:
    cipher = DES.new(DES_KEY, DES.MODE_ECB)
    encrypted = cipher.encrypt(pad(b, DES.block_size))
    return base64.b64encode(encrypted).decode()

def des_decrypt_bytes(b64text: str) -> bytes:
    cipher = DES.new(DES_KEY, DES.MODE_ECB)
    encrypted = base64.b64decode(b64text)
    decrypted = unpad(cipher.decrypt(encrypted), DES.block_size)
    return decrypted

# -----------------------------
# 3) TEKS SUPER: Vigenere + AES
# -----------------------------
# Vigenere (classical)
def vigenere_encrypt(plain: str, key: str) -> str:
    key = key.upper()
    out = []
    ki = 0
    for ch in plain:
        if ch.isalpha():
            base = 'A' if ch.isupper() else 'a'
            shift = ord(key[ki % len(key)]) - ord('A')
            out.append(chr((ord(ch) - ord(base) + shift) % 26 + ord(base)))
            ki += 1
        else:
            out.append(ch)
    return ''.join(out)

def vigenere_decrypt(cipher: str, key: str) -> str:
    key = key.upper()
    out = []
    ki = 0
    for ch in cipher:
        if ch.isalpha():
            base = 'A' if ch.isupper() else 'a'
            shift = ord(key[ki % len(key)]) - ord('A')
            out.append(chr((ord(ch) - ord(base) - shift) % 26 + ord(base)))
            ki += 1
        else:
            out.append(ch)
    return ''.join(out)

# AES (CBC mode) — menggunakan base64 output
# AES_KEY harus 16/24/32 bytes; IV 16 bytes
AES_KEY = b'16bytesAESkey!!!'  # contoh 16 bytes (ubah di produksi)
AES_IV  = b'16bytesAESiv!!!!'  # contoh 16 bytes

def aes_encrypt_text(plain: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    enc = cipher.encrypt(pad(plain.encode('utf-8'), AES.block_size))
    return base64.b64encode(enc).decode()

def aes_decrypt_text(b64cipher: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    dec = unpad(cipher.decrypt(base64.b64decode(b64cipher)), AES.block_size)
    return dec.decode('utf-8')

def text_super_encrypt(plain: str, v_key: str) -> str:
    step1 = vigenere_encrypt(plain, v_key)
    return aes_encrypt_text(step1)

def text_super_decrypt(b64cipher: str, v_key: str) -> str:
    step1 = aes_decrypt_text(b64cipher)
    return vigenere_decrypt(step1, v_key)

# -----------------------------
# 4) FILE: Blowfish — operasi bytes <-> base64
# -----------------------------
BLOWFISH_KEY = b'MyBlowK!'  # 8..56 bytes

def blowfish_encrypt_bytes(raw: bytes) -> str:
    cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_ECB)
    enc = cipher.encrypt(pad(raw, Blowfish.block_size))
    return base64.b64encode(enc).decode()

def blowfish_decrypt_bytes(b64cipher: str) -> bytes:
    cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_ECB)
    dec = unpad(cipher.decrypt(base64.b64decode(b64cipher)), Blowfish.block_size)
    return dec

# -----------------------------
# 5) STEGANOGRAFI: LSB (RGB)
# -----------------------------
# Marker akhir pesan: 16-bit sentinel '1111111111111110'
def _to_bin(data: bytes) -> str:
    return ''.join(format(b, '08b') for b in data)

def lsb_hide(image_path: str, message: str, out_path: str):
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    msg_bytes = message.encode('utf-8')
    bin_msg = _to_bin(msg_bytes) + '1111111111111110'  # sentinel
    data_index = 0

    pixels = list(img.getdata())
    new_pixels = []
    for i, pixel in enumerate(pixels):
        if data_index >= len(bin_msg):
            new_pixels.extend(pixels[i:])  # sisa
            break
        r, g, b = pixel
        r = (r & ~1) | int(bin_msg[data_index]) if data_index < len(bin_msg) else r
        data_index += 1
        g = (g & ~1) | int(bin_msg[data_index]) if data_index < len(bin_msg) else g
        data_index += 1
        b = (b & ~1) | int(bin_msg[data_index]) if data_index < len(bin_msg) else b
        data_index += 1
        new_pixels.append((r, g, b))
    # if leftover not filled, just fill rest
    new_pixels += pixels[len(new_pixels):]
    encoded = Image.new(img.mode, img.size)
    encoded.putdata(new_pixels)
    encoded.save(out_path)

def lsb_reveal(image_path: str) -> str:
    img = Image.open(image_path).convert('RGB')
    pixels = list(img.getdata())
    bin_data = ''
    for pixel in pixels:
        for n in range(3):
            bin_data += str(pixel[n] & 1)
    # split per 8 bits
    chars = [bin_data[i:i+8] for i in range(0, len(bin_data), 8)]
    message_bytes = bytearray()
    for ch in chars:
        if len(ch) < 8:
            break
        if ch == '11111110':  # sentinel (last 8 bits of sentinel)
            break
        message_bytes.append(int(ch, 2))
    try:
        return message_bytes.decode('utf-8', errors='ignore')
    except:
        return ""
