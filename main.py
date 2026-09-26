"""ISS Overhead Project: This project checks if the ISS is overhead and if the
 time is nighttime, and if so, it sends an email to the user."""

import requests
import datetime as dt
import smtplib
import time
import os
from dotenv import load_dotenv

load_dotenv()

MY_GMAIL = os.getenv("SMTP_GMAIL_ID")
PASSWORD = os.getenv("SMTP_GMAIL_PASSWORD")
MESSAGE = "Subject: ISS Coming🛰️\n\nLook at the sky, ISS is above your head."

# Latitude and longitude of the user
MY_LAT = 25.487049102783203
MY_LONG = 83.57356262207031


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

alert = False

while True:
    """Checks if the ISS is overhead and if the time is nighttime, and if so,
      it sends an email to the user."""
    time.sleep(60)  # Check every 60 seconds
    if iss_overhead() and night():
        if not alert:
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(user=MY_GMAIL, password=PASSWORD)
                connection.sendmail(
                    from_addr=MY_GMAIL,
                    to_addrs=MY_GMAIL,
                    msg=MESSAGE.encode("utf-8"),
                )
            print("Sent email")
            alert = True
    else:
        alert = False
