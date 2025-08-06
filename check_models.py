import google.generativeai as genai
import os

# paste model yang kamu pilih disini yaa :)
genai.configure(api_key='YOUR_API_KEY')

print("Daftar model yang tersedia untuk generateContent:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")