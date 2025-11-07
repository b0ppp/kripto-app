import streamlit as st
from rumus_crypto import (
    text_super_encrypt, text_super_decrypt,
    blowfish_encrypt_bytes, blowfish_decrypt_bytes,
    lsb_hide, lsb_reveal
)
from history_manager import save_history
import tempfile, os

def home_page():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu.")
        st.stop()

    st.title("Crypton")
    st.write(f"Halo, **{st.session_state.username}** — pilih fitur di bawah.")

    menu = st.selectbox("Fitur:", ["Teks (Vigenere + AES)", "File (Blowfish)", "Gambar (Steganografi LSB)"])

    if menu == "Teks (Vigenere + AES)":
        st.subheader("🍳 Teks Super — Vigenere + AES")
        key = st.text_input("Kunci Vigenere (huruf):", value="KUNCI")
        text = st.text_area("Masukkan teks")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Enkripsi Teks"):
                if not text or not key:
                    st.warning("Masukkan teks dan kunci.")
                else:
                    out = text_super_encrypt(text, key)
                    st.code(out)
                    save_history(st.session_state.user_id, "Enkripsi Teks", f"Plain len={len(text)}; result={out[:80]}...")
        with col2:
            enc_input = st.text_area("Masukkan ciphertext (base64) untuk dekripsi")
            if st.button("Dekripsi Teks"):
                if not enc_input or not key:
                    st.warning("Masukkan ciphertext dan kunci.")
                else:
                    try:
                        dec = text_super_decrypt(enc_input, key)
                        st.code(dec)
                        save_history(st.session_state.user_id, "Dekripsi Teks", f"Cipher len={len(enc_input)}; result_preview={dec[:80]}...")
                    except Exception as e:
                        st.error(f"Error dekripsi: {e}")

    elif menu == "File (Blowfish)":
        st.subheader("🪄 Enkripsi / Dekripsi File — Blowfish")
        uploaded = st.file_uploader("Upload file untuk enkripsi", type=None)
        if uploaded:
            filename = uploaded.name
            raw = uploaded.read()
            if st.button("Enkripsi file"):
                b64 = blowfish_encrypt_bytes(raw)
                st.download_button("Download file terenkripsi (.bin)", data=b64.encode(), file_name=f"{filename}.enc", mime="application/octet-stream")
                save_history(st.session_state.user_id, "Enkripsi File", f"File {filename} enkripsi size={len(raw)} -> {len(b64)}")
            st.markdown("---")
            st.write("Dekripsi file terenkripsi (paste base64 hasil enkripsi):")
            paste = st.text_area("Paste base64 ciphertext")
            if st.button("Dekripsi file"):
                try:
                    dec = blowfish_decrypt_bytes(paste)
                    st.download_button("Download hasil dekripsi", data=dec, file_name=f"decrypted_{filename}", mime="application/octet-stream")
                    save_history(st.session_state.user_id, "Dekripsi File", f"File {filename} dekripsi size={len(dec)}")
                except Exception as e:
                    st.error(f"Error dekripsi: {e}")

    elif menu == "Gambar (Steganografi LSB)":
        st.subheader("🖼️ Steganografi LSB — Sembunyikan pesan dalam gambar")
        colA, colB = st.columns(2)
        with colA:
            up_img = st.file_uploader("Upload gambar (PNG/JPG) untuk embed pesan", type=["png","jpg","jpeg"])
            msg = st.text_area("Pesan yang ingin disembunyikan")
            if up_img and st.button("Sembunyikan pesan ke gambar"):
                # simpan sementara
                tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(up_img.name)[1])
                tmp_in.write(up_img.read())
                tmp_in.close()
                out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                try:
                    lsb_hide(tmp_in.name, msg, out_path)
                    with open(out_path, "rb") as f:
                        data = f.read()
                    st.download_button("Download gambar berisi pesan", data=data, file_name=f"stego_{up_img.name}", mime="image/png")
                    save_history(st.session_state.user_id, "Stego Embed", f"Embed message len={len(msg)} into {up_img.name}")
                finally:
                    try: os.unlink(tmp_in.name)
                    except: pass

        with colB:
            up_img2 = st.file_uploader("Upload gambar (PNG/JPG) untuk ekstrak pesan", key="extract")
            if up_img2 and st.button("Ekstrak pesan"):
                tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(up_img2.name)[1])
                tmp_in.write(up_img2.read())
                tmp_in.close()
                try:
                    revealed = lsb_reveal(tmp_in.name)
                    if revealed:
                        st.success("Pesan terdeteksi:")
                        st.code(revealed)
                        save_history(st.session_state.user_id, "Stego Extract", f"Extracted message len={len(revealed)} from {up_img2.name}")
                    else:
                        st.info("Tidak ada pesan yang terdeteksi atau format tidak cocok.")
                finally:
                    try: os.unlink(tmp_in.name)
                    except: pass

