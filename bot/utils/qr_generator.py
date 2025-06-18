import qrcode

def generate_qr(session_id):
    url = f"https://t.me/sapat_print_bot?start={session_id}"
    img = qrcode.make(url)
    img.save(f"{session_id}.png")
    print(f"QR-код сохранён: {session_id}.png")
