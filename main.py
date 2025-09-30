from flask import Flask, jsonify, request, send_from_directory
import requests
import datetime
import os

# 🔹 Firebase Config
FIREBASE_URL = "https://homepage-e21ca-default-rtdb.firebaseio.com/visits/count.json"

# 🔹 Telegram Config
BOT_TOKEN = "8469613543:AAEG5_OxiBEbweHIeBUqts7pXjormS9kwbI"
CHAT_ID = "5029478739"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

PAGE_NAME = "HOMEPAGE"

app = Flask(__name__, static_folder="static", template_folder=".")

# ------------------- Reset Logic -------------------
def update_counter(new_count):
    try:
        res = requests.put(FIREBASE_URL, json=new_count)
        return res.status_code == 200
    except Exception as e:
        print("Error updating counter:", e)
        return False

def send_telegram_message(text):
    try:
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        requests.post(TELEGRAM_API, json=payload)
    except Exception as e:
        print("Telegram error:", e)

def reset_logic():
    now = datetime.datetime.now()
    visit_time = now.strftime("%Y-%m-%d %H:%M:%S")

    current_count = 1
    ok = update_counter(current_count)

    if ok:
        try:
            ip_data = requests.get("https://api.ipify.org?format=json").json()
            ip = ip_data.get("ip", "Unknown")

            loc_data = requests.get(f"https://ipapi.co/{ip}/json/").json()
            city = loc_data.get("city", "Unknown")
            region = loc_data.get("region", "")
            country = loc_data.get("country_name", "")
            isp = loc_data.get("org", "")

            text_message = (
                f"🚨 *Visit Reset* 🚨\n\n"
                f"📄 Page: {PAGE_NAME}\n"
                f"🌐 IP: {ip}\n"
                f"📍 Location: {city}, {region}, {country}\n"
                f"🏢 ISP: {isp}\n"
                f"⏰ Time: {visit_time}\n"
                f"#️⃣ Visitor Count: {current_count}"
            )

            send_telegram_message(text_message)
        except Exception as e:
            print("Error sending Telegram message:", e)

    return ok
# ---------------------------------------------------

# 🔹 Root route → serve your HTML frontend
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# 🔹 Favicon route (error fix)
@app.route("/favicon.ico")
def favicon():
    return "", 204

# 🔹 API Reset endpoint
@app.route("/api/reset", methods=["POST"])
def reset_endpoint():
    ok = reset_logic()
    if ok:
        return jsonify({"success": True, "new_count": 1}), 200
    else:
        return jsonify({"success": False, "error": "Firebase update failed"}), 500


# 🔹 Local run ke liye
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
