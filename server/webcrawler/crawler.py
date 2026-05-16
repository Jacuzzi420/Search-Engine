from trafilatura.spider import extract_links
from urllib.parse import urlsplit
from collections import deque
from protego import Protego
from pathlib import Path
import trafilatura
import requests
import random
import time

BOTNAME = 'MyCrawl/1.0 (+https://github.com/Jacuzzi420/Search-Engine)'

HEADERS = {
    'User-Agent': BOTNAME,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

def get_robots(robots_url: str) -> Protego:
    try:
        response = requests.get(robots_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except:
        return None

    return Protego.parse(response.text)

def clear_data():
    for element in Path('data/').iterdir():
        if element.is_file(): element.unlink()

def get_crawled_data() -> tuple[int, set[str]]:
    visited = set()
    index = 0

    try:
        with open('data/description.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                file, title, url = line.split('|')
                visited.add(url.strip())
                index = int(file)

    except FileNotFoundError:
        print("Nie znaleziono pliku")
    except UnicodeDecodeError:
        print("Złe kodowanie")

    return index + 1, visited

def crawl(seeds: list[str], load_data=False) -> None:
    index = 0
    robots = dict()
    visited = set()
    queue = deque(seeds)

    if load_data:
        index, visited = get_crawled_data()
    else: clear_data()

    while queue:
        url = queue.popleft()

        if url in visited: continue
        visited.add(url)

        url_split = urlsplit(url)
        if url_split.netloc != 'en.wikipedia.org': continue

        robots_url = f"{url_split.scheme}://{url_split.netloc}/robots.txt"
        if robots_url not in robots:
            robots[robots_url] = get_robots(robots_url)

        if not robots[robots_url].can_fetch(url, BOTNAME): continue

        delay = robots[robots_url].crawl_delay(BOTNAME)
        if delay: time.sleep(delay)
        else: time.sleep(random.randint(3, 8))

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except:
            print(f"REQUEST ERROR WITH CODE: {response.status_code}")
            return
        
        text_cleaned = trafilatura.extract(response.text)
        metadata = trafilatura.extract_metadata(response.text)
        links = extract_links(response.text, url)

        with open(f'data/{index}.txt', "w", encoding="utf-8") as file:
            file.write(text_cleaned)
        
        with open(f'data/description.txt', "a", encoding="utf-8") as file:
            file.write(f"{index} | {metadata.title} | {url}\n")

        queue.extend(links)
        index += 1
        
if __name__ == "__main__":
    seeds = ['https://en.wikipedia.org/wiki/Kanye_West']
    crawl(seeds, load_data=True)