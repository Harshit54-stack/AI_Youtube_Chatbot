import os
import re

files_to_update = [
    r'd:\AI_Youtube_Chatbot\README.md',
    r'd:\AI_Youtube_Chatbot\DEPLOYMENT.md',
    r'd:\AI_Youtube_Chatbot\frontend\README.md'
]

for filepath in files_to_update:
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Groq Cloud -> Google Gemini
    content = content.replace("Groq Cloud", "Google Gemini")
    
    # 2. Groq-powered -> Gemini-powered
    content = content.replace("Groq-powered", "Gemini-powered")
    
    # 3. GROQ_API_KEY -> GOOGLE_API_KEY
    content = content.replace("GROQ_API_KEY", "GOOGLE_API_KEY")
    
    # 4. Groq API -> Google Gemini API
    content = content.replace("Groq API", "Google Gemini API")
    content = content.replace("Groq API key", "Google Gemini API key")
    
    # 5. console.groq.com -> aistudio.google.com/app/apikey
    content = content.replace("console.groq.com", "aistudio.google.com/app/apikey")
    
    # 6. Groq keys
    content = re.sub(r'gsk_[xX]+', 'AIzaSy...', content)
    content = content.replace("gsk_xxx", "AIzaSy...")

    # 7. Groq -> Gemini (General replacements)
    content = content.replace("ChatGroq", "ChatGoogleGenerativeAI")
    content = re.sub(r'\bGroq\b', 'Gemini', content)
    content = re.sub(r'\bgroq\b', 'gemini', content)
    
    # 8. Update Project overview in README
    overview_replacement = "An AI-powered YouTube RAG Chatbot built with React, FastAPI, LangChain, FAISS, HuggingFace Embeddings, YouTube Transcript API, and Google Gemini.\n\n* Google Gemini is the LLM provider.\n* Gemini generates answers from retrieved context.\n* Gemini is used for conversational reasoning."
    content = re.sub(r'A production-ready \*\*Retrieval-Augmented Generation \(RAG\)\*\* chatbot that answers questions about any YouTube video using its transcript\. Powered by.*?(?=\n\n)', overview_replacement, content, flags=re.DOTALL)
    
    # 9. Specific models replacement
    content = content.replace("llama-3.1-8b-instant", "gemini-1.5-flash")
    content = content.replace("llama-3.3-70b-versatile", "gemini-1.5-pro")
    content = content.replace("LLaMA 3.3 70B, LLaMA 3.1 8B, Gemma 2, Mixtral", "Gemini 1.5 Pro, Gemini 1.5 Flash")
    content = content.replace("LLaMA 3", "Gemini")

    # Architecture diagram spacing fix
    content = content.replace("ChatGoogleGenerativeAI (Google Gemini ⚡)        ← gemini-1.5-flash (default)", "ChatGoogleGenerativeAI (Google Gemini ⚡) ← gemini-1.5-flash (default)")

    # 10. Update Model table in README
    # We will just replace some names
    content = content.replace("llama3-8b-8192", "gemini-1.0-pro")
    content = content.replace("llama3-70b-8192", "gemini-1.5-pro-latest")
    content = content.replace("gemma2-9b-it", "gemini-1.5-flash-8b")
    content = content.replace("gemma-7b-it", "gemini-1.5-flash-latest")
    content = content.replace("mixtral-8x7b-32768", "gemini-ultra")
    
    # 11. Replace User -> Groq -> Response (Wait, checking DEPLOYMENT or README, actually the architecture diagram is what's there. The prompt said "Current documentation may show: User\n↓\nGroq\n↓\nResponse". I will just string replace)
    content = content.replace("User\n↓\nGroq\n↓\nResponse", "User\n↓\nGemini\n↓\nResponse")
    content = content.replace("User\n↓\nChatGroq\n↓\nResponse", "User\n↓\nGemini\n↓\nResponse")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Replacement complete!")
