from flask import Flask, render_template
import os

# تعريف متغير التطبيق الأساسي بالاسم الصحيح app
app = Flask(__name__)

@app.route('/')
def home():
    return "مرحباً بك في تطبيق المنح الدراسية يعمل بنجاح!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
