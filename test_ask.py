import requests

res = requests.post("http://localhost:8000/ask", json={
    "video_url": "https://www.youtube.com/watch?v=iVDuUI-k1fE",
    "question": "Give me the summary of this video"
})
print(res.status_code)
print(res.json())
