
from flask import Flask, render_template_string, request

app = Flask(__name__)

# ==========================================
# قاعدة بيانات المنح الدراسية العالمية
# المعدلات إرشادية وليست شروط قبول موحدة
# ==========================================

scholarships_db = [

    # EUROPE
    {
        "name": "Türkiye Bursları",
        "country": "تركيا",
        "continent": "أوروبا وآسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "70% للبكالوريوس، 75% للدراسات العليا، 90% للطب",
        "majors": "الطب، الهندسة، الذكاء الاصطناعي، الاقتصاد، القانون، العلوم، الفنون",
        "funding": "تمويل كامل، رسوم دراسية، سكن، راتب شهري، تذاكر طيران، تأمين صحي، سنة لغة تركية.",
        "link": "https://www.turkiyeburslari.gov.tr",
        "type": "ممولة بالكامل"
    },
    {
        "name": "Stipendium Hungaricum",
        "country": "المجر",
        "continent": "أوروبا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "غالباً 70% فما فوق حسب الجامعة",
        "majors": "الطب، طب الأسنان، الصيدلة، الهندسة، الزراعة، الاقتصاد، علوم الحاسوب",
        "funding": "إعفاء من الرسوم، راتب شهري، مساهمة في السكن، تأمين صحي.",
        "link": "https://stipendiumhungaricum.hu",
        "type": "ممولة بالكامل أو جزئياً"
    },
    {
        "name": "DAAD Scholarship",
        "country": "ألمانيا",
        "continent": "أوروبا",
        "degree": "ماجستير، دكتوراه",
        "gpa": "غالباً جيد جداً أو سجل أكاديمي قوي",
        "majors": "الهندسة، الطب، الطاقة، علوم الحاسوب، الاقتصاد، البيئة، العلوم",
        "funding": "راتب شهري، تأمين صحي، بدل سفر، ومزايا إضافية حسب البرنامج.",
        "link": "https://www.daad.de",
        "type": "ممولة بالكامل أو جزئياً"
    },
    {
        "name": "MAECI Scholarship",
        "country": "إيطاليا",
        "continent": "أوروبا",
        "degree": "ماجستير، دكتوراه، فنون",
        "gpa": "حسب البرنامج والجامعة",
        "majors": "الهندسة، العمارة، التصميم، الفنون، الاقتصاد، العلوم السياسية",
        "funding": "منحة مالية، تأمين صحي، وإعفاءات دراسية وفق شروط البرنامج.",
        "link": "https://studyinitaly.esteri.it",
        "type": "ممولة"
    },
    {
        "name": "Erasmus Mundus",
        "country": "دول أوروبية متعددة",
        "continent": "أوروبا",
        "degree": "ماجستير",
        "gpa": "سجل أكاديمي قوي، وغالباً بكالوريوس مناسب للتخصص",
        "majors": "الهندسة، الذكاء الاصطناعي، البيئة، الإدارة، العلوم، الصحة، التكنولوجيا",
        "funding": "منح كاملة تشمل الرسوم الدراسية ومساهمة شهرية وتكاليف السفر والاستقرار وفق البرنامج.",
        "link": "https://erasmus-plus.ec.europa.eu",
        "type": "ممولة بالكامل"
    },
    {
        "name": "Chevening Scholarship",
        "country": "المملكة المتحدة",
        "continent": "أوروبا",
        "degree": "ماجستير",
        "gpa": "شهادة جامعية تؤهل للماجستير وخبرة عمل مستوفية للشروط",
        "majors": "الإدارة، القانون، السياسة، الاقتصاد، الهندسة، التكنولوجيا، الصحة",
        "funding": "الرسوم الدراسية، راتب المعيشة، تذاكر السفر ومصاريف إضافية.",
        "link": "https://www.chevening.org",
        "type": "ممولة بالكامل"
    },
    {
        "name": "Swiss Government Excellence",
        "country": "سويسرا",
        "continent": "أوروبا",
        "degree": "دكتوراه، أبحاث، ما بعد الدكتوراه",
        "gpa": "مؤهل جامعي قوي ومقترح بحثي مناسب",
        "majors": "العلوم، الهندسة، الطب، التكنولوجيا، الفنون والبحث العلمي",
        "funding": "راتب شهري وتأمين ومزايا سفر حسب البرنامج.",
        "link": "https://www.sbfi.admin.ch",
        "type": "ممولة"
    },
    {
        "name": "Swedish Institute Scholarship",
        "country": "السويد",
        "continent": "أوروبا",
        "degree": "ماجستير",
        "gpa": "سجل أكاديمي قوي وخبرة مهنية وفق شروط المنحة",
        "majors": "التنمية المستدامة، التكنولوجيا، الإدارة، الابتكار، العلوم",
        "funding": "الرسوم الدراسية، راتب شهري، تأمين وبدل سفر وفق الدورة.",
        "link": "https://si.se",
        "type": "ممولة بالكامل"
    },

    # NORTH AND SOUTH AMERICA
    {
        "name": "Fulbright Scholarship",
        "country": "الولايات المتحدة الأمريكية",
        "continent": "أمريكا الشمالية",
        "degree": "ماجستير، أبحاث",
        "gpa": "سجل أكاديمي قوي؛ يختلف حسب البرنامج والدولة",
        "majors": "الهندسة، الطب والصحة العامة، العلوم، الاقتصاد، القانون، الفنون",
        "funding": "الرسوم الدراسية، المعيشة، التأمين الصحي وتذاكر السفر وفق البرنامج.",
        "link": "https://foreign.fulbrightonline.org",
        "type": "ممولة بالكامل"
    },
    {
        "name": "Knight-Hennessy Scholars",
        "country": "الولايات المتحدة الأمريكية",
        "continent": "أمريكا الشمالية",
        "degree": "ماجستير، دكتوراه، برامج مهنية",
        "gpa": "تميز أكاديمي وقيادي؛ لا يوجد حد موحد للمعدل",
        "majors": "الهندسة، الطب، القانون، العلوم، الأعمال، التعليم",
        "funding": "تمويل دراسي ومعيشة ومخصصات إضافية وفق شروط البرنامج.",
        "link": "https://knight-hennessy.stanford.edu",
        "type": "ممولة بالكامل"
    },
    {
        "name": "Vanier / Canadian Doctoral Awards",
        "country": "كندا",
        "continent": "أمريكا الشمالية",
        "degree": "دكتوراه",
        "gpa": "تفوق أكاديمي وبحثي وفق معايير البرنامج",
        "majors": "العلوم الصحية، الهندسة، العلوم الطبيعية، العلوم الاجتماعية",
        "funding": "تمويل بحثي ومخصصات مالية وفق برنامج الجائزة والجامعة.",
        "link": "https://www.educanada.ca",
        "type": "تمويل بحثي"
    },
    {
        "name": "Lester B. Pearson Scholarship",
        "country": "كندا",
        "continent": "أمريكا الشمالية",
        "degree": "بكالوريوس",
        "gpa": "تفوق أكاديمي استثنائي وترشيح من المدرسة",
        "majors": "تخصصات متعددة في جامعة تورنتو",
        "funding": "الرسوم الدراسية، الكتب، الرسوم الإضافية والسكن لمدة أربع سنوات وفق الشروط.",
        "link": "https://future.utoronto.ca/pearson",
        "type": "ممولة بالكامل"
    },
    {
        "name": "OAS Academic Scholarships",
        "country": "دول الأمريكتين",
        "continent": "أمريكا الشمالية والجنوبية",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "حسب البرنامج والجامعة",
        "majors": "الهندسة، العلوم، الإدارة، التكنولوجيا، التنمية",
        "funding": "مساهمات مالية دراسية تختلف حسب المنحة.",
        "link": "https://www.oas.org",
        "type": "تمويل جزئي أو كامل"
    },

    # ASIA
    {
        "name": "Chinese Government Scholarship CSC",
        "country": "الصين",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "غالباً 70% فما فوق حسب الجامعة والتخصص",
        "majors": "الطب، الهندسة، الذكاء الاصطناعي، البرمجة، الاقتصاد، اللغات",
        "funding": "رسوم الدراسة، السكن، التأمين الصحي، راتب شهري حسب البرنامج.",
        "link": "https://www.campuschina.org",
        "type": "ممولة بالكامل"
    },
    {
        "name": "Global Korea Scholarship GKS",
        "country": "كوريا الجنوبية",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "80% أو ضمن أعلى 20% من الدفعة وفق شروط البرنامج",
        "majors": "الهندسة، التكنولوجيا، الطب، الإدارة، العلوم، الفنون",
        "funding": "الرسوم الدراسية، تذاكر الطيران، راتب شهري، تأمين وسنة لغة كورية.",
        "link": "https://www.studyinkorea.go.kr",
        "type": "ممولة بالكامل"
    },
    {
        "name": "MEXT Scholarship",
        "country": "اليابان",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه، أبحاث",
        "gpa": "حسب المسار والتقييم الأكاديمي",
        "majors": "الروبوتات، الهندسة، الطب، العلوم، الاقتصاد، الزراعة، الفنون",
        "funding": "إعفاء من الرسوم، راتب شهري، تذاكر سفر وفق الشروط.",
        "link": "https://www.studyinjapan.go.jp",
        "type": "ممولة بالكامل"
    },
    {
        "name": "India ICCR Scholarship",
        "country": "الهند",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "حسب الجامعة والتخصص",
        "majors": "الهندسة، العلوم، الإدارة، الفنون، الاقتصاد، اللغات",
        "funding": "رسوم دراسية ومخصصات مالية وسكن وفق البرنامج.",
        "link": "https://a2ascholarships.iccr.gov.in",
        "type": "ممولة"
    },
    {
        "name": "Malaysia MTCP Scholarship",
        "country": "ماليزيا",
        "continent": "آسيا",
        "degree": "ماجستير",
        "gpa": "غالباً CGPA 3.0 من 4 أو ما يعادله",
        "majors": "الهندسة، العلوم، التكنولوجيا، الإدارة، العلاقات الدولية",
        "funding": "الرسوم الدراسية، راتب شهري وتغطية طبية وفق شروط البرنامج.",
        "link": "https://mtcp.kln.gov.my",
        "type": "ممولة بالكامل"
    },
    {
        "name": "Saudi Study in Saudi",
        "country": "السعودية",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "حسب الجامعة والبرنامج",
        "majors": "الطب، الهندسة، الحاسب، العلوم، الشريعة، الإدارة",
        "funding": "منح كاملة وجزئية حسب الجامعة والبرنامج، وقد تشمل السكن والتأمين ومخصصات.",
        "link": "https://studyinsaudi.moe.gov.sa",
        "type": "كاملة أو جزئية"
    },
    {
        "name": "Qatar University Scholarships",
        "country": "قطر",
        "continent": "آسيا",
        "degree": "بكالوريوس، دراسات عليا",
        "gpa": "يختلف حسب المنحة والتخصص",
        "majors": "الطب، الهندسة، القانون، الإدارة، العلوم، الآداب",
        "funding": "إعفاءات من الرسوم ومزايا أخرى حسب نوع المنحة.",
        "link": "https://www.qu.edu.qa",
        "type": "كاملة أو جزئية"
    },
    {
        "name": "Abu Dhabi University Scholarships",
        "country": "الإمارات",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير",
        "gpa": "حسب فئة المنحة وقد يصل إلى معدلات تفوق مرتفعة",
        "majors": "الهندسة، الأعمال، القانون، الصحة، العلوم",
        "funding": "خصومات وإعفاءات دراسية متفاوتة حسب الاستحقاق.",
        "link": "https://www.adu.ac.ae",
        "type": "جزئية أو كاملة"
    },
    {
        "name": "Russian Government Scholarship",
        "country": "روسيا",
        "continent": "أوروبا وآسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "حسب الجامعة والتخصص والمنافسة",
        "majors": "الطب، الهندسة النووية، الطيران، البرمجة، العلوم",
        "funding": "مقاعد دراسية ممولة وإعفاء من الرسوم وفق الشروط؛ بعض المصاريف قد يتحملها الطالب.",
        "link": "https://education-in-russia.com",
        "type": "ممولة"
    },

    # OCEANIA
    {
        "name": "Australia Awards",
        "country": "أستراليا",
        "continent": "أوقيانوسيا",
        "degree": "ماجستير، برامج محددة",
        "gpa": "حسب الدولة والبرنامج وخبرة المتقدم",
        "majors": "الصحة، الهندسة، الزراعة، الإدارة، التنمية، البيئة",
        "funding": "الرسوم الدراسية، تذاكر السفر، بدل معيشة، تأمين صحي ومزايا أخرى.",
        "link": "https://www.dfat.gov.au",
        "type": "ممولة بالكامل"
    },
    {
        "name": "Manaaki New Zealand Scholarships",
        "country": "نيوزيلندا",
        "continent": "أوقيانوسيا",
        "degree": "بكالوريوس، دبلوم دراسات عليا، ماجستير، دكتوراه حسب الأهلية",
        "gpa": "سجل أكاديمي جيد وخبرة وشروط الدولة",
        "majors": "الزراعة، البيئة، الصحة، الهندسة، التنمية، التكنولوجيا",
        "funding": "الرسوم الدراسية، راتب المعيشة، السفر والتأمين وفق البرنامج.",
        "link": "https://www.nzscholarships.govt.nz",
        "type": "ممولة بالكامل"
    },

    # AFRICA
    {
        "name": "Mastercard Foundation Scholars Program",
        "country": "دول أفريقية متعددة",
        "continent": "أفريقيا",
        "degree": "بكالوريوس، ماجستير",
        "gpa": "تميز أكاديمي وحاجة مالية وإمكانات قيادية",
        "majors": "الهندسة، الصحة، الزراعة، التكنولوجيا، الأعمال، العلوم",
        "funding": "قد يشمل الرسوم والسكن والمعيشة والإرشاد والتطوير المهني.",
        "link": "https://mastercardfdn.org",
        "type": "ممولة بالكامل"
    },
    {
        "name": "Egyptian Government Scholarships",
        "country": "مصر",
        "continent": "أفريقيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "حسب الجامعة والبرنامج والاتفاقيات",
        "majors": "الطب، الهندسة، العلوم، الزراعة، الآداب، التكنولوجيا",
        "funding": "إعفاءات ورسوم ومزايا متفاوتة حسب برنامج المنحة.",
        "link": "https://study-in-egypt.gov.eg",
        "type": "حسب البرنامج"
    }
]


# ==========================================
# واجهة الموقع
# ==========================================

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>منح العالم | الدليل العالمي للمنح الدراسية</title>

<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    --primary: #4f46e5;
    --secondary: #7c3aed;
    --dark: #111827;
    --muted: #64748b;
    --bg: #f5f7fc;
    --white: #ffffff;
}

body {
    font-family: Tahoma, Arial, sans-serif;
    background: var(--bg);
    color: var(--dark);
    line-height: 1.8;
}

/* NAVBAR */

.navbar {
    background: #111827;
    color: white;
    padding: 18px 7%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
}

.logo {
    font-size: 25px;
    font-weight: bold;
}

.logo span {
    color: #a78bfa;
}

.navbar a {
    color: white;
    text-decoration: none;
    margin-right: 15px;
    font-size: 14px;
}

/* HERO */

.hero {
    background: linear-gradient(120deg, #312e81, #4f46e5, #7c3aed);
    color: white;
    padding: 75px 7% 85px;
    text-align: center;
}

.hero h1 {
    font-size: clamp(28px, 5vw, 44px);
    margin-bottom: 15px;
}

.hero p {
    color: #e0e7ff;
    font-size: 17px;
    max-width: 750px;
    margin: auto;
}

.hero-search {
    max-width: 750px;
    margin: 30px auto 0;
    display: flex;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    padding: 6px;
}

.hero-search input {
    flex: 1;
    border: none;
    outline: none;
    padding: 15px;
    font-size: 15px;
    min-width: 0;
}

.hero-search button {
    border: none;
    background: #4f46e5;
    color: white;
    padding: 12px 28px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
}

/* STATS */

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    max-width: 1050px;
    margin: -35px auto 35px;
    padding: 0 20px;
}

.stat {
    background: white;
    padding: 22px;
    text-align: center;
    border-radius: 15px;
    box-shadow: 0 8px 25px #0000000b;
}

.stat h2 {
    color: var(--primary);
    font-size: 30px;
}

.stat p {
    color: var(--muted);
    font-size: 14px;
}

/* MAIN */

.container {
    max-width: 1250px;
    padding: 20px;
    margin: auto;
}

.section-title {
    margin-bottom: 25px;
}

.section-title h2 {
    font-size: 27px;
}

.section-title p {
    color: var(--muted);
}

/* FILTERS */

.filters {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    background: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 0 5px 20px #00000008;
}

.filters select {
    padding: 13px;
    border: 1px solid #e2e8f0;
    border-radius: 9px;
    background: white;
    font-size: 14px;
    outline: none;
}

.filter-btn {
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 9px;
    cursor: pointer;
    font-weight: bold;
    padding: 12px;
}

.reset {
    background: #e2e8f0;
    color: #334155;
    padding: 12px;
    border-radius: 9px;
    text-align: center;
    text-decoration: none;
}

/* CARDS */

.scholarship-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 22px;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 22px;
    border: 1px solid #edf0f7;
    box-shadow: 0 5px 20px #00000008;
    transition: .3s;
    display: flex;
    flex-direction: column;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px #4f46e51a;
}

.card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 12px;
}

.country {
    color: var(--primary);
    font-size: 14px;
    font-weight: bold;
}

.tag {
    background: #ede9fe;
    color: #6d28d9;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    white-space: nowrap;
}

.card h3 {
    font-size: 19px;
    margin-bottom: 10px;
}

.info {
    margin-top: 10px;
    font-size: 13px;
}

.info strong {
    display: block;
    color: #334155;
    margin-bottom: 3px;
}

.info p {
    color: var(--muted);
}

.card-bottom {
    margin-top: auto;
    padding-top: 20px;
}

.apply {
    display: block;
    text-align: center;
    background: linear-gradient(100deg, #4f46e5, #7c3aed);
    color: white;
    text-decoration: none;
    padding: 12px;
    border-radius: 9px;
    font-weight: bold;
    transition: .2s;
}

.apply:hover {
    opacity: .85;
}

/* EMPTY */

.empty {
    background: white;
    padding: 50px;
    text-align: center;
    border-radius: 15px;
    color: var(--muted);
}

/* NOTICE */

.notice {
    background: #fffbeb;
    border: 1px solid #fde68a;
    color: #92400e;
    padding: 17px;
    border-radius: 12px;
    margin: 30px 0;
    font-size: 13px;
}

/* FOOTER */

footer {
    background: #111827;
    color: #cbd5e1;
    text-align: center;
    padding: 30px 15px;
    margin-top: 50px;
    font-size: 13px;
}

@media(max-width: 950px) {
    .scholarship-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .filters {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media(max-width: 600px) {
    .scholarship-grid {
        grid-template-columns: 1fr;
    }

    .stats {
        grid-template-columns: 1fr;
        margin-top: 20px;
    }

    .filters {
        grid-template-columns: 1fr;
    }

    .hero {
        padding: 50px 20px;
    }

    .hero-search button {
        padding: 10px 15px;
    }

    .navbar {
        justify-content: center;
    }
}
</style>
</head>

<body>

<nav class="navbar">
    <div class="logo">🎓 منح <span>العالم</span></div>
    <div>
        <a href="/">الرئيسية</a>
        <a href="#scholarships">المنح الدراسية</a>
        <a href="#about">عن المنصة</a>
    </div>
</nav>

<section class="hero">
    <h1>اكتشف مستقبلك مع المنح الدراسية العالمية</h1>

    <p>
        دليلك الشامل للوصول إلى المنح الدراسية في مختلف دول العالم.
        اختر الدولة والتخصص والمرحلة الدراسية وابحث عن فرصتك القادمة.
    </p>

    <form class="hero-search" method="GET" action="/">
        <input
            type="text"
            name="q"
            placeholder="ابحث باسم المنحة أو الدولة أو التخصص..."
            value="{{ q }}"
        >
        <button type="submit">بحث 🔍</button>
    </form>
</section>

<section class="stats">
    <div class="stat">
        <h2>{{ total }}</h2>
        <p>برنامج منحة في قاعدة البيانات</p>
    </div>

    <div class="stat">
        <h2>{{ countries }}</h2>
        <p>دولة وجهة دراسية</p>
    </div>

    <div class="stat">
        <h2>{{ continents }}</h2>
        <p>قارات ومناطق جغرافية</p>
    </div>
</section>

<main class="container" id="scholarships">

    <div class="section-title">
        <h2>🌍 اكتشف المنح الدراسية</h2>
        <p>اختر المنحة التي تناسب مؤهلاتك وطموحاتك الأكاديمية.</p>
    </div>

    <form method="GET" action="/" class="filters">

        <input type="hidden" name="q" value="{{ q }}">

        <select name="continent">
            <option value="">جميع القارات</option>
            {% for c in all_continents %}
            <option value="{{ c }}"
                {% if selected_continent == c %}selected{% endif %}>
                {{ c }}
            </option>
            {% endfor %}
        </select>

        <select name="country">
            <option value="">جميع الدول</option>
            {% for c in all_countries %}
            <option value="{{ c }}"
                {% if selected_country == c %}selected{% endif %}>
                {{ c }}
            </option>
            {% endfor %}
        </select>

        <select name="degree">
            <option value="">جميع المراحل الدراسية</option>
            {% for d in all_degrees %}
            <option value="{{ d }}"
                {% if selected_degree == d %}selected{% endif %}>
                {{ d }}
            </option>
            {% endfor %}
        </select>

        <button class="filter-btn" type="submit">
            تطبيق الفلاتر
        </button>

        <a class="reset" href="/">إعادة تعيين</a>

    </form>

    <p style="margin-bottom:20px;color:#64748b">
        عدد النتائج: <strong>{{ scholarships|length }}</strong>
    </p>

    {% if scholarships %}

    <div class="scholarship-grid">

        {% for s in scholarships %}

        <article class="card">

            <div class="card-top">
                <span class="country">📍 {{ s.country }}</span>
                <span class="tag">{{ s.type }}</span>
            </div>

            <h3>{{ s.name }}</h3>

            <div class="info">
                <strong>🌎 القارة</strong>
                <p>{{ s.continent }}</p>
            </div>

            <div class="info">
                <strong>🎓 المراحل الدراسية</strong>
                <p>{{ s.degree }}</p>
            </div>

            <div class="info">
                <strong>📊 المعدل المطلوب</strong>
                <p>{{ s.gpa }}</p>
            </div>

            <div class="info">
                <strong>📚 التخصصات المتاحة</strong>
                <p>{{ s.majors }}</p>
            </div>

            <div class="info">
                <strong>💰 المميزات والتمويل</strong>
                <p>{{ s.funding }}</p>
            </div>

            <div class="card-bottom">
                <a class="apply"
                   href="{{ s.link }}"
                   target="_blank"
                   rel="noopener noreferrer">
                    الموقع الرسمي والتقديم ←
                </a>
            </div>

        </article>

        {% endfor %}

    </div>

    {% else %}

    <div class="empty">
        <h2>🔍 لم نجد نتائج مطابقة</h2>
        <p>جرّب تغيير كلمات البحث أو اختيار دولة أخرى.</p>
    </div>

    {% endif %}

    <div class="notice">
        <strong>⚠️ تنبيه مهم:</strong>
        المعدلات المذكورة إرشادية وليست شروط قبول رسمية موحدة.
        تختلف شروط القبول والتمويل والتخصصات والمواعيد من جامعة إلى
        أخرى ومن دورة تقديم إلى أخرى. يرجى مراجعة الموقع الرسمي لكل منحة
        والتأكد من أهلية بلدك قبل التقديم.
    </div>

</main>

<section class="container" id="about">
    <div class="section-title">
        <h2>عن منصة منح العالم</h2>
        <p>
            منصة إرشادية تساعد الطلاب والباحثين عن فرص التعليم العالي
            في الوصول إلى برامج المنح الدولية ومقارنة شروطها ومميزاتها.
        </p>
    </div>
</section>

<footer>
    <h3>🎓 منح العالم</h3>
    <p>دليلك نحو مستقبل أكاديمي أفضل</p>
    <p>© 2026 جميع الحقوق محفوظة</p>
    <p>منصة معلوماتية مستقلة وليست جهة مانحة للمنح الدراسية.</p>
</footer>

</body>
</html>
"""


# ==========================================
# محرك البحث والفلاتر
# ==========================================

@app.route("/")
def home():

    q = request.args.get("q", "").strip().casefold()
    selected_country = request.args.get("country", "").strip()
    selected_continent = request.args.get("continent", "").strip()
    selected_degree = request.args.get("degree", "").strip()

    scholarships = scholarships_db.copy()

    if q:
        scholarships = [
            s for s in scholarships
            if q in " ".join([
                s["name"],
                s["country"],
                s["continent"],
                s["degree"],
                s["gpa"],
                s["majors"],
                s["funding"],
                s["type"]
            ]).casefold()
        ]

    if selected_country:
        scholarships = [
            s for s in scholarships
            if s["country"] == selected_country
        ]

    if selected_continent:
        scholarships = [
            s for s in scholarships
            if selected_continent in s["continent"]
        ]

    if selected_degree:
        scholarships = [
            s for s in scholarships
            if selected_degree in s["degree"]
        ]

    all_countries = sorted(
        set(s["country"] for s in scholarships_db)
    )

    all_continents = sorted(
        set(
            continent
            for s in scholarships_db
            for continent in s["continent"].split(" و")
        )
    )

    all_degrees = [
        "بكالوريوس",
        "ماجستير",
        "دكتوراه",
        "أبحاث"
    ]

    return render_template_string(
        HTML,
        scholarships=scholarships,
        q=request.args.get("q", ""),
        selected_country=selected_country,
        selected_continent=selected_continent,
        selected_degree=selected_degree,
        all_countries=all_countries,
        all_continents=all_continents,
        all_degrees=all_degrees,
        total=len(scholarships_db),
        countries=len(all_countries),
        continents=len(all_continents)
    )


# ==========================================
# تشغيل التطبيق
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
