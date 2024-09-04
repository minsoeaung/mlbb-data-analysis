import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://mobile-legends.fandom.com/wiki/List_of_heroes'
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table')

headers = ['Hero Id', 'Hero']
heroes = []

rows = table.find_all('tr')

for row in rows[1:]:  # Skip the header row
    cells = row.find_all('td')
    if len(cells) > 1:
        hero_id = cells[2].text.strip()
        hero_name = cells[1].text.strip()
        hero_name = str.split(hero_name, ',')[0]
        if hero_id and hero_name:
            heroes.append({'Hero Id': hero_id, 'Hero': hero_name})

# Convert to DataFrame and save to CSV
df = pd.DataFrame(heroes, columns=headers)
df.to_csv('heroes.csv', index=False)
print('Scraping completed. Data saved to heroes.csv')
