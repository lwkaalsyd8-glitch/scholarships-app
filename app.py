import os
import re
import sqlite3
import requests

from datetime import date, datetime
from flask import Flask, request, jsonify, render_template_string, abort

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
            percentage_minimum TEXT,
            requirements TEXT,
            description TEXT,
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
        "percentage_minimum": "TEXT",
        "description": "TEXT",
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
# منح أولية (بدون روسيا، وتدعم البكالوريوس والنسب المئوية)
# ==============================

INITIAL_SCHOLARSHIPS = [
    {
        "name": "Türkiye Scholarships (المنحة التركية)",
        "country": "تركيا",
        "continent": "آسيا وأوروبا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "fields": "جميع التخصصات (هندسة، طب، علوم، إنسانيات)",
        "percentage_minimum": "70% للبكالوريوس (80% للطب والصيدلة)",
        "requirements": "شهادة الثانوية العامة، جواز سفر، خطاب تفوق أو توصية",
        "description": "تعتبر المنحة التركية من أشهر المنح حول العالم لشمولها التام لكافة الرسوم الدراسية، السكن الجامعي، سنة كاملة لتعلم اللغة التركية، تذاكر الطيران ذهاباً وإياباً، وراتب شهري منتظم لمرحلة البكالوريوس والدراسات العليا.",
        "official_url": "https://www.turkiyeburslari.gov.tr/"
    },
    {
        "name": "Stipendium Hungaricum (منحة المجر)",
        "country": "المجر",
        "continent": "أوروبا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "fields": "الهندسة، إدارة الأعمال، الطب، الزراعة، العلوم",
        "percentage_minimum": "75% (تقدير جيد جداً في الشهادة الثانوية أو البكالوريوس)",
        "requirements": "شهادة الثانوية مترجمة، شهادة لغة إنجليزية، استمارة التقديم",
        "description": "منحة الحكومة المجرية ممولة بالكامل وتوفر مقاعد دراسية واسعة للطلاب الدوليين لمرحلة البكالوريوس والدراسات العليا، وتشمل الإعفاء من الرسوم الدراسية، سكن مجاني، تأمين صحي، وراتب شهري معيشي.",
        "official_url": "https://stipendiumhungaricum.hu/"
    },
    {
        "name": "DAAD Scholarships (المنحة الألمانية)",
        "country": "ألمانيا",
        "continent": "أوروبا",
        "degree": "ماجستير ودكتوراه",
        "fields": "تخصصات متعددة، الطاقة المتجددة، الهندسة، الاقتصاد",
        "percentage_minimum": "80% أو تقدير جيد جداً مرتفع",
        "requirements": "خبرة عمل لمدة سنة على الأقل، شهادة إنجليزية أو ألمانية",
        "description": "تستهدف المنحة الألمانية (DAAD) الكفاءات الأكاديمية والمهنية لدعم الدراسات العليا بتمويل شهري سخي وتأمين صحي وتغطية تكاليف السفر.",
        "official_url": "https://www.daad.de/"
    },
    {
        "name": "Chinese Government Scholarship (منحة الصين)",
        "country": "الصين",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "fields": "ذكاء اصطناعي، هندسة برمجيات، طب، لغات، علوم",
        "percentage_minimum": "70% في الشهادة الثانوية أو الجامعية",
        "requirements": "الفحص الطبي، شهادة خلو سوابق، خطة بحث أو خطاب دوافع",
        "description": "منحة شاملة تقدمها الحكومة الصينية بالتعاون مع كبرى الجامعات الصينية لدعم طلاب البكالوريوس والدراسات العليا مع تغطية كاملة للمصاريف والإقامة.",
        "official_url": "https://www.campuschina.org/"
    },
    {
        "name": "Global Korea Scholarship - GKS (منحة كوريا الجنوبية)",
        "country": "كوريا الجنوبية",
        "continent": "آسيا",
        "degree": "بكالوريوس ودراسات عليا",
        "fields": "هندسة، تكنولوجيا، إدارة أعمال، رعاية صحية",
        "percentage_minimum": "80% أو معدل تراكمي عالي",
        "requirements": "شهادات معتمدة، تزكيات أكاديمية، استمارة التسجيل",
        "description": "منحة حكومية كورية كبرى تتيح للطلاب دراسة البكالوريوس والماجستير والدكتوراه بعد سنة تحضيرية لتعلم اللغة الكورية، مع تذاكر طيران وراتب ومصاريف دراسية كاملة.",
        "official_url": "https://www.studyinkorea.go.kr/"
    },
    {
        "name": "Fulbright Scholarship (منحة فولبرايت الأمريكية)",
        "country": "الولايات المتحدة",
        "continent": "أمريكا الشمالية",
        "degree": "دراسات عليا (ماجستير وأبحاث)",
        "fields": "تخصصات متعددة",
        "percentage_minimum": "85% فما فوق مع إجادة اللغة الإنجليزية",
        "requirements": "اختبارات القدرات واللغة (TOEFL/IELTS)، خطابات توصية",
        "description": "أرقى المنح الدراسية في الولايات المتحدة الأمريكية لتمويل دراسة الماجستير والأبحاث للطلاب المتميزين من حول العالم.",
        "official_url": "https://fulbrightprogram.org/"
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
                    fields, percentage_minimum, requirements, description, official_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["name"],
                item["country"],
                item["continent"],
                item["degree"],
                item["fields"],
                item["percentage_minimum"],
                item["requirements"],
                item["description"],
                item["official_url"]
            ))

    conn.commit()
    conn.close()


# ==============================
# تصميم الواجهة الأنيقة والمميزة مع صفحة المقال / التفاصيل
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
    --border-color: #e2e8f0;
}

body {
    font-family: 'Cairo', sans-serif;
    background-color: var(--bg-color);
    color: var(--text-main);
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

header {
    background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
    color: white;
    text-align: center;
    padding: 40px 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

header h1 {
    margin: 0 0 10px 0;
    font-size: 2.2rem;
    font-weight: 800;
}

header p {
    margin: 5px 0;
    font-size: 1.05rem;
    opacity: 0.9;
}

.container {
    max-width: 1100px;
    margin: 30px auto;
    padding: 0 20px;
}

.card {
    background: var(--card-bg);
    padding: 25px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    border: 1px solid var(--border-color);
}

h2 {
    color: var(--text-main);
    font-size: 1.4rem;
    margin-top: 0;
    margin-bottom: 20px;
    font-weight: 700;
    border-right: 4px solid var(--primary);
    padding-right: 10px;
}

.search-box {
    display: grid;
    grid-template-columns: 2fr 1fr auto;
    gap: 12px;
}

@media (max-width: 768px) {
    .search-box {
        grid-template-columns: 1fr;
    }
}

input, select {
    width: 100%;
    box-sizing: border-box;
    padding: 12px 16px;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    font-family: 'Cairo', sans-serif;
    font-size: 0.95rem;
    background: #f8fafc;
}

input:focus, select:focus {
    outline: none;
    border-color: var(--primary);
    background: #fff;
}

button, .btn-action {
    background: var(--primary);
    color: white;
    cursor: pointer;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    padding: 12px 20px;
    border-radius: 10px;
    font-family: 'Cairo', sans-serif;
    font-weight: 700;
    border: none;
    transition: background 0.2s;
}

button:hover {
    background: var(--primary-hover);
}

.scholarship-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.scholarship-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid var(--border-color);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.scholarship-card h3 {
    color: var(--primary);
    margin-top: 0;
    font-size: 1.25rem;
    font-weight: 700;
}

.scholarship-card p {
    margin: 6px 0;
    font-size: 0.9rem;
    color: var(--text-muted);
}

.scholarship-card p strong {
    color: var(--text-main);
}

.percentage-badge {
    background: #fef3c7;
    color: #92400e;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 700;
    margin: 10px 0;
    display: block;
}

.status-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    background: #e0e7ff;
    color: #3730a3;
    margin-bottom: 12px;
}

.actions-row {
    display: flex;
    gap: 8px;
    margin-top: 15px;
    flex-wrap: wrap;
}

.btn-details {
    background: #0284c7;
    color: white;
    text-align: center;
    padding: 10px;
    border-radius: 8px;
    font-size: 0.85rem;
    text-decoration: none;
    font-weight: 600;
    flex: 1;
}

.btn-details:hover {
    background: #0369a1;
}

.btn-apply {
    background: var(--success);
    color: white;
    text-align: center;
    padding: 10px;
    border-radius: 8px;
    font-size: 0.85rem;
    text-decoration: none;
    font-weight: 600;
    flex: 1;
}

.btn-apply:hover {
    background: var(--success-hover);
}

footer {
    text-align: center;
    padding: 30px;
    color: var(--text-muted);
    font-size: 0.9rem;
    border-top: 1px solid var(--border-color);
    margin-top: 40px;
    background: white;
}
</style>
</head>

<body>

<header>
    <h1>🌍 منح العالم</h1>
    <p>بوابة البحث الذكية عن المنح الدراسية والفرص الأكاديمية العالمية</p>
    <p style="font-size: 0.85rem; opacity: 0.8; margin-top: 8px;">تصميم وتطوير: السيد لوكا</p>
</header>

<div class="container">

<!-- صندوق البحث -->
<div class="card">
    <h2>🔍 ابحث عن فرصتك الدراسية</h2>
    <form method="GET" action="/" class="search-box">
        <input name="q" placeholder="ابحث باسم المنحة، الدولة، أو التخصص..." value="{{ request.args.get('q', '') }}">

        <select name="continent">
            <option value="">جميع القارات</option>
            <option {% if request.args.get('continent') == 'آسيا' %}selected{% endif %}>آسيا</option>
            <option {% if request.args.get('continent') == 'أوروبا' %}selected{% endif %}>أوروبا</option>
            <option {% if request.args.get('continent') == 'أمريكا الشمالية' %}selected{% endif %}>أمريكا الشمالية</option>
        </select>

        <button type="submit">بحث متقدم</button>
    </form>
</div>

<h2>🎓 قائمة المنح المتاحة (بكالوريوس ودراسات عليا)</h2>

<div class="scholarship-grid">
{% for s in scholarships %}
<div class="scholarship-card">
    <div>
        <span class="status-badge">{{ s.status }}</span>
        <h3>{{ s.name }}</h3>
        <p><strong>الدولة:</strong> {{ s.country or "غير محددة" }}</p>
        <p><strong>الدرجات المتاحة:</strong> {{ s.degree or "بكالوريوس والدراسات العليا" }}</p>
        <p><strong>التخصصات:</strong> {{ s.fields or "غير محددة" }}</p>
        
        <div class="percentage-badge">
            📊 النسبة / المعدل المطلوب: {{ s.percentage_minimum or s.gpa_minimum or "راجع الإعلان الرسمي" }}
        </div>
    </div>
    
    <div class="actions-row">
        <a href="/scholarship/{{ s.id }}" class="btn-details">📖 قراءة المقال والتفاصيل</a>
        <a href="/register?scholarship_id={{ s.id }}" class="btn-apply">📝 التقديم الفوري</a>
    </div>
</div>
{% else %}
<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">لا توجد نتائج مطابقة لبحثك.</p>
{% endfor %}
</div>

<!-- قسم التسجيل -->
<div class="card" id="register-section" style="margin-top: 40px;">
    <h2>📝 تسجيل طالب جديد</h2>

    <form action="/register" method="POST">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
            <input name="full_name" placeholder="الاسم الكامل" required style="margin:0;">
            <input name="email" type="email" placeholder="البريد الإلكتروني" required style="margin:0;">
        </div>

        <select name="scholarship_id" style="margin-bottom: 15px;">
            <option value="">اختر المنحة المطلوبة (اختياري)</option>
            {% for s in all_scholarships %}
            <option value="{{ s.id }}" {% if request.args.get('scholarship_id')|int == s.id %}selected{% endif %}>{{ s.name }}</option>
            {% endfor %}
        </select>

        <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 20px; font-size: 0.9rem; cursor: pointer;">
            <input type="checkbox" name="consent" value="yes" required style="width: auto; margin:0;">
            أوافق على استخدام بياناتي لإدارة طلب التسجيل الخاص بي.
        </label>

        <button type="submit" style="width: 100%;">إرسال طلب التسجيل</button>
    </form>
</div>

</div>

<footer>
    جميع الحقوق محفوظة © 2026 - تم التطوير بكل إتقان بواسطة السيد لوكا
</footer>

</body>
</html>
"""

# قالب صفحة المقال وقراءة تفاصيل المنحة منفصلة
DETAIL_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ scholarship.name }} | تفاصيل المنحة</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
body { font-family: 'Cairo', sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 20px; line-height: 1.8; }
.container { max-width: 800px; margin: 40px auto; background: white; padding: 35px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
h1 { color: #4f46e5; margin-top: 0; font-size: 1.8rem; }
.badge { display: inline-block; background: #e0e7ff; color: #3730a3; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; margin-bottom: 15px; }
.section { margin: 20px 0; padding: 15px; background: #f8fafc; border-radius: 10px; border-right: 4px solid #4f46e5; }
.btn-group { display: flex; gap: 15px; margin-top: 30px; }
.btn { flex: 1; padding: 12px; text-align: center; border-radius: 10px; font-weight: bold; text-decoration: none; font-size: 1rem; }
.btn-primary
