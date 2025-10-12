import google.generativeai as genai
import os
import traceback

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Debug: Print API key status
if GEMINI_API_KEY:
    print(f"✅ GEMINI_API_KEY found: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
else:
    print("❌ GEMINI_API_KEY not found in environment variables!")
    
genai.configure(api_key=GEMINI_API_KEY)

# Initialize model - Using the correct model name from the list
try:
    model = genai.GenerativeModel('models/gemini-2.5-flash')  # ⬅️ CORRECTED
    print("✅ Gemini model initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Gemini model: {str(e)}")
    model = None

def generate_personalized_feedback(resume_text, job_description, match_score, keywords_found, keywords_missing):
    """Generate detailed, personalized feedback using Gemini AI"""
    if not model:
        return f"Unable to generate detailed feedback at this time. Basic analysis: Your resume has a {match_score}% match. Focus on adding these skills: {', '.join(keywords_missing[:5])}."
    
    prompt = f"""You are an expert career coach and resume writer. Analyze this resume against the job description and provide specific, actionable feedback.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

CURRENT ANALYSIS:
- Match Score: {match_score}%
- Keywords Found: {', '.join(keywords_found[:10])}
- Keywords Missing: {', '.join(keywords_missing[:10])}

Please provide:
1. **Overall Assessment** (2-3 sentences about the current match)
2. **Specific Strengths** (3 things this resume does well for this job)
3. **Critical Gaps** (3 most important things missing)
4. **Action Items** (5 specific changes to make, with examples)
5. **Keyword Integration Tips** (How to naturally add missing keywords)

Be specific, encouraging, and actionable. Focus on what the candidate CAN control."""

    try:
        print("🔄 Sending request to Gemini API for feedback...")
        response = model.generate_content(prompt)
        print("✅ Gemini API response received successfully")
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error in generate_personalized_feedback: {str(e)}")
        traceback.print_exc()
        return f"Unable to generate detailed feedback at this time. Error: {str(e)}. Basic analysis: Your resume has a {match_score}% match. Focus on adding these skills: {', '.join(keywords_missing[:5])}."

def generate_optimized_resume(resume_text, job_description, keywords_missing):
    """Generate an optimized version of the resume tailored to the job"""
    if not model:
        print("❌ Model not initialized")
        return None
        
    prompt = f"""You are an expert resume writer. Rewrite this resume to better match the job description while maintaining the candidate's authentic experience and achievements.

ORIGINAL RESUME:
{resume_text[:4000]}

TARGET JOB DESCRIPTION:
{job_description[:2000]}

MISSING KEYWORDS TO INTEGRATE:
{', '.join(keywords_missing[:15])}

INSTRUCTIONS:
1. Keep all real experiences and achievements - DO NOT fabricate
2. Rephrase bullets to include relevant keywords naturally
3. Emphasize experiences that match the job requirements
4. Add a professional summary tailored to this role
5. Reorganize sections to highlight most relevant experience first
6. Use action verbs and quantify achievements where possible
7. Integrate missing keywords ONLY where they genuinely apply

FORMAT: Return the complete optimized resume in a clean, professional format.

IMPORTANT: Be honest - only include keywords where the candidate actually has that experience."""

    try:
        print("🔄 Sending request to Gemini API for optimized resume...")
        response = model.generate_content(prompt)
        print("✅ Gemini API response received successfully")
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error in generate_optimized_resume: {str(e)}")
        traceback.print_exc()
        return None

def generate_cover_letter(resume_text, job_description, company_name, job_title):
    """Generate a tailored cover letter"""
    if not model:
        print("❌ Model not initialized")
        return None
        
    prompt = f"""Write a compelling cover letter for this candidate applying to {company_name} for the {job_title} position.

CANDIDATE'S RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

REQUIREMENTS:
1. Professional yet personable tone
2. 3-4 paragraphs (250-300 words)
3. Highlight 2-3 most relevant experiences
4. Show genuine interest in the company/role
5. Include a strong closing call-to-action
6. Use specific examples from their resume

Make it unique and authentic, not generic."""

    try:
        print("🔄 Sending request to Gemini API for cover letter...")
        response = model.generate_content(prompt)
        print("✅ Gemini API response received successfully")
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error in generate_cover_letter: {str(e)}")
        traceback.print_exc()
        return None

def suggest_missing_experience(keywords_missing, resume_text):
    """Suggest how to gain or highlight missing skills"""
    if not model:
        return None
        
    prompt = f"""The candidate is missing these skills for their target role: {', '.join(keywords_missing[:10])}

Based on their resume background:
{resume_text[:2000]}

Provide 5 specific, actionable suggestions for how they could:
1. Gain these skills (online courses, projects, certifications)
2. Highlight existing transferable experience
3. Reframe their experience to show these skills

Be specific with course names, project ideas, and phrasing examples."""

    try:
        print("🔄 Sending request to Gemini API for skill suggestions...")
        response = model.generate_content(prompt)
        print("✅ Gemini API response received successfully")
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error in suggest_missing_experience: {str(e)}")
        traceback.print_exc()
        return None