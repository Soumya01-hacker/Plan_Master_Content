import urllib.request
from bs4 import BeautifulSoup
import json
from datetime import datetime

url = "https://services.licindia.in/LICEPS/portlets/visitor/CurrentNAV/CurrentNAVDay/CurrentNAVDayController.jpf"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        html = response.read()
except Exception as e:
    print(f"Error fetching URL: {e}")
    exit(1)

soup = BeautifulSoup(html, 'html.parser')

navDate = "Today"
labels = soup.find_all('label')
for label in labels:
    if "NAV FOR THE DATE" in label.text:
        navDate = label.text.replace("NAV FOR THE DATE :", "").strip()
        break

tables = soup.find_all('table', class_='commonTableBorder')
if not tables:
    print("No NAV tables found")
    exit(1)

table = tables[0]
rows = table.find_all('tr', class_='tableHeadingBG')

nav_data = []
current_plan = None

for row in rows:
    tds = row.find_all('td')
    if not tds: continue
    
    # Check if this is a Plan row
    if len(tds) == 2 and tds[0].get('colspan') == '2':
        planName = tds[0].text.strip()
        launchDateRaw = tds[1].text.strip()
        launchDate = launchDateRaw.replace('Launch Date:', '').strip()
        
        if 'Plan Name' in planName:
            continue
            
        current_plan = {
            "planName": planName,
            "launchDate": launchDate,
            "funds": []
        }
        nav_data.append(current_plan)
        
    elif len(tds) == 6 and current_plan is not None:
        fundName = tds[0].text.strip()
        if 'Fund' in fundName:
            continue
            
        sfinNo = tds[1].text.strip()
        faceValue = tds[2].text.strip()
        nav = tds[3].text.strip()
        repurchaseValue = tds[4].text.strip()
        saleValue = tds[5].text.strip()
        
        current_plan["funds"].append({
            "fundName": fundName,
            "sfinNo": sfinNo,
            "faceValue": faceValue,
            "nav": nav,
            "repurchaseValue": repurchaseValue,
            "saleValue": saleValue
        })

output = {
    "navDate": navDate,
    "lastUpdated": datetime.utcnow().isoformat(),
    "plans": nav_data
}

with open("nav_data.json", "w") as f:
    json.dump(output, f, indent=4)

print("Successfully saved nav_data.json")
