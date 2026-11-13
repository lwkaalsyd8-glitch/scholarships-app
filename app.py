from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

# قاعدة بيانات واسعة تشمل منح من مختلف دول العالم
scholarships_db = [
    {
        "name": "منحة تركيا (Türkiye Bursları)",
        "country": "تركيا",
        "continent": "آسيا وأوروبا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "funding": "تمويل كامل (رسوم، سكن، تذاكر، راتب)",
        "deadline": "فبراير 2027"
    },
    {
        "name": "منحة الحكومة المجرية (Stipendium Hungaricum)",
        "country": "المجر",
        "continent": "أوروبا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "funding": "تمويل كامل مع سكن وتأمين صحي وراتب",
        "deadline": "يناير 2027"
    },
    {
        "name": "منحة الحكومة الإيطالية (MAECI)",
        "country": "إيطاليا",
        "continent": "أوروبا",
        "degree": "ماجستير، دكتوراه",
        "funding": "إعفاء من الرسوم وراتب شهري وتأمين",
        "deadline": "مايو 2027"
    },
    {
        "name": "منحة جامعة هداية (Indonesia Scholarship)",
        "country": "إندونيسيا",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير",
        "funding": "الرسوم الدراسية وسكن جامعي ومصروف جيب",
        "deadline": "أبريل 2027"
    },
    {
        "name": "منحة الحكومة الصينية (CSC)",
        "country": "الصين",
        "continent": "آسيا",
        "degree": "جميع المستويات",
        "funding": "تمويل شامل وكامل الرسوم والإقامة",
        "deadline": "مارس 2027"
    },
    {
        "name": "منحة حكومة كوريا الجنوبية (GKS)",
        "country": "كوريا الجنوبية",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "funding": "تذاكر طيران، رسوم الدراسة، راتب شهري وسكن",
        "deadline": "مارس 2027"
    },
    {
        "name": "منحة الحكومة الألمانية (DAAD)",
        "country": "ألمانيا",
        "continent": "أوروبا",
        "degree": "ماجستير، دكتوراه",
        "funding": "راتب شهري، تأمين صحي وتذاكر سفر",
        "deadline": "أكتوبر 2027"
    },
    {
        "name": "منحة الحكومة الروسية",
        "country": "روسيا",
        "continent": "أوروبا وآسيا",
        "degree": "جميع المستويات",
        "funding": "مجانية بالكامل (تدرس اللغة أولاً)",
        "deadline": "يونيو 2027"
    },
    {
        "name": "منحة جامعة أكسفورد (Clarendon)",
        "country": "المملكة المتحدة",
        "continent": "أوروبا",
        "degree": "دراسات عليا (ماجستير ودكتوراه)",
        "funding": "تغطية كاملة للرسوم الدراسية مع منحة معيشية",
        "deadline": "يناير 2027"
    },
    {
        "name": "منحة الحكومة الفرنسية (Eiffel)",
        "country": "فرنسا",
        "continent": "أوروبا",
        "degree": "ماجستير، دكتوراه",
        "funding": "راتب شهري كبير وتذاكر وتأمين صحي",
        "deadline": "يناير 2027"
    },
    {
        "name": "منحة جامعة محمد بن زايد للذكاء الاصطناعي",
        "country": "الإمارات",
        "continent": "آسيا (عربي)",
        "degree": "ماجستير، دكتوراه",
        "funding": "تمويل كامل، سكن مجاني وراتب شهري",
        "deadline": "أبريل 2027"
    }
]

@app.route('/')
def home():
    search_query = request.args.get('q', '').strip()
    selected_country = request.args.get('country', '').strip()
    
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
        <title>منصة المنح العالمية الشاملة</title>
        <style>
            :root { --primary: #2563eb; --bg: #f8fafc; --text: #1e293b; --card-bg: #ffffff; }
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 20px; }
            header { text-align: center; margin-bottom: 30px; }
            h1 { color: var(--primary); margin-bottom: 5px; }
            .subtitle { color: #64748b; font-size: 14px; }
            
            .filter-container { background: var(--card-bg); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); max-width: 750px; margin: 0 auto 25px auto; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
            input, select { padding: 10px 15px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; flex: 1; min-width: 200px; }
            button { background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
            button:hover { background: #1d4ed8; }

            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 20px; max-width: 1000px; margin: 0 auto; }
            .card { background: var(--card-bg); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-right: 5px solid var(--primary); transition: transform 0.2s; }
            .card:hover { transform: translateY(-3px); }
            h3 { color: var(--primary); margin-top: 0; font-size: 18px; }
            p { margin: 8px 0; font-size: 14px; }
            .badge { display: inline-block; background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 10px; }
            .no-result { text-align: center; color: #64748b; grid-column: 1 / -1; padding: 40px; }
        </style>
    </head>
    <body>
        <header>
            <h1>🌍 بوابة المنح الدراسية العالمية</h1>
            <p class="subtitle">دليلك الشامل لأبرز المنح الدولية والمحتوى المحدث للفرص الدراسية</p>
        </header>

        <form method="GET" class="filter-container">
            <input type="text" name="q" placeholder="ابحث باسم المنحة أو الدولة..." value="{{ search_query }}">
            <select name="country">
                <option value="الكل">كل الدول (عرض الكل)</option>
                <option value="تركيا" {% if selected_country == 'تركيا' %}selected{% endif %}>تركيا</option>
                <option value="المجر" {% if selected_country == 'المجر' %}selected{% endif %}>المجر</option>
                <option value="إيطاليا" {% if selected_country == 'إيطاليا' %}selected{% endif %}>إيطاليا</option>
                <option value="إندونيسيا" {% if selected_country == 'إندونيسيا' %}selected{% endif %}>إندونيسيا</option>
                <option value="الصين" {% if selected_country == 'الصين' %}selected{% endif %}>الصين</option>
                <option value="كوريا الجنوبية" {% if selected_country == 'كوريا الجنوبية' %}selected{% endif %}>كوريا الجنوبية</option>
                <option value="ألمانيا" {% if selected_country == 'ألمانيا' %}selected{% endif %}>ألمانيا</option>
                <option value="روسيا" {% if selected_country == 'روسيا' %}selected{% endif %}>روسيا</option>
                <option value="المملكة المتحدة" {% if selected_country == 'المملكة المتحدة' %}selected{% endif %}>المملكة المتحدة</option>
                <option value="فرنسا" {% if selected_country == 'فرنسا' %}selected{% endif %}>فرنسا</option>
                <option value="الإمارات" {% if selected_country == 'الإمارات' %}selected{% endif %}>الإمارات</option>
            </select>
            <button type="submit">بحث وتصفية</button>
        </form>

        <div class="grid">
            {% if scholarships %}
                {% for s in scholarships %}
                <div class="card">
                    <span class="badge">{{ s.country }} ({{ s.continent }})</span>
                    <h3>{{ s.name }}</h3>
                    <p><strong>المستويات:</strong> {{ s.degree }}</p>
                    <p><strong>التمويل:</strong> {{ s.funding }}</p>
                    <p><strong>ميعاد التسجيل:</strong> 📅 {{ s.deadline }}</p>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-result">
                    <h3>عذراً، لم نجد نتائج مطابقة لبحثك!</h3>
                    <p>جرب البحث بكلمات أخرى أو اختر دولة مختلفة من القائمة.</p>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, scholarships=filtered_scholarships, search_query=search_query, selected_country=selected_country)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
