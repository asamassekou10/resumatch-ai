import PyPDF2
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from io import BytesIO

# Load spaCy model (you'll need to download: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("WARNING: spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

def extract_text_from_pdf(file_stream):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"PDF parsing failed: {str(e)}")

def extract_text_from_docx(file_stream):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_stream)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise Exception(f"DOCX parsing failed: {str(e)}")

def extract_text_from_file(file):
    """Extract text from uploaded file (PDF or DOCX)"""
    filename = file.filename.lower()
    file_stream = BytesIO(file.read())
    
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file_stream)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(file_stream)
    elif filename.endswith('.txt'):
        return file_stream.read().decode('utf-8')
    else:
        raise Exception("Unsupported file format. Please upload PDF, DOCX, or TXT")

def extract_keywords_tfidf(text, top_n=20):
    """Extract keywords using TF-IDF"""
    # Clean and tokenize
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s+#]', ' ', text)
    
    # Use TF-IDF to find important keywords
    vectorizer = TfidfVectorizer(
        max_features=top_n,
        stop_words='english',
        ngram_range=(1, 3),  # Unigrams, bigrams, and trigrams
        min_df=1
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        
        # Get scores for each keyword
        scores = tfidf_matrix.toarray()[0]
        keyword_scores = list(zip(feature_names, scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [kw for kw, score in keyword_scores if score > 0]
    except:
        # Fallback: simple word frequency
        words = text.split()
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:top_n]

def extract_skills_with_ner(text):
    """Extract skills using Named Entity Recognition with spaCy"""
    if not nlp:
        return []
    
    doc = nlp(text)
    skills = set()
    
    # Common skill patterns
    skill_patterns = [
        'python', 'java', 'javascript', 'react', 'vue', 'angular', 'node',
        'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'docker',
        'kubernetes', 'machine learning', 'data analysis', 'api', 'rest',
        'agile', 'scrum', 'git', 'ci/cd', 'testing', 'flask', 'django',
        'html', 'css', 'typescript', 'express', 'redux', 'graphql'
    ]
    
    text_lower = text.lower()
    for skill in skill_patterns:
        if skill in text_lower:
            skills.add(skill)
    
    # Extract entities that might be skills (ORG, PRODUCT, etc.)
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
            if len(ent.text) > 2 and len(ent.text) < 30:
                skills.add(ent.text.lower())
    
    return list(skills)

def calculate_match_score(resume_text, job_description):
    """Calculate similarity score between resume and job description"""
    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(similarity * 100, 2)
    except:
        # Fallback: simple word overlap
        resume_words = set(resume_text.lower().split())
        job_words = set(job_description.lower().split())
        overlap = len(resume_words.intersection(job_words))
        total = len(job_words)
        return round((overlap / total) * 100, 2) if total > 0 else 0

def generate_suggestions(keywords_missing, match_score):
    """Generate actionable suggestions for the user"""
    suggestions = []
    
    if match_score < 50:
        suggestions.append("Your resume shows limited alignment with this job description. Consider tailoring your resume to highlight relevant experience.")
    elif match_score < 70:
        suggestions.append("Your resume is moderately aligned. Focus on incorporating the missing keywords where they genuinely reflect your experience.")
    else:
        suggestions.append("Strong alignment! Your resume matches well with this job description.")
    
    if len(keywords_missing) > 10:
        suggestions.append(f"Consider adding {len(keywords_missing)} key skills from the job description to your resume, particularly: {', '.join(keywords_missing[:5])}.")
    elif len(keywords_missing) > 0:
        suggestions.append(f"Add these important keywords where relevant: {', '.join(keywords_missing[:5])}.")
    else:
        suggestions.append("You've covered all major keywords from the job description!")
    
    suggestions.append("Ensure your experience section uses action verbs and quantifiable achievements.")
    suggestions.append("Tailor your summary or objective statement to match the job requirements.")
    
    return " ".join(suggestions)

def process_resume_analysis(resume_file, job_description):
    """
    Main function to process resume analysis
    Returns: dict with match_score, keywords_found, keywords_missing, suggestions
    """
    # Extract text from resume
    resume_text = extract_text_from_file(resume_file)
    
    if not resume_text or len(resume_text) < 50:
        raise Exception("Could not extract text from resume. Please ensure the file is not corrupted or try a different format.")
    
    # Extract keywords from both documents
    resume_keywords = set(extract_keywords_tfidf(resume_text, top_n=30))
    resume_skills = set(extract_skills_with_ner(resume_text))
    resume_all = resume_keywords.union(resume_skills)
    
    job_keywords = set(extract_keywords_tfidf(job_description, top_n=30))
    job_skills = set(extract_skills_with_ner(job_description))
    job_all = job_keywords.union(job_skills)
    
    # Find matches and gaps
    keywords_found = list(resume_all.intersection(job_all))
    keywords_missing = list(job_all - resume_all)
    
    # Calculate match score
    match_score = calculate_match_score(resume_text, job_description)
    
    # Generate suggestions
    suggestions = generate_suggestions(keywords_missing, match_score)
    
    return {
        'match_score': match_score,
        'keywords_found': keywords_found[:20],  # Limit to top 20
        'keywords_missing': keywords_missing[:20],  # Limit to top 20
        'suggestions': suggestions,
        'resume_text': resume_text[:500]  # Store excerpt for reference
    }