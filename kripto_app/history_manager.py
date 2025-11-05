from db_config import get_connection
from rumus_crypto import des_encrypt_bytes, des_decrypt_bytes

def save_history(user_id: int, activity_type: str, details: str) -> bool:
    conn = get_connection()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        enc = des_encrypt_bytes(details.encode('utf-8'))
        cur.execute("""
            INSERT INTO history_log (user_id, activity_type, log_encrypted)
            VALUES (%s, %s, %s)
        """, (user_id, activity_type, enc))
        conn.commit()
        return True
    except Exception as e:
        print("save_history error:", e)
        return False
    finally:
        cur.close()
        conn.close()

def fetch_history(user_id: int):
    conn = get_connection()
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT activity_type, log_encrypted, created_at
            FROM history_log
            WHERE user_id=%s
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
        out = []
        for act, enc, created in rows:
            try:
                dec = des_decrypt_bytes(enc).decode('utf-8')
            except Exception as e:
                dec = f"[decryption error: {e}]"
            out.append({"type": act, "details": dec, "time": created})
        return out
    finally:
        cur.close()
        conn.close()
