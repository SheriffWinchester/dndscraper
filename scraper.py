import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import csv

def main():
    URL = "https://5esrd.kyiv.ua/docs/spellcasting/indexes/index_all_list.html"
    base_URL = "https://5esrd.kyiv.ua/"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    spell_elements = soup.select("div.page li")
    for index, element in enumerate(spell_elements):
        relative_url = element.find('a')['href']  # Extract the href attribute
        full_url = urljoin(base_URL, relative_url)  # Join the base URL with the relative URL
        link_page = requests.get(full_url)  # Open the link

        link_soup = BeautifulSoup(link_page.content, "html.parser")
        div_page = link_soup.select_one("div.page")
        first_p = div_page.find("p")
        first_p_text = first_p.get_text()

        level_spell = get_level_spell(first_p_text, div_page, link_soup)
        print(level_spell)
        spell_name = get_spell_name(link_soup, re)
        print(spell_name)
        school_spell = get_school_spell(first_p_text, div_page, link_soup)
        print(school_spell)
        casting_time = get_casting_time(first_p_text, div_page, link_soup)
        print(casting_time)
        range_spell = get_range_spell(first_p_text, div_page, link_soup)
        print(range_spell)
        components_spell = get_components_spell(first_p_text, div_page, link_soup)
        print(components_spell)
        duration_spell = get_duration_spell(first_p_text, div_page, link_soup)
        print(duration_spell)
        description_spell = get_description_spell(first_p_text, div_page, link_soup)
        print(description_spell)
        class_spell = get_class_spell(first_p_text, div_page, link_soup)
        print(class_spell)

        # Open the CSV file in write mode
        with open('spells.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            # Write the header row
            #writer.writerow(["Spell Name", "School Spell", "Casting Time", "Range Spell", "Components Spell", "Duration Spell", "Description Spell"])
            # Write the data row
            writer.writerow([level_spell, spell_name, school_spell, casting_time, range_spell, components_spell, duration_spell, description_spell, class_spell])

        print("Progress: ", index)

    


def get_level_spell(first_p_text, div_page, link_soup):
    # Find the position of the <em> tag and the semicolon
    start = first_p_text.find("<em>") + 1  # Add 4 to exclude the <em> tag itself
    end = first_p_text.find(";")

    # Extract the text between the <em> tag and the semicolon
    text = first_p_text[start:end]

    # Search for digits in the text
    number = re.search(r'\d+', text)

    #Return the level number if found, otherwise it is a cantrip
    return number.group() if number else "0"


def get_spell_name(link_soup, re):
    page_title_element = link_soup.select_one("h1.page-title")
    page_title_text = page_title_element.text
    # Filter out non-Cyrillic characters
    cyrillic_text = re.sub("[^а-яА-ЯёЁіІ\s]", "", page_title_text)
    return cyrillic_text

def get_school_spell(first_p_text, div_page, link_soup):
    # Find the position of the <em> tag and the semicolon
    start = first_p_text.find("<em>") + 1  # Add 4 to exclude the <em> tag itself
    end = first_p_text.find(";")

    # Extract the text between the <em> tag and the semicolon
    text = first_p_text[start:end]
    return text

def get_casting_time(first_p_text, div_page, link_soup):
    strong_tag = div_page.find('strong', string=re.compile('Час створення'))
    strong_tag_text = strong_tag.get_text()

    # Split the text at "Час створення" and take the second part
    parts = first_p_text.split(strong_tag_text, 1)
    casting_time = parts[1].strip() if len(parts) > 1 else None

    if casting_time is None:
        return 0

    # Further split the casting_time at the first space and take the first two parts
    casting_time_parts = casting_time.split(' ', 2)
    casting_time = ' '.join(casting_time_parts[:2]) if len(casting_time_parts) > 1 else None

    return casting_time

def get_range_spell(first_p_text, div_page, link_soup):
    strong_tag = div_page.find('strong', string=re.compile('Відстань'))
    strong_tag_text = strong_tag.get_text()

    # Split the text at "Відстань" and take the second part
    parts = first_p_text.split(strong_tag_text)
    range_spell = parts[1].strip().split() if len(parts) > 1 else None
    if range_spell is None:
        return 0
    range_spell = ' '.join(range_spell[0:2])
    return range_spell

def get_components_spell(first_p_text, div_page, link_soup):
    #Exception handling due to inaccuracy on the page in one of the link
    try:
        strong_tag = div_page.find('strong', string=re.compile('Складові'))
        strong_tag_text = strong_tag.get_text()

        # Split the text at "Складові" and take the second part
        parts = first_p_text.split(strong_tag_text)
        components_spell = parts[1].strip().split() if len(parts) > 1 else None

        if components_spell is None:
            return 0
        start = components_spell[0]
        end = components_spell.index('Тривалість:')

        components_spell = components_spell[:end]

        return ' '.join(components_spell)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_duration_spell(first_p_text, div_page, link_soup):
    strong_tag = div_page.find('strong', string=re.compile('Тривалість'))
    strong_tag_text = strong_tag.get_text()

    # Split the text at "Тривалість" and take the second part
    parts = first_p_text.split(strong_tag_text)
    duration_spell = parts[1].strip().split() if len(parts) > 1 else None
    
    if duration_spell is None:
        return 0
    return ' '.join(duration_spell)

def get_description_spell(first_p_text, div_page, link_soup):
    # Find all <p> tags after the first one
    p_tags = div_page.select("p")[1:]

    # Get the text within each <p> tag
    description_spell = [p.get_text().strip() for p in p_tags]

    # Join the descriptions into a single string
    description_spell = ' '.join(description_spell)

    return description_spell

def get_class_spell(first_p_text, div_page, link_soup):
    # Find the position of the <em> tag and the semicolon
    start = first_p_text.find(";") + 1 # Add 4 to exclude the <em> tag itself
    end = first_p_text.find("Час створення:")

    # Extract the text between the <em> tag and the semicolon
    text = first_p_text[start:end]

    if text is None:
        return 0
    return text.strip().capitalize()

if __name__ == "__main__":
    main()
