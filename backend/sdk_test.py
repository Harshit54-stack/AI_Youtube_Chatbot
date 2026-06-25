from groq import Groq

client = Groq(
    api_key="PASTE_NEW_KEY_HERE"
)

response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)

print(response.choices[0].message.content)