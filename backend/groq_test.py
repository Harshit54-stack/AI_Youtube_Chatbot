from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("GROQ_API_KEY")

print("Key prefix:", key[:10])
print("Key length:", len(key))
print("Starts with gsk_:", key.startswith("gsk_"))