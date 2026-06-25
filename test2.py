import requests

res = requests.post("http://localhost:8000/ask", json={
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "question": "Summary?"
})
print("Status:", res.status_code)
print("Data:", res.json())
