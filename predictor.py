import requests
import re
import ast
import math
from lxml import html

AGE_START = 14
AGE_TARGET = 22

SKILL_ORDER = [
    'IS', 'OS', 'RNG', 'FIN', 'REB', 'ID', 'PD',
    'IQ', 'PASS', 'HND', 'DRV', 'STR', 'SPD', 'STA'
]

LABEL_MAP = {
    "Inside Shot": "IS", "Outside Shot": "OS", "Shooting Range": "RNG",
    "Finishing": "FIN", "Rebounding": "REB", "Interior Defense": "ID",
    "Perimeter Defense": "PD", "Basketball IQ": "IQ", "Passing": "PASS",
    "Ball Handling": "HND", "Driving": "DRV", "Strength": "STR",
    "Speed": "SPD", "Stamina": "STA"
}

def scrape_current_skills_and_pot(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception("Failed to fetch player page.")
    tree = html.fromstring(resp.content)
    rows = tree.xpath("//table[1]//tr")

    skills = {}
    age = None
    pot = None

    for row in rows:
        cells = row.xpath("./td")
        if len(cells) == 0:
            continue

        left_text = cells[0].text_content().strip()
        if left_text.startswith("Age:"):
            try:
                age = int(left_text.split("Age:")[1].strip())
            except:
                pass

        if len(cells) == 5:
            for i, j in [(1, 2), (3, 4)]:
                label = cells[i].text_content().strip().strip(':')
                value_node = cells[j].xpath(".//text()[normalize-space()]")
                value = next((v.strip() for v in value_node if v.strip().isdigit()), None)
                if label in LABEL_MAP and value:
                    skills[LABEL_MAP[label]] = int(value)

        if len(cells) >= 3 and 'Potential:' in cells[1].text_content():
            try:
                pot = int(cells[2].text_content().strip())
            except:
                pass

    return age, skills, pot

def scrape_initial_skills(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception("Failed to fetch development page.")
    text = resp.text
    scripts = re.findall(r"<script.*?>.*?</script>", text, re.DOTALL)

    initial = {}
    for script in scripts:
        title_match = re.search(r"title:\s*'([^']+)'", script)
        array_match = re.search(r"arrayToDataTable\(\s*(\[\[.*?\]\])\s*\)", script, re.DOTALL)
        if not title_match or not array_match:
            continue
        array_str = array_match.group(1).replace("null", "None")
        try:
            data = ast.literal_eval(array_str)
            if len(data) < 2:
                continue
            header = data[0][1:]
            first_row = data[1][1:]
            for h, v in zip(header, first_row):
                if isinstance(v, int) and h:
                    short = LABEL_MAP.get(h.strip(), h.strip().upper())
                    initial[short] = v
        except:
            continue
    return initial

def predict_skills(initial, current, age_now, pot):
    predicted = {}
    si_cap = int(pot * 15.5) if pot is not None else None

    raw = {}
    for skill in SKILL_ORDER:
        init = initial.get(skill)
        curr = current.get(skill)
        if init is None or curr is None:
            raw[skill] = None
        else:
            growth = (curr - init) / (age_now - AGE_START) if age_now > AGE_START else 0
            raw[skill] = curr + (AGE_TARGET - age_now) * growth

    # Pre-floor values but cap at 20
    floored = {
        s: math.floor(min(v, 20)) if v is not None else None
        for s, v in raw.items()
    }

    total_si = sum(v for v in floored.values() if v is not None)
    capped = False

    if si_cap is not None and total_si > si_cap:
        scaling_factor = si_cap / total_si
        adjusted = {}
        for s, v in raw.items():
            if v is None:
                adjusted[s] = None
                continue
            scaled = v * scaling_factor
            # Floor scaled value, cap at 20, and never drop below current skill
            adjusted_value = max(math.floor(min(scaled, 20)), current.get(s, 0))
            adjusted[s] = adjusted_value
        predicted = adjusted
        capped = True
    else:
        predicted = floored

    final_si = sum(v for v in predicted.values() if v is not None)
    return predicted, final_si, capped

def run_prediction(url):
    url = url.strip()
    url_current = url
    url_dev = url if url.endswith("/D") else url.rstrip("/") + "/D"

    age_now, current_skills, pot = scrape_current_skills_and_pot(url_current)
    initial_skills = scrape_initial_skills(url_dev)
    predicted_skills, predicted_si, was_capped = predict_skills(initial_skills, current_skills, age_now, pot)

    return {
        "age": age_now,
        "pot": pot,
        "initial": initial_skills,
        "current": current_skills,
        "predicted": predicted_skills,
        "predicted_si": predicted_si,
        "si_capped": was_capped
    }
