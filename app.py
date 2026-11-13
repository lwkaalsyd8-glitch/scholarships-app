from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

# قاعدة بيانات متكاملة للمنح الدراسية العالمية مع تصنيفات دقيقة
scholarships_db = [
    {
        "name": "منحة تركيا (Türkiye Bursları)",
        "country": "تركيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "funding": "تمويل كامل (رسوم، سكن، تذاكر طيران، راتب)",
        "deadline": "فبراير 2027",
        "category": "كامل"
    },
    {
        "name": "منحة الحكومة المجرية (Stipendium Hungaricum)",
        "country": "المجر",
        "degree": "بكالوريوس، ماجستير",
        "funding": "تمويل كامل مع سكن وتأمين صحي",
        "deadline": "يناير 2027",
        "category": "كامل"
    },
    {
        "name": "منحة الحكومة الإيطالية (MAECI)",
        "country": "إيطاليا",
        "degree": "ماجستير، دكتوراه",
        "funding": "إعفاء من الرسوم وراتب شهري",
        "deadline": "مايو 2027",
        "category": "جزئي"
    },
    {
        "name": "منحة جامعة هداية (Indonesia Scholarship)",
        "country": "إندونيسيا",
        "degree": "بكالوريوس وماجستير",
        "funding": "رسوم الدراسية وسكن جامعي",
        "deadline": "أبريل 2027",
        "category": "كامل"
    }
]

@app.route('/')
def home():
    # استقبال خيارات البحث والفلترة من المستخدم
    search_query = request.args.get('q', '').strip()
    selected_country = request.args.get('country', '').strip()
    
    # فلترة المنح بناءً على البحث أو الدولة
    filtered_scholarships = scholarships_db
    if search_query:
        filtered_scholarships = [s for s in filtered_scholarships if search_query.lower() in s['name'].lower() or search_query in s['country']]
    if selected_country and selected_country != 'الكل':
        filtered_scholarships = [s for s in filtered_scholarships if s['country'] == selected_country]

    html_template = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>منصة المنح العالمية الاحترافية</title>
        <style>
            :root { --primary: #2563eb; --bg: #f8fafc; --text: #1e293b; --card-bg: #ffffff; }
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 20px; }
            header { text-align: center; margin-bottom: 30px; }
            h1 { color: var(--primary); margin-bottom: 5px; }
            .subtitle { color: #64748b; font-size: 14px; }
            
            /* تصميم شريط البحث والفلترة */
            .filter-container { background: var(--card-bg); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); max-width: 700px; margin: 0 auto 25px auto; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
            input, select { padding: 10px 15px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; flex: 1; min-width: 200px; }
            button { background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
            button:hover { background: #1d4ed8; }

            /* شبكة عرض المنح */
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 900px; margin: 0 auto; }
            .card { background: var(--card-bg); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-right: 5px solid var(--primary); }
            h3 { color: var(--primary); margin-top: 0; }
            p { margin: 8px 0; font-size: 14px; }
            .badge { display: inline-block; background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 10px; }
            .no-result { text-align: center; color: #64748b; grid-column: 1 / -1; padding: 30px; }
        </style>
    </head>
    <body>
        <header>
            <h1>🎓 بوابة المنح الدراسية العالمية</h1>
            <p class="subtitle">تحديث يومي لأحدث الفرص والمنح الدولية للطلاب</p>
        </header>

        <!-- صندوق البحث والفلترة الفورية -->
        <form method="GET" class="filter-container">
            <input type="text" name="q" placeholder="ابحث باسم المنحة أو الدولة..." value="{{ search_query }}">
            <select name="country">
                <option value="الكل">كل الدول</option>
                <option value="تركيا" {% if selected_country == 'تركيا' %}selected{% endif %}>تركيا</option>
                <option value="المجر" {% if selected_country == 'المجر' %}selected{% endif %}>المجر</option>
                <option value="إيطاليا" {% if selected_country == 'إيطاليا' %}selected{% endif %}>إيطاليا</option>
                <option value="إندونيسيا" {% if selected_country == 'إندونيسيا' %}selected{% endif %}>إندونيسيا</option>
            </select>
            <button type="submit">بحث وتصفية</button>
        </form>

        <!-- عرض المنح الدراسية -->
        <div class="grid">
            {% if scholarships %}
                {% for s in scholarships %}
                <div class="card">
                    <span class="badge">{{ s.country }}</span>
                    <h3>{{ s.name }}</h3>
                    <p><strong>المستويات:</strong> {{ s.degree }}</p>
                    <p><strong>التمويل:</strong> {{ s.funding }}</p>
                    <p><strong>ميعاد التسجيل:</strong> 📅 {{ s.deadline }}</p>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-result">
                    <h3>عذراً، لم نجد نتائج مطابقة لبحثك!</h3>
                    <p>جرب البحث بكلمات أخرى أو اختر دولة مختلفة.</p>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, scholarships=filtered_scholarships, search_query=search_query, selected_country=selected_country)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
