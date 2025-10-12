import google.generativeai as genai

genai.configure(api_key="AIzaSyCHWxD9xDklPZ5JaibfEO4tf2gJHq3FJ9I")  # Your key

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")