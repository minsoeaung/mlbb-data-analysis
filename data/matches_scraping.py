import csv

import requests
from bs4 import BeautifulSoup


def check_green_tick(result_elem):
    if result_elem.find('i') is not None:
        # if 'green' in result_elem.find('i').get('class').lower():
        return 1
    elif result_elem.find('img') is not None:
        if 'no' in result_elem.find('img').get('src').lower():
            return 0
    else:
        return None


def parse_pick_elem(team_pick_elem):
    hero_elems = team_pick_elem.find_all('div')
    hero_colors = []
    hero_names = []

    for hero_elem in hero_elems:

        # get team color
        curr_hero_color = hero_elems[0].get('class')[0]
        if 'blue' in curr_hero_color:
            hero_colors.append('blue')
        elif 'red' in curr_hero_color:
            hero_colors.append('red')
        else:
            hero_colors.append('unknown')

        # get hero names
        hero_a_tag = hero_elem.find('a')
        if hero_a_tag is not None:
            hero_name = hero_a_tag.get('title')
            hero_names.append(hero_name)

    # get team side
    first_color = hero_colors[0]

    # Compare the first element with the rest of the elements
    if all(element == first_color for element in hero_colors):
        team_side = first_color
    else:
        team_side = None

    return team_side, hero_names


matches = []

with open('urls.txt', 'r') as file:
    links = file.read().splitlines()

count = 0

for link in links:
    count = count + 1
    print(f"{count}/{len(links)}, Scrapping from {link}")

    response = requests.get(link)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        continue
    soup = BeautifulSoup(response.content, 'html.parser')

    matches_popup_element = soup.find_all('div', class_='brkts-popup brkts-match-info-popup')

    for matches_popup in matches_popup_element:
        matches_body = matches_popup.find('div', class_='brkts-popup-body')
        game_rows = matches_body.find_all('div', class_='brkts-popup-body-element brkts-popup-body-game')
        if len(game_rows) == 0:
            continue

        for game_row in game_rows:
            t1_sides_data = []
            t1_picks_data = []
            t1_result_data = []

            t2_sides_data = []
            t2_picks_data = []
            t2_result_data = []

            pick_elems = game_row.find_all('div', attrs={'class': False})

            team_a_picks = pick_elems[0]
            team_a_heroes = team_a_picks.find_all('div')

            team_b_picks = pick_elems[1]
            team_b_heroes = team_b_picks.find_all('div')

            t1_side, t1_heroes = parse_pick_elem(team_a_picks)
            t2_side, t2_heroes = parse_pick_elem(team_b_picks)

            if len(t1_heroes) == 0 and len(t2_heroes) == 0:
                continue

            t1_sides_data.append(t1_side)
            t1_picks_data.append(t1_heroes)
            t2_sides_data.append(t2_side)
            t2_picks_data.append(t2_heroes)

            result_elems = game_row.find_all('div', class_="brkts-popup-spaced")
            t1_res_elem = result_elems[0]
            t2_res_elem = result_elems[1]
            t1_result = check_green_tick(t1_res_elem)
            t2_result = check_green_tick(t2_res_elem)

            t1_result_data.append(t1_result)
            t2_result_data.append(t2_result)

            combined_pick = t1_picks_data[0] + t2_picks_data[0] + [t1_result]

            print(f"Got {combined_pick}")

            matches.append(combined_pick)

hero_name_to_id = {}

with open('heroes.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        hero_name_to_id[row['Hero']] = row['Hero Id']

for match in matches:
    for i in range(10):  # Replace only the first 10 elements (H1 to H10)
        match[i] = hero_name_to_id.get(match[i], match[i])  # Repl

with open('matches.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'Result'])
    writer.writerows(matches)

print("CSV file matches.csv is created!")
