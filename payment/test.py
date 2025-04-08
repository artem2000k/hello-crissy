import requests

url = 'https://api.merchant001.io/v2/payment-method/merchant/available?makeArray=1'
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJkNHFiR21INnR3WERqdXZ0V1lBakIzTTVGcXAxIiwiZGF0ZSI6IjIwMjQtMTAtMTZUMTI6NDg6MTkuMDEzWiIsImlhdCI6MTcyOTA4Mjg5OX0.n91aqd732-2fgtYdPPW8ftICskwBcERy0iNHs97VK7I",
    "Content-Type": "application/x-www-form-urlencoded"
}
result = requests.get(url, headers=headers).json()
avaible_currencies = []
for i in result:
    avaible_currencies.append(i['currency'])
print(avaible_currencies)