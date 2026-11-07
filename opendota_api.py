import requests
import json
from pathlib import Path
import time



#получаем json-данные матча по id
def fetch_match(pro_match_id):
    time.sleep(2)
    url = f"https://api.opendota.com/api/matches/{pro_match_id}"
    response = requests.get(url, timeout = 10)
    response.raise_for_status()
    match_data = response.json()
    return match_data

#получаем драфты
def extract_match(match_data):
    picks = match_data.get("picks_bans")
    if not picks:
        return None
    radiant_pick = []
    dire_pick = []
    for hero in picks:
        if hero["is_pick"] == True and hero["team"] == 0:
            radiant_pick.append(hero["hero_id"])

        if hero["is_pick"] == True and hero["team"] == 1:
            dire_pick.append(hero["hero_id"])
    if (len(radiant_pick) == 5 and len(dire_pick)  == 5 and len(set(radiant_pick)) == 5 and len(set(dire_pick)) == 5):
        return radiant_pick, dire_pick

#сохранение в json
def save_match(match_data, radiant_pick, dire_pick):
    data = {
        "match_id": match_data.get("match_id"),
        "radiant_heroes": radiant_pick,
        "dire_heroes": dire_pick,
        "radiant_score": match_data.get("radiant_score"),
        "dire_score": match_data.get("dire_score"),
        "radiant_win": match_data.get("radiant_win"),
        "match_duration": match_data.get("duration"),
        "start_time": match_data.get("start_time")
    }
    folder = Path("data/processed")
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder/f"{match_data.get('match_id')}.json"
    with open(file_path, "x", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def collect_matches():
    folder = Path("data/processed")
    folder.mkdir(parents=True, exist_ok=True)
    MAX_MATCHES = 1000
    url = "https://api.opendota.com/api/proMatches"
    try:
        respo = requests.get(url, timeout=30)
        respo.raise_for_status()
        matches = respo.json()

    except requests.exceptions.RequestException as error:
        print(f"Ошибка OpenDota API: {error}")
        return
    saved_total = len(list(folder.glob("*.json")))
    for match in matches:
        if saved_total >= MAX_MATCHES:
            print(f"[DONE] Достигнут лимит: {MAX_MATCHES} матчей")
            break
        match_id = match.get("match_id")

        file_path = Path("data/processed") / f"{match_id}.json"
        if file_path.exists():
            continue
        try:
            match_data = fetch_match(match_id)

        except requests.exceptions.RequestException as error:
            print(f"[ERROR] Матч {match_id}: {error}")
            continue
        pair = extract_match(match_data)
        if pair is None:
            continue
        radiant_pick, dire_pick = pair
        save_match(match_data, radiant_pick, dire_pick)
        saved_total += 1
        print(f"[SUCCESS] Матч {match_id} успешно обработан и сохранён!")

if __name__ == "__main__":
    collect_matches()


