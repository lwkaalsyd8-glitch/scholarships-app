from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

# قاعدة بيانات شاملة لأوروبا، آسيا، وأمريكا مع الروابط الرسمية ومعدلات القبول
scholarships_db = [
    {
        "name": "منحة تركيا (Türkiye Bursları)",
        "country": "تركيا",
        "continent": "أوروبا وآسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "70% فما فوق (80% للطب)",
        "majors": "هندسة، طب، علوم، إنسانيات، حاسب آلي",
        "funding": "تمويل كامل (رسوم، سكن، تذاكر، راتب، سنة لغة)",
        "deadline": "فبراير 2027",
        "link": "https://www.turkiyeburslari.gov.tr"
    },
    {
        "name": "منحة الحكومة المجرية (Stipendium Hungaricum)",
        "country": "المجر",
        "continent": "أوروبا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "75% (تقدير جيد جداً)",
        "majors": "هندسة، إدارة أعمال، طب، زراعة، علوم طبيعية",
        "funding": "تمويل كامل مع سكن وتأمين صحي وراتب شهري",
        "deadline": "يناير 2027",
        "link": "https://stipendiumhungaricum.hu"
    },
    {
        "name": "منحة الحكومة الألمانية (DAAD)",
        "country": "ألمانيا",
        "continent": "أوروبا",
        "degree": "ماجستير، دكتوراه",
        "gpa": "80% أو جيد جداً مرتفع",
        "majors": "هندسة، طاقة متجددة، علوم بيئية، اقتصاد",
        "funding": "راتب شهري، تأمين صحي وتذاكر سفر",
        "deadline": "أكتوبر 2027",
        "link": "https://www.daad.de"
    },
    {
        "name": "منحة الحكومة الإيطالية (MAECI)",
        "country": "إيطاليا",
        "continent": "أوروبا",
        "degree": "ماجستير، دكتوراه، فنون",
        "gpa": "75% فما فوق",
        "majors": "هندسة، تصميم، فنون، عمارة، علوم سياسية",
        "funding": "إعفاء من الرسوم وراتب شهري وتأمين صحي",
        "deadline": "مايو 2027",
        "link": "https://studyinitaly.esteri.it"
    },
    {
        "name": "منحة فولبرايت الأمريكية (Fulbright)",
        "country": "الولايات المتحدة الأمريكية",
        "continent": "أمريكا الشمالية",
        "degree": "ماجستير، أبحاث",
        "gpa": "80% فما فوق مع لغة إنجليزية ممتازة (TOEFL/IELTS)",
        "majors": "جميع التخصصات الأكاديمية والمهنية",
        "funding": "تغطية كاملة للرسوم، المعيشة، التأمين وتذاكر السفر",
        "deadline": "مايو 2027",
        "link": "https://foreign.fulbrightonline.org"
    },
    {
        "name": "منحة جامعة هارفارد (Harvard University Scholarships)",
        "country": "الولايات المتحدة الأمريكية",
        "continent": "أمريكا الشمالية",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "90% فما فوق (امتياز مع مرتبة الشرف)",
        "majors": "إدارة أعمال، طب، قانون، هندسة، علوم",
        "funding": "تعتمد على الحاجة المالية (تغطية تصل إلى 100%)",
        "deadline": "ديسمبر 2027",
        "link": "https://college.harvard.edu/financial-aid"
    },
    {
        "name": "منحة الحكومة الصينية (CSC)",
        "country": "الصين",
        "continent": "آسيا",
        "degree": "جميع المستويات",
        "gpa": "70% فما فوق",
        "majors": "ذكاء اصطناعي، هندسة برمجيات، طب، لغات",
        "funding": "تمويل شامل وكامل الرسوم والإقامة والراتب",
        "deadline": "مارس 2027",
        "link": "https://www.campuschina.org"
    },
    {
        "name": "منحة حكومة كوريا الجنوبية (GKS)",
        "country": "كوريا الجنوبية",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "80% (أو معدل تراكمي 2.64/4.0)",
        "majors": "هندسة، تكنولوجيا، إدارة، رعاية صحية",
        "funding": "تذاكر طيران، رسوم الدراسة، راتب شهري وسكن",
        "deadline": "مارس 2027",
        "link": "https://www.studyinkorea.go.kr"
    },
    {
        "name": "منحة الحكومة الروسية",
        "country": "روسيا",
        "continent": "أوروبا وآسيا",
        "degree": "جميع المستويات",
        "gpa": "65% فما فوق (مقبول فما فوق)",
        "majors": "طيران وفضاء، طب بشري، هندسة نووية، برمجة",
        "funding": "مجانية بالكامل (تدرس اللغة الروسية سنة أولى)",
        "deadline": "يونيو 2027",
        "link": "https://education-in-russia.com"
    }
]

@app.route('/')
def home():
    search_query = request.args.get('q', '').strip()
    selected_country = request.args.get('country', '').strip()
    
    filtered_scholarships = scholarships_db
    if search_query:
        filtered_scholarships = [s for s in filtered_scholarships if search_query.lower() in s['name'].lower() or search_query in s['country'] or search_query in s['majors'].lower()]
    if selected_country and selected_country != 'الكل':
        filtered_scholarships = [s for s in filtered_scholarships if s['country'] == selected_country]

    html_template = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>منصة المنح العالمية الشاملة (أوروبا، آسيا، أمريكا)</title>
        <style>
            :root { --primary: #2563
