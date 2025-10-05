import requests
from bs4 import BeautifulSoup
import telegram
import os

LOGIN_URL = "https://online.spor.istanbul/uyegiris"
SESSIONS_URL = "https://online.spor.istanbul/uyeseanssecim"

TC = os.getenv("TC")           # TC Kimlik No
SIFRE = os.getenv("SIFRE")     # Şifre
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telegram.Bot(token=BOT_TOKEN)

def login():
    """Siteye giriş yapar ve session döner."""
    session = requests.Session()
    payload = {
        "txtTCPasaport": TC,
        "txtSifre": SIFRE,
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    response = session.post(LOGIN_URL, data=payload, headers=headers)
    if response.status_code != 200:
        print("⚠️ Giriş isteği başarısız:", response.status_code)
    return session

def check_sessions(session):
    """Rezervasyona açık seansları kontrol eder."""
    r = session.get(SESSIONS_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    # "Karma" içeren seans kutularını bul
    cards = soup.select("div.col-md-3")
    open_sessions = []
    for card in cards:
        if "Karma" in card.text:
            text = " ".join(card.text.split())
            open_sessions.append(text)

    if not open_sessions:
        print("Şu anda açık (Karma) seans yok.")
        return

    try:
        with open("old_sessions.txt", "r", encoding="utf-8") as f:
            old_sessions = set(f.read().splitlines())
    except FileNotFoundError:
        old_sessions = set()

    new_sessions = set(open_sessions) - old_sessions

    if new_sessions:
        msg = "🎾 Yeni seans(lar) açıldı:\n" + "\n".join(new_sessions)
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print(msg)
    else:
        print("Yeni seans bulunamadı.")

    with open("old_sessions.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(open_sessions))

if __name__ == "__main__":
    session = login()
    check_sessions(session)
