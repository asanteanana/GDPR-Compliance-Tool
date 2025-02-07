from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pdfkit
import os
from datetime import datetime

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

@app.route("/")
def index():
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
