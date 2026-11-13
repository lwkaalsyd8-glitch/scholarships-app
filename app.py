
from flask import Flask, render_template_string, request
import os
import json
import sqlite3
import requests

from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# ==================================================
# الإعدادات
# ==================================================

DB_FILE = "scholarships.db"

UPDATE_FEED_URL = os.environ.get(
    "SCHOLARSHIPS_FEED_URL", ""
)

TIMEZONE = "Africa/Khartoum"


# ==================================================
# دليل التخصصات الأكاديمية
# ==================================================

MAJOR_CATEGORIES = {
    "الطب والصحة": [
        "الطب البشري", "طب الأسنان", "الصيدلة",
        "التمريض", "العلاج الطبيعي", "المختبرات الطبية",
        "الأشعة", "التخدير", "الصحة العامة",
        "التغذية العلاجية", "الطب البيطري",
        "العلوم الطبية الحيوية", "القبالة",
        "إدارة المستشفيات", "علم النفس السريري"
    ],

    "الهندسة": [
        "الهندسة المدنية", "الهندسة المعمارية",
        "الهندسة الكهربائية", "الهندسة الميكانيكية",
        "الهندسة الكيميائية", "هندسة الطيران",
        "هندسة الفضاء", "هندسة البترول",
        "هندسة التعدين", "هندسة الطاقة",
        "هندسة الاتصالات", "هندسة الإلكترونيات",
        "الهندسة الصناعية", "الهندسة النووية",
        "هندسة الميكاترونكس", "هندسة البيئة",
        "هندسة المواد", "الهندسة الطبية الحيوية"
    ],

    "علوم الحاسوب والتكنولوجيا": [
        "علوم الحاسوب", "هندسة البرمجيات",
        "الذكاء الاصطناعي", "علم البيانات",
        "الأمن السيبراني", "الشبكات",
        "تقنية المعلومات", "نظم المعلومات",
        "تطوير التطبيقات", "تطوير الألعاب",
        "الحوسبة السحابية", "الروبوتات",
        "إنترنت الأشياء", "تعلم الآلة",
        "تحليل البيانات", "قواعد البيانات"
    ],

    "العلوم الطبيعية": [
        "الرياضيات", "الفيزياء", "الكيمياء",
        "الأحياء", "علم الفلك", "الجيولوجيا",
        "علوم البحار", "العلوم البيئية",
        "الإحصاء", "الفيزياء النووية",
        "الكيمياء الحيوية", "علم الوراثة",
        "علوم المناخ", "علوم الأرض"
    ],

    "الآداب والعلوم الإنسانية": [
        "اللغة العربية", "اللغة الإنجليزية",
        "اللغة الفرنسية", "اللغة الألمانية",
        "اللغة الإسبانية", "اللغة الصينية",
        "الترجمة", "الأدب العربي", "الأدب الإنجليزي",
        "التاريخ", "الجغرافيا", "الفلسفة",
        "علم الاجتماع", "علم النفس",
        "الأنثروبولوجيا", "الدراسات الثقافية",
        "الآثار", "دراسات المتاحف",
        "العلوم الإنسانية"
    ],

    "القانون والسياسة": [
        "القانون العام", "القانون الخاص",
        "القانون الدولي", "القانون التجاري",
        "القانون الجنائي", "حقوق الإنسان",
        "العلاقات الدولية", "العلوم السياسية",
        "الدراسات الدبلوماسية", "السياسات العامة",
        "الدراسات الأمنية", "الحوكمة"
    ],

    "الإدارة والاقتصاد": [
        "إدارة الأعمال", "المحاسبة", "الاقتصاد",
        "الاقتصاد الدولي", "التمويل والمصارف",
        "التسويق", "إدارة الموارد البشرية",
        "إدارة المشاريع", "التجارة الدولية",
        "ريادة الأعمال", "إدارة سلاسل الإمداد",
        "الإدارة العامة", "إدارة المخاطر",
        "التأمين", "التجارة الإلكترونية"
    ],

    "التربية والتعليم": [
        "التربية العامة", "تعليم اللغة العربية",
        "تعليم اللغة الإنجليزية", "التربية الخاصة",
        "رياض الأطفال", "المناهج وطرق التدريس",
        "الإرشاد النفسي والتربوي",
        "تكنولوجيا التعليم", "الإدارة التربوية"
    ],

    "الإعلام والاتصال": [
        "الإعلام", "الصحافة", "العلاقات العامة",
        "الإذاعة والتلفزيون", "الإنتاج السينمائي",
        "الإعلام الرقمي", "الاتصال الجماهيري",
        "الإعلان", "التسويق الإعلامي",
        "صناعة المحتوى"
    ],

    "الفنون والتصميم": [
        "الفنون الجميلة", "التصميم الجرافيكي",
        "التصميم الداخلي", "التصميم الصناعي",
        "تصميم الأزياء", "التصوير الفوتوغرافي",
        "الموسيقى", "المسرح", "السينما",
        "الرسوم المتحركة", "الفنون الرقمية",
        "النحت", "الرسم"
    ],

    "الزراعة والبيئة": [
        "الزراعة", "الهندسة الزراعية",
        "علوم الأغذية", "الإنتاج الحيواني",
        "الإنتاج النباتي", "الغابات",
        "الثروة السمكية", "الأمن الغذائي",
        "إدارة المياه", "التنمية الريفية",
        "حماية البيئة", "الاستدامة"
    ],

    "السياحة والرياضة": [
        "إدارة السياحة", "إدارة الفنادق",
        "الضيافة", "الإرشاد السياحي",
        "إدارة الفعاليات", "إدارة المطاعم",
        "السفر والطيران", "التربية البدنية",
        "علوم الرياضة", "الإدارة الرياضية",
        "التدريب الرياضي", "العلاج الرياضي"
    ],

    "الدراسات الدينية": [
        "الدراسات الإسلامية", "الشريعة",
        "الفقه", "أصول الدين",
        "القرآن الكريم وعلومه", "الحديث الشريف",
        "الدعوة", "الدراسات المقارنة للأديان"
    ]
}

ALL_MAJORS = [
    major
    for category in MAJOR_CATEGORIES.values()
    for major in category
]


# ==================================================
# قاعدة بيانات المنح الأولية
# ==================================================

INITIAL_SCHOLARSHIPS = [

    {
        "name": "Türkiye Bursları",
        "country": "تركيا",
        "continent": "أوروبا وآسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "70% للبكالوريوس، 75% للدراسات العليا، 90% للطب وفق شروط البرنامج",
        "majors": "الطب، الهندسة، العلوم، الآداب، الاقتصاد، القانون، الحاسب والفنون",
        "funding": "رسوم دراسية وسكن وراتب شهري وتذاكر وتأمين وسنة لغة تركية وفق الشروط.",
        "link": "https://www.turkiyeburslari.gov.tr",
        "type": "ممولة بالكامل",
        "description": "برنامج الحكومة التركية للطلاب الدوليين، ويتيح الدراسة في جامعات تركية ضمن تخصصات ومراحل مختلفة.",
        "eligible_nationalities": "حسب شروط الجنسية المنشورة لكل دورة.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "يعلن سنوياً",
        "application_status": "غير متحقق حالياً",
        "required_documents": "جواز السفر، الشهادة، كشف الدرجات، صورة شخصية، مستندات إضافية حسب المرحلة.",
        "language_requirements": "حسب لغة البرنامج والجامعة.",
        "official_source": "https://www.turkiyeburslari.gov.tr"
    },

    {
        "name": "Stipendium Hungaricum",
        "country": "المجر",
        "continent": "أوروبا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "حسب متطلبات الجامعة والبرنامج",
        "majors": "الطب، الهندسة، العلوم، الزراعة، الاقتصاد، العلوم الإنسانية والفنون",
        "funding": "إعفاء من الرسوم ومساهمة سكن وراتب شهري وتأمين صحي.",
        "link": "https://stipendiumhungaricum.hu",
        "type": "ممولة",
        "description": "منحة الحكومة المجرية بالتعاون مع جهات شريكة في الدول المؤهلة.",
        "eligible_nationalities": "الدول الشريكة وفق الإعلان السنوي.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "يعلن سنوياً",
        "application_status": "غير متحقق حالياً",
        "required_documents": "شهادة دراسية وكشف درجات وجواز سفر ورسالة دافع ومستندات البرنامج.",
        "language_requirements": "الإنجليزية أو المجرية حسب البرنامج.",
        "official_source": "https://stipendiumhungaricum.hu"
    },

    {
        "name": "DAAD Scholarship",
        "country": "ألمانيا",
        "continent": "أوروبا",
        "degree": "ماجستير، دكتوراه، أبحاث",
        "gpa": "سجل أكاديمي قوي حسب البرنامج",
        "majors": "الهندسة، العلوم، الاقتصاد، البيئة، الفنون، العلوم الاجتماعية والإنسانية",
        "funding": "راتب شهري وتأمين وبدل سفر ومزايا تختلف حسب المنحة.",
        "link": "https://www.daad.de",
        "type": "ممولة أو جزئية",
        "description": "مجموعة برامج تمويل ألمانية للطلاب والباحثين الدوليين.",
        "eligible_nationalities": "حسب برنامج التمويل.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "يختلف حسب البرنامج",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادة وكشف الدرجات والسيرة الذاتية وخطاب الدافع والتوصيات عند طلبها.",
        "language_requirements": "ألمانية أو إنجليزية وفق البرنامج.",
        "official_source": "https://www.daad.de"
    },

    {
        "name": "Erasmus Mundus",
        "country": "دول أوروبية متعددة",
        "continent": "أوروبا",
        "degree": "ماجستير",
        "gpa": "بكالوريوس مناسب وسجل أكاديمي تنافسي",
        "majors": "الهندسة، العلوم، الاقتصاد، البيئة، الإعلام، الثقافة، التكنولوجيا والعلوم الاجتماعية",
        "funding": "منح تنافسية قد تشمل الرسوم ومساهمة المعيشة والسفر والاستقرار.",
        "link": "https://erasmus-plus.ec.europa.eu",
        "type": "ممولة بالكامل للمنح المختارة",
        "description": "برامج ماجستير مشتركة تنفذها جامعات من عدة دول، وقد ينتقل الطالب بين جامعات مختلفة.",
        "eligible_nationalities": "طلاب من دول متعددة وفق شروط البرنامج.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "يختلف حسب برنامج الماجستير",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادة وكشف الدرجات والسيرة الذاتية ورسائل التوصية وخطاب الدافع.",
        "language_requirements": "غالباً إثبات إجادة الإنجليزية أو لغة الدراسة.",
        "official_source": "https://erasmus-plus.ec.europa.eu"
    },

    {
        "name": "Chevening",
        "country": "المملكة المتحدة",
        "continent": "أوروبا",
        "degree": "ماجستير",
        "gpa": "شهادة جامعية مؤهلة للقبول في برنامج الماجستير",
        "majors": "القانون، السياسة، الإدارة، الاقتصاد، العلوم، الإعلام، التكنولوجيا والإنسانيات",
        "funding": "الرسوم والمعيشة والسفر وفق شروط البرنامج.",
        "link": "https://www.chevening.org",
        "type": "ممولة بالكامل",
        "description": "برنامج منح بريطاني للقيادات المستقبلية، ويشترط استيفاء متطلبات الخبرة والعمل وغيرها.",
        "eligible_nationalities": "حسب قائمة الدول المؤهلة.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "يعلن سنوياً",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادة، خبرة العمل المطلوبة، إجابات الطلب، التوصيات والمستندات الأخرى.",
        "language_requirements": "متطلبات اللغة والجامعة وفق شروط القبول.",
        "official_source": "https://www.chevening.org"
    },

    {
        "name": "Fulbright",
        "country": "الولايات المتحدة الأمريكية",
        "continent": "أمريكا الشمالية",
        "degree": "ماجستير، أبحاث",
        "gpa": "حسب البرنامج والبلد",
        "majors": "العلوم، الهندسة، الفنون، القانون، الاقتصاد، التعليم، العلوم الإنسانية والاجتماعية",
        "funding": "رسوم ومعيشة وتأمين وسفر وفق برنامج الدولة.",
        "link": "https://foreign.fulbrightonline.org",
        "type": "ممولة",
        "description": "برنامج تبادل أكاديمي أمريكي تختلف شروطه ومواعيده حسب بلد المتقدم.",
        "eligible_nationalities": "وفق البرنامج القطري.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "حسب بلد المتقدم",
        "application_status": "غير متحقق حالياً",
        "required_documents": "شهادة وكشف درجات وسيرة ذاتية وخطاب دافع ومراجع أكاديمية.",
        "language_requirements": "الإنجليزية واختبارات حسب البرنامج.",
        "official_source": "https://foreign.fulbrightonline.org"
    },

    {
        "name": "Chinese Government Scholarship CSC",
        "country": "الصين",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "حسب الجامعة والتخصص",
        "majors": "الطب، الهندسة، الاقتصاد، اللغات، العلوم، الإدارة، العلوم الإنسانية",
        "funding": "قد تشمل الرسوم والسكن والتأمين والراتب الشهري.",
        "link": "https://www.campuschina.org",
        "type": "ممولة",
        "description": "منح الحكومة الصينية للطلاب الدوليين عبر مسارات تقديم مختلفة.",
        "eligible_nationalities": "حسب شروط البرنامج.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "يختلف حسب المسار والجامعة",
        "application_status": "غير متحقق حالياً",
        "required_documents": "جواز السفر والشهادة وكشف الدرجات وخطة الدراسة والتوصيات حسب المرحلة.",
        "language_requirements": "الصينية أو الإنجليزية حسب البرنامج.",
        "official_source": "https://www.campuschina.org"
    },

    {
        "name": "Global Korea Scholarship",
        "country": "كوريا الجنوبية",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "وفق الحد الأدنى الرسمي أو الترتيب الأكاديمي المحدد للدورة",
        "majors": "الهندسة، الحاسب، العلوم، الفنون، الإدارة، العلوم الإنسانية والاجتماعية",
        "funding": "رسوم وتذاكر وراتب وتأمين وبرنامج لغة كورية وفق الشروط.",
        "link": "https://www.studyinkorea.go.kr",
        "type": "ممولة بالكامل",
        "description": "برنامج الحكومة الكورية لدعم الطلاب الدوليين.",
        "eligible_nationalities": "حسب قائمة الدول المؤهلة للدورة.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "حسب مسار التقديم",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادة وكشف الدرجات وجواز السفر وخطابات التوصية والنماذج الرسمية.",
        "language_requirements": "حسب البرنامج؛ وقد تتضمن سنة لغة كورية.",
        "official_source": "https://www.studyinkorea.go.kr"
    },

    {
        "name": "MEXT Scholarship",
        "country": "اليابان",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه، أبحاث",
        "gpa": "حسب مسار المنحة والتقييم الأكاديمي",
        "majors": "الهندسة، الطب، العلوم، الاقتصاد، التربية، الآداب، العلوم الاجتماعية والفنون",
        "funding": "رسوم دراسية وراتب شهري وتذاكر سفر وفق الشروط.",
        "link": "https://www.studyinjapan.go.jp",
        "type": "ممولة بالكامل",
        "description": "منح وزارة التعليم والثقافة والرياضة والعلوم والتكنولوجيا اليابانية.",
        "eligible_nationalities": "حسب شروط سفارة اليابان والبرنامج.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "حسب السفارة أو الجامعة",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادة وكشف الدرجات وخطة البحث والنماذج الرسمية.",
        "language_requirements": "اليابانية أو الإنجليزية حسب المسار.",
        "official_source": "https://www.studyinjapan.go.jp"
    },

    {
        "name": "India ICCR",
        "country": "الهند",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "حسب الجامعة والتخصص",
        "majors": "العلوم والهندسة والاقتصاد والفنون واللغات والإدارة والعلوم الإنسانية",
        "funding": "رسوم ومخصصات وسكن وفق نوع المنحة.",
        "link": "https://a2ascholarships.iccr.gov.in",
        "type": "ممولة حسب البرنامج",
        "description": "منح المجلس الهندي للعلاقات الثقافية للطلاب الدوليين.",
        "eligible_nationalities": "وفق الدول والبرامج المؤهلة.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "حسب الدورة",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادات وجواز السفر والمستندات الأكاديمية.",
        "language_requirements": "حسب لغة البرنامج.",
        "official_source": "https://a2ascholarships.iccr.gov.in"
    },

    {
        "name": "Australia Awards",
        "country": "أستراليا",
        "continent": "أوقيانوسيا",
        "degree": "برامج دراسات عليا حسب الأهلية",
        "gpa": "حسب الدولة والبرنامج والخبرة",
        "majors": "الصحة، التعليم، الإدارة، البيئة، الزراعة، الهندسة والتنمية",
        "funding": "رسوم دراسية ومعيشة وسفر وتأمين وفق شروط البرنامج.",
        "link": "https://www.dfat.gov.au",
        "type": "ممولة بالكامل",
        "description": "برنامج منح أسترالي تنموي يستهدف الدول المشاركة.",
        "eligible_nationalities": "وفق قائمة الدول المشاركة.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "حسب الدولة",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادة والخبرة والمستندات المطلوبة في الإعلان القطري.",
        "language_requirements": "حسب شروط البرنامج والجامعة.",
        "official_source": "https://www.dfat.gov.au"
    },

    {
        "name": "Manaaki New Zealand",
        "country": "نيوزيلندا",
        "continent": "أوقيانوسيا",
        "degree": "دراسات عليا وبرامج أخرى حسب الأهلية",
        "gpa": "سجل أكاديمي مناسب",
        "majors": "الزراعة، البيئة، الصحة، التعليم، الهندسة والتنمية",
        "funding": "رسوم ومعيشة وسفر وتأمين وفق البرنامج.",
        "link": "https://www.nzscholarships.govt.nz",
        "type": "ممولة بالكامل",
        "description": "برنامج منح نيوزيلندي للدول الشريكة.",
        "eligible_nationalities": "وفق قائمة الدول المؤهلة.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "حسب الدورة والدولة",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادات والسيرة الذاتية والمستندات الخاصة بالبرنامج.",
        "language_requirements": "وفق شروط الجامعة.",
        "official_source": "https://www.nzscholarships.govt.nz"
    },

    {
        "name": "Mastercard Foundation Scholars",
        "country": "دول أفريقية متعددة",
        "continent": "أفريقيا",
        "degree": "بكالوريوس، ماجستير",
        "gpa": "تفوق أكاديمي وحاجة مالية وشروط المؤسسة الشريكة",
        "majors": "العلوم، الهندسة، الأعمال، الصحة، الزراعة، العلوم الاجتماعية",
        "funding": "قد يشمل الرسوم والسكن والمعيشة والإرشاد الأكاديمي.",
        "link": "https://mastercardfdn.org",
        "type": "ممولة بالكامل في البرامج المختارة",
        "description": "برنامج منح من خلال جامعات ومؤسسات شريكة.",
        "eligible_nationalities": "وفق الجامعة والبرنامج.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "حسب الجامعة الشريكة",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادات وإثبات الحاجة المالية وخطابات التوصية حسب الجامعة.",
        "language_requirements": "حسب الجامعة.",
        "official_source": "https://mastercardfdn.org"
    },

    {
        "name": "Saudi Study in Saudi",
        "country": "السعودية",
        "continent": "آسيا",
        "degree": "بكالوريوس، ماجستير، دكتوراه",
        "gpa": "حسب الجامعة والبرنامج",
        "majors": "الطب، الهندسة، الشريعة، العلوم، الحاسب، الآداب والإدارة",
        "funding": "منح كاملة وجزئية حسب نوع المنحة.",
        "link": "https://studyinsaudi.moe.gov.sa",
        "type": "كاملة أو جزئية",
        "description": "بوابة الدراسة في السعودية للطلاب الدوليين.",
        "eligible_nationalities": "حسب البرنامج وشروط الإقامة والجنسية.",
        "accepted_majors": ALL_MAJORS,
        "deadline": "حسب الجامعة",
        "application_status": "غير متحقق حالياً",
        "required_documents": "الشهادة وكشف الدرجات وجواز السفر والمستندات الإضافية.",
        "language_requirements": "العربية أو الإنجليزية حسب البرنامج.",
        "official_source": "https://studyinsaudi.moe.gov.sa"
    }
]


# ==================================================
# SQLite: إنشاء قاعدة البيانات
# ==================================================

def connect_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS scholarships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                country TEXT,
                continent TEXT,
                degree TEXT,
                gpa TEXT,
                majors TEXT,
                funding TEXT,
                link TEXT,
                type TEXT,
                description TEXT,
                eligible_nationalities TEXT,
                accepted_majors TEXT,
                deadline TEXT,
                application_status TEXT,
                required_documents TEXT,
                language_requirements TEXT,
                official_source TEXT,
                last_verified TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        for item in INITIAL_SCHOLARSHIPS:

            values = {
                **item,
                "accepted_majors": json.dumps(
                    item.get("accepted_majors", []),
                    ensure_ascii=False
                ),
                "last_verified": None
            }

            fields = list(values.keys())

            placeholders = ", ".join("?" for _ in fields)

            conn.execute(
                f"""
                INSERT OR IGNORE INTO scholarships
                ({", ".join(fields)})
                VALUES ({placeholders})
                """,
                [values[field] for field in fields]
            )


def get_setting(key, default=""):
    with connect_db() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key=?",
            (key,)
        ).fetchone()

    return row["value"] if row else default


def set_setting(key, value):
    with connect_db() as conn:
        conn.execute("""
            INSERT INTO settings(key, value)
            VALUES (?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value=excluded.value
        """, (key, value))


def get_scholarships():
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT * FROM scholarships ORDER BY country, name"
        ).fetchall()

    result = []

    for row in rows:
        item = dict(row)

        try:
            item["accepted_majors"] = json.loads(
                item["accepted_majors"] or "[]"
            )
        except (ValueError, TypeError):
            item["accepted_majors"] = []

        result.append(item)

    return result


# ==================================================
# نظام التحديث اليومي
# ==================================================

def daily_update():

    global UPDATE_FEED_URL

    if not UPDATE_FEED_URL:
        set_setting(
            "update_status",
            "لم يتم تحديد مصدر بيانات خارجي."
        )
        return

    try:
        response = requests.get(
            UPDATE_FEED_URL,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            raise ValueError("المصدر يجب أن يعيد قائمة JSON")

        allowed_fields = {
            "country",
            "continent",
            "degree",
            "gpa",
            "majors",
            "funding",
            "link",
            "type",
            "description",
            "eligible_nationalities",
            "accepted_majors",
            "deadline",
            "application_status",
            "required_documents",
            "language_requirements",
            "official_source"
        }

        count = 0
        now = datetime.now(timezone.utc).isoformat()

        with connect_db() as conn:

            for item in data:

                if not isinstance(item, dict):
                    continue

                name = item.get("name")
                source = item.get("official_source")

                if not name or not source:
                    continue

                if not source.startswith("https://"):
                    continue

                clean = {
                    k: v
                    for k, v in item.items()
                    if k in allowed_fields
                }

                if "accepted_majors" in clean:
                    clean["accepted_majors"] = json.dumps(
                        clean["accepted_majors"],
                        ensure_ascii=False
                    )

                clean["last_verified"] = now

                fields = ["name"] + list(clean.keys())

                values = [name] + list(clean.values())

                update_sql = ", ".join(
                    f"{field}=excluded.{field}"
                    for field in clean
                )

                conn.execute(
                    f"""
                    INSERT INTO scholarships
                    ({", ".join(fields)})
                    VALUES ({", ".join("?" for _ in fields)})
                    ON CONFLICT(name)
                    DO UPDATE SET {update_sql}
                    """,
                    values
                )

                count += 1

        set_setting(
            "last_update",
            now
        )

        set_setting(
            "update_status",
            f"تم تحديث {count} سجل من مصدر البيانات."
        )

    except (
        requests.RequestException,
        ValueError,
        TypeError,
        sqlite3.Error
    ) as error:

        set_setting(
            "update_status",
            "فشل التحديث مع الاحتفاظ بالبيانات السابقة: "
            + str(error)
        )


# ==================================================
# واجهة الموقع والتصميم
# ==================================================

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>منح العالم | المنصة العالمية للمنح الدراسية</title>

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
}

body {
    font-family: Tahoma, Arial, sans-serif;
    background: var(--bg);
    color: var(--dark);
    line-height: 1.8;
}

.navbar {
    background: #111827;
    color: white;
    padding: 18px 7%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
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
    margin: 0 8px;
    font-size: 14px;
}

.hero {
    background: linear-gradient(120deg,#312e81,#4f46e5,#7c3aed);
    color: white;
    padding: 70px 7%;
    text-align: center;
}

.hero h1 {
    font-size: clamp(28px,5vw,44px);
    margin-bottom: 12px;
}

.hero p {
    color: #e0e7ff;
    max-width: 750px;
    margin: auto;
}

.hero-search {
    max-width: 750px;
    margin: 28px auto 0;
    display: flex;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    padding: 6px;
}

.hero-search input {
    flex: 1;
    min-width: 0;
    border: none;
    outline: none;
    padding: 14px;
    font-size: 15px;
}

button {
    cursor: pointer;
}

.hero-search button {
    background: var(--primary);
    color: white;
    border: 0;
    border-radius: 8px;
    padding: 12px 25px;
    font-weight: bold;
}

.container {
    max-width: 1300px;
    margin: auto;
    padding: 25px 20px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 18px;
    max-width: 1050px;
    margin: -28px auto 25px;
    padding: 0 20px;
}

.stat {
    background: white;
    text-align: center;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 8px 25px #0000000b;
}

.stat h2 {
    font-size: 30px;
    color: var(--primary);
}

.stat p {
    color: var(--muted);
    font-size: 13px;
}

.section-title {
    margin-bottom: 22px;
}

.section-title h2 {
    font-size: 26px;
}

.section-title p {
    color: var(--muted);
}

.update-panel {
    background: #eef2ff;
    color: #3730a3;
    padding: 17px;
    border-radius: 12px;
    margin-bottom: 25px;
    font-size: 13px;
    border: 1px solid #c7d2fe;
}

.filters {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 12px;
    background: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 25px;
}

.filters select {
    width: 100%;
    padding: 13px;
    border: 1px solid #e2e8f0;
    border-radius: 9px;
    background: white;
}

.filter-btn {
    background: var(--primary);
    color: white;
    border: 0;
    border-radius: 9px;
    padding: 12px;
    font-weight: bold;
}

.reset {
    background: #e2e8f0;
    color: #334155;
    padding: 12px;
    text-decoration: none;
    text-align: center;
    border-radius: 9px;
}

.scholarship-grid {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 20px;
}

.card {
    background: white;
    border: 1px solid #edf0f7;
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 5px 20px #00000008;
    display: flex;
    flex-direction: column;
    transition: .25s;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 35px #4f46e51a;
}

.card-top {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 12px;
    align-items: center;
}

.country {
    color: var(--primary);
    font-size: 13px;
    font-weight: bold;
}

.tag {
    background: #ede9fe;
    color: #6d28d9;
    padding: 4px 9px;
    border-radius: 20px;
    font-size: 11px;
}

.card h3 {
    font-size: 19px;
    margin-bottom: 10px;
}

.info {
    font-size: 13px;
    margin-top: 12px;
    overflow-wrap: anywhere;
}

.info strong {
    display: block;
    color: #334155;
    margin-bottom: 3px;
}

.info p {
    color: var(--muted);
}

.details {
    margin-top: 13px;
    padding: 10px;
    background: #f8fafc;
    border-radius: 9px;
}

.details summary {
    cursor: pointer;
    color: var(--primary);
    font-weight: bold;
    font-size: 13px;
}

.details ul {
    padding: 12px 20px;
    color: var(--muted);
    font-size: 12px;
}

.card-bottom {
    margin-top: auto;
    padding-top: 20px;
}

.apply {
    display: block;
    background: linear-gradient(100deg,#4f46e5,#7c3aed);
    color: white;
    text-decoration: none;
    text-align: center;
    padding: 12px;
    border-radius: 9px;
    font-weight: bold;
}

.notice {
    background: #fffbeb;
    color: #92400e;
    border: 1px solid #fde68a;
    border-radius: 12px;
    padding: 18px;
    margin-top: 30px;
    font-size: 13px;
}

.empty {
    background: white;
    padding: 45px;
    text-align: center;
    border-radius: 15px;
    color: var(--muted);
}

footer {
    background: #111827;
    color: #cbd5e1;
    text-align: center;
    padding: 32px;
    margin-top: 45px;
    font-size: 13px;
}

@media(max-width:950px) {
    .scholarship-grid {
        grid-template-columns: repeat(2,1fr);
    }

    .filters {
        grid-template-columns: repeat(2,1fr);
    }
}

@media(max-width:600px) {
    .scholarship-grid,
    .stats,
    .filters {
        grid-template-columns: 1fr;
    }

    .stats {
        margin-top: 20px;
    }

    .navbar {
        justify-content: center;
    }

    .hero {
        padding: 45px 18px;
    }

    .hero-search button {
        padding: 10px 14px;
    }
}

</style>

</head>

<body>

<nav class="navbar">
    <div class="logo">🎓 منح <span>العالم</span></div>

    <div>
        <a href="/">الرئيسية</a>
        <a href="#scholarships">المنح</a>
        <a href="#majors">التخصصات</a>
        <a href="#about">عن المنصة</a>
    </div>
</nav>

<section class="hero">

    <h1>اكتشف مستقبلك مع المنح العالمية</h1>

    <p>
        ابحث عن فرصتك الدراسية في مختلف دول العالم،
        سواء كنت من طلاب التخصصات الأدبية أو العلمية.
    </p>

    <form class="hero-search" method="GET">

        <input
            name="q"
            placeholder="اسم المنحة أو الدولة أو التخصص..."
            value="{{ q }}"
        >

        <button>بحث 🔍</button>

    </form>

</section>

<section class="stats">

    <div class="stat">
        <h2>{{ total }}</h2>
        <p>برنامجاً في قاعدة البيانات</p>
    </div>

    <div class="stat">
        <h2>{{ countries }}</h2>
        <p>دولة أو جهة دراسية</p>
    </div>

    <div class="stat">
        <h2>{{ major_count }}</h2>
        <p>تخصصاً أكاديمياً</p>
    </div>

</section>

<main class="container" id="scholarships">

    <div class="update-panel">
        <strong>🔄 تحديث قاعدة البيانات</strong>
        <p>{{ update_message }}</p>
        <p>آخر مزامنة ناجحة: {{ last_update or "لم تتم بعد" }}</p>
        <p>عدم ظهور تاريخ تحقق يعني أن المعلومات لم تتم مراجعتها آلياً بعد.</p>
    </div>

    <div class="section-title">
        <h2>🌍 المنح الدراسية العالمية</h2>
        <p>قارن شروط القبول والتخصصات والتمويل قبل التقديم.</p>
    </div>

    <form method="GET" class="filters">

        <input type="hidden" name="q" value="{{ q }}">

        <select name="continent">
            <option value="">جميع القارات</option>
            {% for c in continents_list %}
            <option value="{{ c }}"
                {% if selected_continent == c %}selected{% endif %}>
                {{ c }}
            </option>
            {% endfor %}
        </select>

        <select name="country">
            <option value="">جميع الدول</option>
            {% for c in countries_list %}
            <option value="{{ c }}"
                {% if selected_country == c %}selected{% endif %}>
                {{ c }}
            </option>
            {% endfor %}
        </select>

        <select name="degree">
            <option value="">جميع المراحل</option>
            {% for d in degrees %}
            <option value="{{ d }}"
                {% if selected_degree == d %}selected{% endif %}>
                {{ d }}
            </option>
            {% endfor %}
        </select>

        <select name="major">
            <option value="">جميع التخصصات</option>

            {% for category, majors in major_categories.items() %}
            <optgroup label="{{ category }}">

                {% for major in majors %}
                <option value="{{ major }}"
                    {% if selected_major == major %}selected{% endif %}>
                    {{ major }}
                </option>
                {% endfor %}

            </optgroup>
            {% endfor %}
        </select>

        <button class="filter-btn">تطبيق الفلاتر</button>

        <a href="/" class="reset">إعادة تعيين</a>

    </form>

    <p style="margin-bottom:20px;color:#64748b">
        النتائج: <strong>{{ scholarships|length }}</strong>
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
                <strong>🎓 المرحلة الدراسية</strong>
                <p>{{ s.degree }}</p>
            </div>

            <div class="info">
                <strong>📊 المعدل المطلوب</strong>
                <p>{{ s.gpa }}</p>
            </div>

            <div class="info">
                <strong>📚 التخصصات</strong>
                <p>{{ s.majors }}</p>
            </div>

            <div class="info">
                <strong>💰 التمويل والمميزات</strong>
                <p>{{ s.funding }}</p>
            </div>

            <div class="info">
                <strong>📅 موعد التقديم</strong>
                <p>{{ s.deadline }}</p>
            </div>

            <div class="info">
                <strong>📌 حالة التقديم</strong>
                <p>{{ s.application_status }}</p>
            </div>

            <details class="details">
                <summary>📖 شرح المنحة وشروطها بالتفصيل</summary>

                <div class="info">
                    <strong>نبذة عن المنحة</strong>
                    <p>{{ s.description }}</p>
                </div>

                <div class="info">
                    <strong>الجنسيات المؤهلة</strong>
                    <p>{{ s.eligible_nationalities }}</p>
                </div>

                <div class="info">
                    <strong>متطلبات اللغة</strong>
                    <p>{{ s.language_requirements }}</p>
                </div>

                <div class="info">
                    <strong>المستندات المطلوبة</strong>
                    <p>{{ s.required_documents }}</p>
                </div>

                <div class="info">
                    <strong>آخر تحقق فعلي</strong>
                    <p>{{ s.last_verified or "لم يتم التحقق بعد" }}</p>
                </div>
            </details>

            <div class="card-bottom">
                <a class="apply"
                   href="{{ s.link }}"
                   target="_blank"
                   rel="noopener noreferrer">
                    الموقع الرسمي للمنحة ←
                </a>
            </div>

        </article>

        {% endfor %}

    </div>

    {% else %}

    <div class="empty">
        <h2>🔍 لا توجد نتائج مطابقة</h2>
        <p>جرّب تغيير التخصص أو الدولة أو المرحلة الدراسية.</p>
    </div>

    {% endif %}

    <div class="notice">
        <strong>تنبيه مهم:</strong>
        هذه قاعدة بيانات إرشادية أولية. ليست كل التخصصات في دليل
        التخصصات مقبولة في جميع المنح. يجب التأكد من القائمة الرسمية
        لكل جامعة وبرنامج، وكذلك المعدل والجنسية والمواعيد والتمويل.
        لا تعتبر حالة المنحة مفتوحة إلا بعد مراجعة الإعلان الرسمي.
    </div>

</main>

<section class="container" id="majors">

    <div class="section-title">
        <h2>📚 دليل التخصصات الأكاديمية</h2>
        <p>التخصصات الأدبية والعلمية والمهنية المتاحة للبحث.</p>
    </div>

    {% for category, majors in major_categories.items() %}

    <details class="details" style="background:white;padding:15px;margin-bottom:12px">

        <summary>{{ category }} ({{ majors|length }})</summary>

        <ul>
            {% for major in majors %}
            <li>{{ major }}</li>
            {% endfor %}
        </ul>

    </details>

    {% endfor %}

</section>

<section class="container" id="about">

    <div class="section-title">
        <h2>عن منصة منح العالم</h2>
        <p>
            منصة إرشادية مستقلة تساعد الطلاب على استكشاف المنح الدراسية
            ومقارنة شروطها ومتطلباتها في مختلف أنحاء العالم.
        </p>
    </div>

</section>

<footer>
    <h3>🎓 منح العالم</h3>
    <p>طريقك نحو مستقبل أكاديمي أفضل</p>
    <p>© 2026 جميع الحقوق محفوظة</p>
    <p>المنصة ليست جهة مانحة ولا تضمن القبول.</p>
</footer>

</body>
</html>
"""


# ==================================================
# محرك البحث والفلاتر
# ==================================================

@app.route("/")
def home():

    q = request.args.get("q", "").strip().casefold()

    selected_country = request.args.get(
        "country", ""
    ).strip()

    selected_continent = request.args.get(
        "continent", ""
    ).strip()

    selected_degree = request.args.get(
        "degree", ""
    ).strip()

    selected_major = request.args.get(
        "major", ""
    ).strip()

    scholarships = get_scholarships()

    if q:

        scholarships = [
            s for s in scholarships
            if q in " ".join([
                str(s.get("name", "")),
                str(s.get("country", "")),
                str(s.get("continent", "")),
                str(s.get("degree", "")),
                str(s.get("gpa", "")),
                str(s.get("majors", "")),
                str(s.get("funding", "")),
                str(s.get("description", ""))
            ]).casefold()
        ]

    if selected_country:
        scholarships = [
            s for s in scholarships
            if s.get("country") == selected_country
        ]

    if selected_continent:
        scholarships = [
            s for s in scholarships
            if selected_continent in s.get("continent", "")
        ]

    if selected_degree:
        scholarships = [
            s for s in scholarships
            if selected_degree in s.get("degree", "")
        ]

    if selected_major:
        scholarships = [
            s for s in scholarships
            if (
                selected_major in s.get("accepted_majors", [])
                or selected_major in s.get("majors", "")
            )
        ]

    all_scholarships = get_scholarships()

    countries_list = sorted(set(
        s["country"] for s in all_scholarships
        if s.get("country")
    ))

    continents_list = sorted(set(
        c.strip()
        for s in all_scholarships
        for c in s.get("continent", "").split(" و")
        if c.strip()
    ))

    degrees = [
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
        selected_major=selected_major,

        countries_list=countries_list,
        continents_list=continents_list,
        degrees=degrees,

        major_categories=MAJOR_CATEGORIES,

        total=len(all_scholarships),
        countries=len(countries_list),
        major_count=len(ALL_MAJORS),

        last_update=get_setting("last_update"),
        update_message=get_setting(
            "update_status",
            "لم تتم المزامنة بعد."
        )
    )


# ==================================================
# بدء التطبيق
# ==================================================

init_db()

scheduler = BackgroundScheduler(
    timezone=TIMEZONE
)

scheduler.add_job(
    daily_update,
    trigger="cron",
    hour=3,
    minute=0,
    id="daily_update",
    replace_existing=True
)

if not scheduler.running:
    scheduler.start()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
