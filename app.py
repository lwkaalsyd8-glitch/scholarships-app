import os
import re
import sqlite3
import requests

from datetime import date, datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ==============================
# إعدادات المنصة
# ==============================

DB_NAME = "scholarships.db"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ==============================
# قاعدة البيانات
# ==============================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            continent TEXT,
            degree TEXT,
            fields TEXT,
            opening_date TEXT,
            closing_date TEXT,
            gpa_minimum TEXT,
            requirements TEXT,
            official_url TEXT,
            last_verified TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            scholarship_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scholarship_id)
                REFERENCES scholarships(id)
        )
    """)

    columns = {
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(scholarships)"
        ).fetchall()
    }

    migrations = {
        "opening_date": "TEXT",
        "closing_date": "TEXT",
        "gpa_minimum": "TEXT",
        "requirements": "TEXT",
        "official_url": "TEXT",
        "last_verified": "TEXT"
    }

    for column, data_type in migrations.items():
        if column not in columns:
            conn.execute(
                f"ALTER TABLE scholarships ADD COLUMN "
                f"{column} {data_type}"
            )

    conn.commit()
    conn.close()


# ==============================
# إشعارات Telegram
# ==============================

def send_telegram_notification(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram is not configured.")
        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    try:
        response = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            },
            timeout=10
        )

        response.raise_for_status()
        return response.json().get("ok", False)

    except requests.RequestException as error:
        print("Telegram error:", error)
        return False


# ==============================
# حالة المنحة
# ==============================

def scholarship_status(item):
    today = date.today()

    opening = item["opening_date"]
    closing = item["closing_date"]

    if not opening or not closing:
        return "المواعيد غير محددة"

    try:
        start = date.fromisoformat(opening)
        end = date.fromisoformat(closing)
    except ValueError:
        return "المواعيد تحتاج إلى تحقق"

    if today < start:
        return "لم يبدأ التقديم"

    if today > end:
        return "التقديم مغلق"

    return "التقديم مفتوح"


# ==============================
# منح أولية
# ==============================

INITIAL_SCHOLARSHIPS = [
    {
        "name": "Türkiye Scholarships",
        "country": "تركيا",
        "continent": "آسيا",
        "degree": "بكالوريوس وماجستير ودكتوراه",
        "fields": "جميع التخصصات",
        "requirements": "تختلف حسب المرحلة والبرنامج",
        "official_url": "https://www.turkiyeburslari.gov.tr/"
    },
    {
        "name": "Stipendium Hungaricum",
        "country": "المجر",
        "continent": "أوروبا",
        "degree": "بكالوريوس وماجستير ودكتوراه",
        "fields": "علمية وأدبية",
        "requirements": "تختلف حسب الجامعة والتخصص",
        "official_url": "https://stipendiumhungaricum.hu/"
    },
    {
        "name": "DAAD Scholarships",
        "country": "ألمانيا",
        "continent": "أوروبا",
        "degree": "ماجستير ودكتوراه",
        "fields": "تخصصات متعددة",
        "requirements": "حسب البرنامج",
        "official_url": "https://www.daad.de/"
    },
    {
        "name": "Erasmus Mundus",
        "country": "دول أوروبية متعددة",
        "continent": "أوروبا",
        "degree": "ماجستير",
        "fields": "تخصصات متعددة",
        "requirements": "حسب البرنامج",
        "official_url": "https://erasmus-plus.ec.europa.eu/"
    },
    {
        "name": "Chevening",
        "country": "المملكة المتحدة",
        "continent": "أوروبا",
        "degree": "ماجستير",
        "fields": "تخصصات متعددة",
        "requirements": "حسب شروط البرنامج",
        "official_url": "https://www.chevening.org/"
    },
    {
        "name": "Fulbright",
        "country": "الولايات المتحدة",
        "continent": "أمريكا الشمالية",
        "degree": "دراسات عليا",
        "fields": "تخصصات متعددة",
        "requirements": "تختلف حسب البلد والبرنامج",
        "official_url": "https://fulbrightprogram.org/"
    },
    {
        "name": "Chinese Government Scholarship",
        "country": "الصين",
        "continent": "آسيا",
        "degree": "بكالوريوس وماجستير ودكتوراه",
        "fields": "تخصصات متعددة",
        "requirements": "حسب الجامعة والبرنامج",
        "official_url": "https://www.campuschina.org/"
    },
    {
        "name": "Global Korea Scholarship",
        "country": "كوريا الجنوبية",
        "continent": "آسيا",
        "degree": "بكالوريوس ودراسات عليا",
        "fields": "تخصصات متعددة",
        "requirements": "حسب المسار",
        "official_url": "https://www.studyinkorea.go.kr/"
    },
    {
        "name": "MEXT Scholarship",
        "country": "اليابان",
        "continent": "آسيا",
        "degree": "مراحل دراسية متعددة",
        "fields": "علمية وأدبية",
        "requirements": "حسب البرنامج",
        "official_url": "https://www.studyinjapan.go.jp/"
    },
    {
        "name": "Australia Awards",
        "country": "أستراليا",
        "continent": "أوقيانوسيا",
        "degree": "دراسات عليا",
        "fields": "تخصصات متعددة",
        "requirements": "حسب بلد المتقدم",
        "official_url": "https://www.dfat.gov.au/"
    },
    {
        "name": "Manaaki New Zealand",
        "country": "نيوزيلندا",
        "continent": "أوقيانوسيا",
        "degree": "دراسات عليا",
        "fields": "تخصصات متعددة",
        "requirements": "حسب بلد المتقدم",
        "official_url": "https://www.nzscholarships.govt.nz/"
    },
    {
        "name": "Study in Saudi",
        "country": "السعودية",
        "continent": "آسيا",
        "degree": "مراحل دراسية متعددة",
        "fields": "تخصصات متعددة",
        "requirements": "حسب الجامعة والمنحة",
        "official_url": "https://studyinsaudi.moe.gov.sa/"
    },
    {
        "name": "ICCR Scholarships",
        "country": "الهند",
        "continent": "آسيا",
        "degree": "مراحل دراسية متعددة",
        "fields": "تخصصات متعددة",
        "requirements": "حسب البرنامج",
        "official_url": "https://a2ascholarships.iccr.gov.in/"
    }
]


def insert_initial_scholarships():
    conn = get_db()

    for item in INITIAL_SCHOLARSHIPS:
        exists = conn.execute(
            "SELECT id FROM scholarships WHERE name = ?",
            (item["name"],)
        ).fetchone()

        if not exists:
            conn.execute("""
                INSERT INTO scholarships (
                    name, country, continent, degree,
                    fields, requirements, official_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item["name"],
                item["country"],
                item["continent"],
                item["degree"],
                item["fields"],
                item["requirements"],
                item["official_url"]
            ))

    conn.commit()
    conn.close()


# ==============================
# تصميم الواجهة الأنيقة والمميزة
# ==============================

HOME_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>منح العالم | السيد لوكا</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">

<style>
:root {
    --primary: #4f46e5;
    --primary-hover: #4338ca;
    --success: #10b981;
    --success-hover: #059669;
    --bg-color: #f8fafc;
    --card-bg: #ffffff;
    --text-main: #1e293b;
    --text-muted: #64748b;
    --border-color: #e2e
