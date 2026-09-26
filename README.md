# 🛰️ ISS Overhead Notifier

A Python automation that watches the sky for you — it continuously checks the International Space Station's real-time position against your location, and emails you the moment it's passing overhead **and** it's dark enough outside to actually spot it.

> No more missing the ISS because you forgot to check. The script watches continuously and only pings you when it's actually worth stepping outside.

---

## 🎮 Demo

<img width="400" height="350" alt="Screenshot 2026-09-26 060559" src="https://github.com/user-attachments/assets/e027d670-561a-4c7b-88b0-3211da10ae07" />

---

## ✨ Features

- 🌍 **Real-time ISS position tracking** using the Open Notify API — no scraping, no manual lookups.
- 🌙 **Nighttime detection** via the Sunrise-Sunset API, so you're only alerted when it's actually dark enough to see the ISS (spotting it in daylight is basically impossible).
- ✉️ **Automatic email alerts** sent through Gmail's SMTP server the moment both conditions line up.
- 🔁 **Continuous monitoring loop** that checks conditions every 60 seconds, so you never have to remember to check manually.
- 🔒 **Secure credential handling** — Gmail login details and your coordinates are all loaded from environment variables via `python-dotenv`, never hardcoded.
- 📍 **Location-based matching** — compares the ISS's live coordinates against your latitude/longitude within a configurable proximity range.

---

## 🛠️ Tech Stack

| Category | Tool / Concept |
|---|---|
| Language | Python 3 |
| APIs | [Open Notify ISS API](http://open-notify.org/) · [Sunrise-Sunset API](https://sunrise-sunset.org/api) |
| HTTP Requests | `requests` |
| Email | `smtplib` (standard library) — SMTP + TLS email delivery |
| Secrets Management | `python-dotenv` |
| Core Concepts | Polling loops, geolocation comparison, date/time parsing, API integration |

---

## 📂 Project Structure

```
ISS Overhead Notifier/
│
├── main.py     # Entry point — polling loop, ISS/night checks, and email alert logic
├── .env         # Your Gmail credentials (never committed — see below)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x installed
- `requests` and `python-dotenv` — install via pip:

```bash
pip install requests python-dotenv
```

### Setup

**1. Create your `.env` file** in the project root with your Gmail credentials and coordinates:

```
SMTP_GMAIL_ID=your_email@gmail.com
SMTP_GMAIL_PASSWORD=your_app_password
ZNA_LAT=your_latitude
ZNA_LONG=your_longitude
```

> ⚠️ Use a [Gmail App Password](https://myaccount.google.com/apppasswords), not your real Gmail password — Google blocks plain-password SMTP logins by default. Add `.env` to your `.gitignore` so it never gets pushed to GitHub.

You can find your latitude/longitude from any map service — just search "my coordinates."

### Run it
```bash
python main.py
```

The script runs continuously, checking every 60 seconds, and emails you the moment the ISS is overhead at night. Leave it running in the background (or deploy it to a small always-on server) for it to actually be useful.

---

## 🧩 How It Works

### 1. Loading Credentials & Coordinates Securely
Gmail credentials and location coordinates are both loaded from environment variables via `python-dotenv` — nothing sensitive or personal is hardcoded in `main.py`.

```python
MY_LAT = float(os.getenv("ZNA_LAT"))
MY_LONG = float(os.getenv("ZNA_LONG"))
```

### 2. Checking the ISS's Current Position
The Open Notify API returns the ISS's live latitude and longitude. The script checks whether those coordinates fall within a ±5 degree box around your own location — a simple approximation rather than a precise "directly overhead" calculation.

```python
def iss_overhead():
    """Checks if the ISS is overhead"""
    response = requests.get("http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_lat = float(data["iss_position"]["latitude"])
    iss_long = float(data["iss_position"]["longitude"])

    return (
        MY_LAT-5 <= iss_lat <= MY_LAT+5 and MY_LONG-5 <= iss_long <= MY_LONG+5
    )
```

### 3. Checking If It's Dark Enough to See It
The Sunrise-Sunset API returns today's sunrise and sunset times for your coordinates. The script compares the current hour against those to determine whether it's currently nighttime.

```python
def night():
    """Checks if the time is nighttime"""
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }

    response = requests.get("https://api.sunrise-sunset.org/json",
                            params=parameters)
    response.raise_for_status()
    data = response.json()["results"]
    sunrise = int(data["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["sunset"].split("T")[1].split(":")[0])

    now = dt.datetime.now().hour

    return now >= sunset or now <= sunrise
```

### 4. The Monitoring Loop
Every 60 seconds, the script re-checks both conditions. If the ISS is overhead **and** it's nighttime, it sends an email alert via a secure Gmail SMTP connection. An `alerted` flag ensures only one email is sent per pass — since a visible ISS pass can last several minutes, without this flag the script would otherwise email you again on every single 60-second check until the ISS moves out of range.

```python
alerted = False

while True:
    """Checks if the ISS is overhead and if the time is nighttime, and if so,
      it sends an email to the user — but only once per pass."""
    time.sleep(60)  # Check every 60 seconds
    if iss_overhead() and night():
        if not alerted:
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(user=MY_GMAIL, password=PASSWORD)
                connection.sendmail(
                    from_addr=MY_GMAIL,
                    to_addrs=MY_GMAIL,
                    msg=MESSAGE.encode("utf-8"),
                )
            print("Sent email")
            alerted = True
    else:
        alerted = False
```

---

## 📚 What This Project Demonstrates

- Integrating multiple third-party REST APIs into a single decision pipeline (ISS position + sunrise/sunset data)
- Building a long-running polling loop that continuously monitors real-world conditions
- Comparing geolocation data with a simple coordinate range check
- Parsing and comparing time data from API responses
- Sending automated email alerts triggered by real-time conditions, with secure credential handling

---

## 🔮 Future Improvements

- [ ] Replace the ±5 degree bounding box with an actual distance calculation (e.g. the [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula)) for a more accurate "overhead" check
- [ ] Use full sunrise/sunset timestamps instead of just the hour, for more precise night detection
- [ ] Add logging so you can confirm the script is still running and what it's checked, without watching the console
- [ ] Persist the `alerted` state to a file so a mid-pass restart doesn't accidentally re-send an alert for the same pass

---

## 👤 Developer

**VISHAL YADAV**
- GitHub: [@VISHAL108-Mech](https://github.com/VISHAL108-Mech)
- LinkedIn: [vishal-yadav-2a91a7428](https://www.linkedin.com/in/vishal-yadav-2a91a7428)
- Email: [vy4122000@gmail.com](mailto:vy4122000@gmail.com)
