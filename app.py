from flask import Flask, render_template_string
import os

app = Flask(__name__)

# قائمة المنح الدراسية لعرضها مباشرة على الموقع
scholarships_data = [
    {
        "id": 1,
        "name": "منحة تركيا (Türkiye Bursları)",
        "country": "تركيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "funding": "تمويل كامل (رسوم، سكن، تذاكر طيران، راتب شهري)",
        "deadline": "فبراير من كل عام"
    },
    {
        "id": 2,
        "name": "منحة الحكومة المجرية (Stipendium Hungaricum)",
        "country": "المجر",
        "degree": "بكالوريوس، ماجستير",
        "funding": "تمويل كامل مع سكن جامعي وتأمين صحي",
        "deadline": "يناير من كل عام"
    }
]

@app.route('/')
def home():
    # تصميم HTML بسيط ومباشر داخل الكود ليظهر فوراً على موقعك
    html_template = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>منصة المنح الدراسية</title>
        <style>
            body { font-family: Tahoma, sans-serif; background-color: #f4f6f9; color: #333; padding: 20px; margin: 0; }
            h1 { color: #2c3e50; text-align: center; }
            .card { background: white; padding: 15px; margin: 15px auto; max-width: 600px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            h3 { color: #2980b9; margin-top: 0; }
            p { margin: 5px 0; }
        </style>
    </head>
    <body>
        <h1>🎓 منصة المنح الدراسية</h1>
        <p style="text-align: center;">أحدث المنح الدولية المتاحة للطلاب:</p>
        
        {% for s in scholarships %}
        <div class="card">
            <h3>{{ s.name }}</h3>
            <p><strong>الدولة:</strong> {{ s.country }}</p>
            <p><strong>المستويات:</strong> {{ s.degree }}</p>
            <p><strong>التنويل:</strong> {{ s.funding }}</p>
            <p><strong>موعد التسجيل:</strong> {{ s.deadline }}</p>
        </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html_template, scholarships=scholarships_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
