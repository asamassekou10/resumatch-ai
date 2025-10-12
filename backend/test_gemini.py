import google.generativeai as genai

API_KEY = "AIza..."  

print("Testing Gemini 2.5 Flash...")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

response = model.generate_content("Say 'Hello, ResuMatch AI is working!' in one sentence.")
print("✅ SUCCESS!")
print(f"Response: {response.text}")
