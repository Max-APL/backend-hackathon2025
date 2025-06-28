


import requests

url = "https://maxpasten.app.n8n.cloud/webhook-test/f182d304-1d67-4798-bd58-24dc84caec48"  # tu Production URL real
response = requests.get(url)

print("Código:", response.status_code)
print("Respuesta:", response.text)
