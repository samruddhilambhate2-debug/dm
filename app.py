from flask import Flask, render_template, request, redirect
import pandas as pd
import os
import matplotlib.pyplot as plt

app = Flask(__name__)
UPLOAD_FOLDER = "resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Make sure the resumes folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load CSVs
users = pd.read_csv("users.csv")
jobs = pd.read_csv("jobs.csv")
if os.path.exists("skills.csv"):
    data = pd.read_csv("skills.csv")
else:
    data = pd.DataFrame(columns=["name","skills"])

# ----------------------
# Helper functions
# ----------------------
def score_candidate(skills_text):
    """Give score based on key skills"""
    skills = skills_text.lower()
    score = 0
    if "python" in skills: score += 5
    if "machine learning" in skills: score += 5
    if "data mining" in skills: score += 4
    if "sql" in skills: score += 3
    return score

def recommend_job(skills_text):
    s = skills_text.lower()
    if "machine learning" in s: return "Data Scientist"
    if "python" in s: return "Data Analyst"
    if "html" in s: return "Web Developer"
    if "sql" in s: return "Database Analyst"
    return "Software Developer"

def create_chart():
    """Generate pie chart of skills distribution"""
    python = sum(data["skills"].str.lower().str.contains("python"))
    ml = sum(data["skills"].str.lower().str.contains("machine learning"))
    web = sum(data["skills"].str.lower().str.contains("html"))
    sql = sum(data["skills"].str.lower().str.contains("sql"))

    labels = ["Python","Machine Learning","Web","SQL"]
    values = [python, ml, web, sql]

    plt.figure()
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title("Skill Distribution")
    plt.savefig("static/chart.png")
    plt.close()

# ----------------------
# Routes
# ----------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users[(users["username"]==username)&(users["password"]==password)]
        if not user.empty:
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    create_chart()
    ranked = data.copy()
    ranked["score"] = ranked["skills"].apply(score_candidate)
    ranked["recommended_job"] = ranked["skills"].apply(recommend_job)
    ranked = ranked.sort_values(by="score", ascending=False)
    table = ranked.to_html(classes="table", index=False)
    return render_template("dashboard.html", table=table)

@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        files = request.files.getlist("resumes")
        for file in files:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)
            text = open(path, "r", encoding="utf-8", errors="ignore").read()
            data.loc[len(data)] = [file.filename.split(".")[0], text]
        data.to_csv("skills.csv", index=False)
        return redirect("/dashboard")
    return render_template("upload.html")

@app.route("/jobs")
def jobs_page():
    table = jobs.to_html(classes="table", index=False)
    return render_template("jobs.html", table=table)

if __name__ == "__main__":
    app.run(debug=True)