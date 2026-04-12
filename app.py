from flask import Flask, render_template, request, send_file
from flask_cors import CORS
from PIL import Image
import os
from io import BytesIO
import base64
from PIL import Image
import io
# PDF Libraries
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from google import genai

app = Flask(__name__)
CORS(app)

# Read API key strictly from Environment Variables (Secure for GitHub)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable is not set!")

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"WARNING: Failed to initialize Gemini Client: {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            waste_file = request.files.get("waste_image")
            if not waste_file:
                return render_template("index.html", result=False, error="No image uploaded.")

            waste_img = Image.open(waste_file)
            waste_img.thumbnail((512, 512))


            prompt = """
            Classify this image into exactly one of these categories and respond with ONLY the category name, nothing else: General, Medical, Hazardous/Chemical, Sharps, Hybrid Waste
            """

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=[prompt, waste_img]
            )
            return render_template("index.html", result=True, report=response.text)

        except Exception as e:
            print(f"Server Error: {e}")
            return render_template("index.html", result=False, error=str(e))

    return render_template("index.html", result=False)


@app.route("/download-report", methods=["POST"])
def download_report():
    report_text = request.form.get("report_content")
    if not report_text:
        return "No report content found", 400

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=20,
        textColor=colors.HexColor("#ff7675"),
    )

    story = [
        Paragraph("MEDICAL WASTE ANALYSIS REPORT", title_style),
        Spacer(1, 12),
    ]

    clean_text = report_text.replace("**", "").replace("#", "").replace("*", "")
    for line in clean_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="Waste_Classification_Report.pdf",
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
