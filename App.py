from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, flash
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pdfkit
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///gdpr.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    organization = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ComplianceTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    deadline = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DataProcessingActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    data_categories = db.Column(db.Text, nullable=False)
    retention_period = db.Column(db.String(100))
    security_measures = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

def analyze_website(url):
    result = {
        "Website URL": url,
        "HTTPS Enabled": url.startswith("https://"),
        "Privacy Policy Found": False,
        "Cookie Banner Detected": False,
        "Terms & Conditions Page Found": False,
        "Contact Page Found": False,
        "Uses Cookies": False,
        "Compliance Score": 0,
        "Scan Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url if url.startswith("http") else "https://" + url)

        page_source = driver.page_source
        driver.quit()

        soup = BeautifulSoup(page_source, "html.parser")
        links = soup.find_all("a")
        for link in links:
            text = link.text.lower()
            href = link.get("href", "").lower()
            if "privacy" in text or "privacy" in href:
                result["Privacy Policy Found"] = True
            if "terms" in text or "terms" in href:
                result["Terms & Conditions Page Found"] = True
            if "contact" in text or "contact" in href:
                result["Contact Page Found"] = True
        
        if "cookie" in page_source.lower():
            result["Cookie Banner Detected"] = True
            result["Uses Cookies"] = True
        
        result["Compliance Score"] = sum([
            20 if result["HTTPS Enabled"] else 0,
            20 if result["Privacy Policy Found"] else 0,
            20 if result["Cookie Banner Detected"] else 0,
            20 if result["Terms & Conditions Page Found"] else 0,
            20 if result["Contact Page Found"] else 0
        ])
    except Exception as e:
        result["Error"] = str(e)

    return result

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400
    return jsonify(analyze_website(url))

WKHTMLTOPDF_PATH = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

@app.route("/download-report", methods=["POST"])
def download_report():
    data = request.json
    report_html = render_template("report.html", results=data)
    pdf_path = os.path.abspath("static/report.pdf")

    # Fix: Add 'file://' to handle local resources
    pdfkit.from_string(report_html, pdf_path, configuration=config, options={
        'page-size': 'A4',
        'encoding': "UTF-8",
        'enable-local-file-access': None  # Allow local file access
    })

    return send_file(pdf_path, as_attachment=True)

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = ComplianceTask.query.filter_by(user_id=current_user.id).all()
    activities = DataProcessingActivity.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', tasks=tasks, activities=activities)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        organization = request.form.get('organization')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
            
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            organization=organization
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        data = request.json
        task = ComplianceTask(
            title=data['title'],
            description=data.get('description', ''),
            deadline=datetime.fromisoformat(data['deadline']),
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({'message': 'Task created successfully'})
    
    tasks = ComplianceTask.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'deadline': task.deadline.isoformat()
    } for task in tasks])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
