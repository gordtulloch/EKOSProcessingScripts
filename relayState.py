import requests

Relay_Results = []
Cyfry = []
Stan = []
Wyniki = []

# The URL of the local page
url = 'http://10.0.0.101/30000/42'
response = requests.get(url)
if response.status_code == 200:
    page_content = response.text

    # Link the results to the next page
    url = 'http://10.0.0.101/30000/42'
    response = requests.get(url)
    if response.status_code == 200:
        page_content += response.text

# Divide the content of the page into lines
lines = page_content.split('/a')

# Search for lines containing "Relay-0"
Relay_Lines_Position = [line.find('Relay-0') for line in lines]

for i in range(len(Relay_Lines_Position)):
    if Relay_Lines_Position[i] > 0:
        Relay_Results.append(lines[i])
        Cyfry.append(int(lines[i][Relay_Lines_Position[i] + 7]))
        Stan.append('<font color="#00FF00">' in lines[i])

# Iterate through Digits and retrieve the appropriate State
for Cyfra in Cyfry:
    Wyniki.append(Stan[Cyfra-1])

# View relay status information
for i, element in enumerate(Wyniki):
    print(f"Relay {i+1}: {'ON' if element else 'OFF'}")

result = Wyniki

print(result)
