import time

_sessions = {}

def save_session(user_id, kiosk_id, ttl=300):
    _sessions[user_id] = {
        "kiosk_id": kiosk_id,
        "expires_at": time.time() + ttl
    }

def get_kiosk_by_session(user_id):
    session = _sessions.get(user_id)
    if not session:
        return None
    if time.time() > session["expires_at"]:
        del _sessions[user_id]
        return None
    return session["kiosk_id"]
