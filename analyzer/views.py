from django.shortcuts import render
from .forms import ResumeForm
import PyPDF2
import spacy

nlp = spacy.load("en_core_web_sm")

def analyze_resume(text):
    doc = nlp(text)

    # 🔹 Extract nouns (skills candidates)
    skills = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            skills.append(token.text.lower())

    # Remove duplicates
    skills = list(set(skills))

    # 🔹 Known tech filter
    tech_keywords = [
        "python", "django", "ai", "machine learning", "deep learning",
        "tensorflow", "pytorch", "docker", "kubernetes",
        "c++", "java", "javascript", "linux", "api"
    ]

    found_skills = [skill for skill in skills if skill in tech_keywords]

    # 🔹 Score logic
    score = min(len(found_skills) * 2, 10)

    if score < 4:
        level = "Beginner"
    elif score < 7:
        level = "Intermediate"
    else:
        level = "Advanced"

    # 🔹 Suggestions
    suggestions = []

    if "experience" not in text.lower():
        suggestions.append("Add work experience section")

    if "project" not in text.lower():
        suggestions.append("Add projects section")

    if len(found_skills) < 5:
        suggestions.append("Improve technical skill set")

    return f"""
Skills Detected: {', '.join(found_skills)}

Experience Level: {level}

Score: {score}/10

Suggestions:
- {'\n- '.join(suggestions)}
"""

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text


def home(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()

            file_path = resume.file.path
            with open(file_path, 'rb') as f:
                text = extract_text_from_pdf(f)

            # 🔥 AI Analysis
            analysis = analyze_resume(text)

            return render(request, 'result.html', {
                'text': text,
                'analysis': analysis
            })

    else:
        form = ResumeForm()

    return render(request, 'home.html', {'form': form})