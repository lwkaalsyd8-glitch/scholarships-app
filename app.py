import time
import threading
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# قاعدة البيانات الأساسية للمنح العالمية
BASE_SCHOLARSHIPS = [
    {
        "id": 1,
        "name": "المنح التركية (Türkiye Bursları)",
        "country": "تركيا",
        "levels": ["بكالوريوس", "ماجستير", "دكتوراه"],
        "funding": "تمويل كامل (رسوم الدراسة، سكن جامعي، راتب شهري، تأمين صحي، تذاكر طيران، وسنة لغة تركية)",
        "universities": "أكثر من 100 جامعة حكومية تركية",
        "requirements": "معدل أكاديمي جيد، جواز سفر ساري، لا يشترط شهادة لغة عند التقديم",
        "deadline": "يناير - فبراير سنوياً",
        "link": "https://www.turkiyeburslari.gov.tr"
    },
    {
        "id": 2,
        "name": "منحة الحكومة الصينية (CSC)",
        "country": "الصين",
        "levels": ["بكالوريوس", "ماجستير", "دكتوراه"],
        "funding": "تمويل كامل (إعفاء من الرسوم، سكن مجاني، راتب شهري، تأمين طبي)",
        "universities": "أكثر من 270 جامعة صينية مرموقة",
        "requirements": "جواز سفر ساري، شهادة تخرج، شهادة إثبات لغة التدريس (MOI)",
        "deadline": "ديسمبر - أبريل سنوياً",
        "link": "https://www.campuschina.org"
    },
    {
        "id": 3,
        "name": "منحة الحكومة الروسية (Russian Government Scholarship)",
        "country": "روسيا",
        "levels": ["بكالوريوس", "ماجستير", "دكتوراه", "تخصص طب/هندسة"],
        "funding": "تمويل كامل للرسوم الدراسية + سكن جامعي + راتب شهري رمزي + سنة تحضيرية للغة الروسية",
        "universities": "جامعات روسية كبرى (مثل جامعة موسكو الحكومية، جامعة سانت بطرسبرغ)",
        "requirements": "شهادة الثانوية أو البكالوريوس، جواز سفر، لا تشترط اللغة الروسية مسبقاً",
        "deadline": "سبتمبر - يناير سنوياً",
        "link": "https://education-in-russia.com"
    },
    {
        "id": 4,
        "name": "منحة فولبرايت الأمريكية (Fulbright Program)",
        "country": "الولايات المتحدة الأمريكية",
        "levels": ["ماجستير", "دكتوراه"],
        "funding": "تمويل كامل (الرسوم الدراسية، المعيشة، تذاكر السفر، والتأمين الصحي)",
        "universities": "الجامعات الأمريكية المعتمدة",
        "requirements": "درجة البكالوريوس بتقدير ممتاز/جيد جداً، اختبارات الكفاءة في اللغة الإنجليزية (TOEFL/IELTS)",
        "deadline": "فبراير - مايو حسب الدولة",
        "link": "https://foreign.fulbrightonline.org"
    },
    {
        "id": 5,
        "name": "منحة الحكومة البريطانية (Chevening Scholarship)",
        "country": "المملكة المتحدة (بريطانيا)",
        "levels": ["ماجستير"],
        "funding": "تمويل كامل للرسوم الدراسية، بدل معيشة شهري، وتذاكر الطيران",
        "universities": "جميع جامعات المملكة المتحدة",
        "requirements": "خبرة عمل لا تقل عن سنتين، شهادة بكالوريوس، استيفاء متطلبات اللغة الإنجليزية",
        "deadline": "أغسطس - نوفمبر سنوياً",
        "link": "https://www.chevening.org"
    },
    {
        "id": 6,
        "name": "منحة داد الألمانية (DAAD)",
        "country": "ألمانيا",
        "levels": ["ماجستير", "دكتوراه"],
        "funding": "تمويل كامل مع راتب شهري مجزي (حوالي 934 يورو للماجستير و1300 يورو للدكتوراه)",
        "universities": "الجامعات الألمانية الحكومية",
        "requirements": "شهادة بكالوريوس، خبرة عمل عملية لبعض التخصصات، إتقان الإنجليزية أو الألمانية",
        "deadline": "أغسطس - أكتوبر سنوياً",
        "link": "https://www.daad.de"
    },
    {
        "id": 7,
        "name": "منحة الحكومة الكورية (GKS)",
        "country": "كوريا الجنوبية",
        "levels": ["بكالوريوس", "ماجستير", "دكتوراه"],
        "funding": "تمويل كامل (تذاكر الطيران، الراتب الشهري، الرسوم، وسنة لغة كاملة)",
        "universities": "أفضل الجامعات الكورية (KAIST، جامعة سيول الوطنية)",
        "requirements": "معدل أكاديمي مرتفع، اجتياز الفحص الطبي، إرسال المستندات عبر السفارة أو الجامعة",
        "deadline": "سبتمبر (للبكالوريوس) / فبراير (للدراسات العليا)",
        "link": "https://www.studyinkorea.go.kr"
    },
    {
        "id": 8,
        "name": "منحة الحكومة اليابانية (MEXT)",
        "country": "اليابان",
        "levels": ["بكالوريوس", "ماجستير", "دكتوراه"],
        "funding": "تمويل شامل الرسوم وراتب شهري وتذاكر السفر ذهاباً وعودة",
        "universities": "الجامعات اليابانية الوطنية",
        "requirements": "عمر محدد حسب البرنامج، اجتياز اختبارات القبول واللغة والمقابلة الشخصية",
        "deadline": "أبريل - يونيو سنوياً",
        "link": "https://www.studyinjapan.go.jp"
    },
    {
        "id": 9,
        "name": "منحة إيراسموس موندوس (Erasmus Mundus)",
        "country": "الاتحاد الأوروبي (عدة دول)",
        "levels": ["ماجستير"],
        "funding": "تمويل كامل شامل الرسوم وراتب شهري (1400 يورو) والتنقل بين دول أوروبا",
        "universities": "تحالف جامعات أوروبية مشتركة",
        "requirements": "بكالوريوس، رسالة دافع قوية، خطابات توصية، إثبات اللغة الإنجليزية",
        "deadline": "أكتوبر - يناير سنوياً",
        "link": "https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en"
    },
    {
        "id": 10,
        "name": "منح الجامعات السعودية الحكومية",
        "country": "السعودية",
        "levels": ["بكالوريوس", "ماجستير", "دكتوراه"],
        "funding": "إعفاء كامل من الرسوم، سكن مجاني، مكافأة شهرية، وتذاكر طيران",
        "universities": "جامعة الملك سعود، الملك عبدالعزيز، أم القرى، وغيرها",
        "requirements": "شهادات معتمدة، حسن سيرة وسلوك، التقديم عبر منصة ادرس في السعودية",
        "deadline": "مفتوح على مدار العام حسب الفترات",
        "link": "https://studyinsaudi.moe.gov.sa"
    }
]

# متغيرات حالة التحديث اليومي
SCHOLARSHIPS = list(BASE_SCHOLARSHIPS)
LAST_UPDATED = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# رابط JSON خارجي اختياري (يمكنك وضع رابط ملف Raw من GitHub لتحديث المنح عن بُعد دون تعديل التطبيق)
REMOTE_DATA_URL = ""

def fetch_daily_updates():
    """دالة تقوم بفحص وتحديث قاعدة البيانات يومياً"""
    global SCHOLARSHIPS, LAST_UPDATED
    updated_list = list(BASE_SCHOLARSHIPS)
    
    if REMOTE_DATA_URL:
        try:
            response = requests.get(REMOTE_DATA_URL, timeout=10)
            if response.status_code == 200:
                extra_data = response.json()
                if isinstance(extra_data, list):
                    updated_list.extend(extra_data)
        except Exception as e:
            print(f"تعذر جلب التحديث الخارجي: {e}")
            
    SCHOLARSHIPS = updated_list
    LAST_UPDATED = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[تم التحديث بنجاح] التوقيت: {LAST_UPDATED} | إجمالي المنح: {len(SCHOLARSHIPS)}")

def daily_scheduler():
    """خيط يعمل في الخلفية لتشغيل التحديث كل 24 ساعة"""
    while True:
        fetch_daily_updates()
        time.sleep(86400)  # انتظار 24 ساعة (86400 ثانية)

# تشغيل المجدول اليومي في الخلفية عند بدء التطبيق
threading.Thread(target=daily_scheduler, daemon=True).start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دليل المنح الدراسية العالمية الشامل</title>
    <style>
        body { font-family: Tahoma, Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 15px; color: #333; }
        .header { background: #117a65; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        .update-bar { background: #d1f2eb; color: #0e6251; padding: 10px 15px; border-radius: 8px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; flex-wrap: wrap; gap: 10px; }
        .refresh-btn { background: #0e6251; color: white; text-decoration: none; padding: 5px 12px; border-radius: 5px; font-weight: bold; }
        .search-box { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px; }
        input, select, button { padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; flex: 1; min-width: 150px; }
        button { background: #117a65; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background: #0e6251; }
        .card { background: white; border-radius: 10px; padding: 18px; margin-bottom: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border-right: 5px solid #117a65; }
        .card h3 { margin-top: 0; color: #117a65; }
        .badge { display: inline-block; background: #e8f8f5; color: #117a65; padding: 4px 10px; border-radius: 15px; font-size: 12px; margin-left: 5px; font-weight: bold; }
        .info-row { margin: 8px 0; font-size: 14px; line-height: 1.6; }
        .btn-link { display: inline-block; margin-top: 10px; background: #27ae60; color: white; text-decoration: none; padding: 8px 15px; border-radius: 6px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>🌍 دليل المنح الدراسية العالمية الشامل</h2>
        <p>ابحث في مئات المنح، الجامعات، والدول المتاحة لجميع طلاب العالم</p>
    </div>

    <div class="update-bar">
        <span>🕒 آخر تحديث تلقائي للبيانات: <strong>{{ last_updated }}</strong> (يُحدّث يومياً)</span>
        <a href="/refresh" class="refresh-btn">تحديث الآن 🔄</a>
    </div>

    <form class="search-box" method="GET">
        <input type="text" name="q" placeholder="ابحث باسم الدولة أو المنحة (مثلاً: روسيا، بريطانيا، أمريكا)..." value="{{ query }}">
        <select name="level">
            <option value="">كل الدرجات العلمية</option>
            <option value="بكالوريوس" {% if level == 'بكالوريوس' %}selected{% endif %}>بكالوريوس</option>
            <option value="ماجستير" {% if level == 'ماجستير' %}selected{% endif %}>ماجستير</option>
            <option value="دكتوراه" {% if level == 'دكتوراه' %}selected{% endif %}>دكتوراه</option>
        </select>
        <button type="submit">بحث وفلترة</button>
    </form>

    {% if scholarships %}
        {% for s in scholarships %}
        <div class="card">
            <h3>{{ s.name }}</h3>
            <div>
                <span class="badge">🌍 {{ s.country }}</span>
                {% for lvl in s.levels %}
                    <span class="badge">📚 {{ lvl }}</span>
                {% endfor %}
            </div>
            <div class="info-row"><strong>💰 التمويل:</strong> {{ s.funding }}</div>
            <div class="info-row"><strong>🏛️ الجامعات:</strong> {{ s.universities }}</div>
            <div class="info-row"><strong>📋 الشروط الأساسية:</strong> {{ s.requirements }}</div>
            <div class="info-row"><strong>⏰ موعد التقديم:</strong> {{ s.deadline }}</div>
            <a href="{{ s.link }}" target="_blank" class="btn-link">الموقع الرسمي للمنحة 🔗</a>
        </div>
        {% endfor %}
    {% else %}
        <p style="text-align:center;">لا توجد منح مطابقة لبحثك حالياً.</p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    query = request.args.get("q", "").strip().lower()
    level = request.args.get("level", "").strip()
    
    filtered = []
    for s in SCHOLARSHIPS:
        match_q = (not query) or (query in s["name"].lower()) or (query in s["country"].lower()) or (query in s["universities"].lower())
        match_lvl = (not level) or any(level in l for l in s["levels"])
        if match_q and match_lvl:
            filtered.append(s)
            
    return render_template_string(
        HTML_TEMPLATE,
        scholarships=filtered,
        query=request.args.get("q", ""),
        level=level,
        last_updated=LAST_UPDATED
    )

@app.route("/refresh")
def manual_refresh():
    fetch_daily_updates()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)

