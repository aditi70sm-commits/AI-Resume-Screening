

from flask import Flask, request, jsonify, render_template
import pdfplumber

app = Flask(__name__)

# Maximum upload size: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# Open homepage
@app.route("/")
def home():
    return render_template("index.html")


# Receive and process resume
@app.route("/upload", methods=["POST"])
def upload_resume():

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    job = request.form.get("job", "").strip()

    resume = request.files.get("resume")

    if not name or not email or not job or not resume:
        return jsonify({"error": "Please complete all fields."}), 400

    if not resume.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF file."}), 400

    try:
        with pdfplumber.open(resume.stream) as pdf:
            extracted_text = "\n".join(
                page.extract_text() or "" for page in pdf.pages
            )

        if not extracted_text.strip():
            return jsonify({
                "error": "No readable text found in this PDF."
            }), 400

        return jsonify({
            "message": "Resume processed successfully!",
            "candidate": name,
            "email": email,
            "resume": resume.filename,
            "extracted_text": extracted_text[:2000],
            "job_description": job
        })

    except Exception:
        return jsonify({
            "error": "Could not read this PDF."
        }), 400


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "File is too large. Maximum size is 5 MB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True)
