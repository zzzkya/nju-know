"""One-off, conservative collection of public list pages.

Review each site's robots/terms and seek authorization as needed before scheduling.
This script fetches one page per source and is intentionally NOT scheduled.
"""
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from app import init_db, connect

SOURCES = [
    {'name': '本科生院', 'url': 'https://jw.nju.edu.cn/ggtz/list.htm', 'category': '教务'},
    {'name': '校团委', 'url': 'https://tuanwei.nju.edu.cn/ggtz/list2.htm', 'category': '校园'},
    {'name': '国际关系学院', 'url': 'https://sis.nju.edu.cn/xshd/list.htm', 'category': '学术'},
]
DATE_RE = re.compile(r'20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}')
UA = 'NJU-Know-Student-Project/0.1 (+public-info-aggregator; contact-required-before-production)'


def parse_listing(html, source):
    soup = BeautifulSoup(html, 'html.parser')
    hostname = urlparse(source['url']).hostname
    seen = set()
    records = []
    for item in soup.select('li.news'):
        a = item.select_one('.news_title a[href]')
        published = item.select_one('.news_meta')
        if a is None or published is None:
            continue
        title = ' '.join((a.get('title') or a.get_text(' ', strip=True)).split())
        if not 8 <= len(title) <= 160:
            continue
        url = urljoin(source['url'], a.get('href',''))
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https') or parsed.hostname != hostname:
            continue
        if not re.search(r'(/|\.)[a-z0-9_-]+\.htm(?:l)?$', parsed.path, re.I):
            continue
        if url in seen or url.rstrip('/') == source['url'].rstrip('/'):
            continue
        # These sources keep the publication date beside, not inside, the title.
        # Read only this item's date field to avoid borrowing dates from titles
        # or neighboring announcements.
        m = DATE_RE.fullmatch(published.get_text(' ', strip=True))
        date = None
        if m:
            try:
                date = datetime.strptime(m.group().replace('/','-').replace('.','-'), '%Y-%m-%d').date().isoformat()
            except ValueError:
                pass
        if not date:
            continue  # Reject ambiguous entries rather than invent a date.
        seen.add(url)
        records.append((title, source['name'], url, date, source['category']))
    return records


def collect():
    init_db()
    total = 0
    for source in SOURCES:
        try:
            r = requests.get(source['url'], headers={'User-Agent': UA}, timeout=15)
            r.raise_for_status()
            r.encoding = r.apparent_encoding or r.encoding
            records = parse_listing(r.text, source)
            with connect() as db:
                for title, name, url, date, category in records:
                    cur = db.execute('''INSERT OR IGNORE INTO posts
                      (title,source,source_url,published_date,category)
                      VALUES (?,?,?,?,?)''', (title,name,url,date,category))
                    total += cur.rowcount
            print(f"{source['name']}: parsed {len(records)} dated entries")
        except requests.RequestException as e:
            print(f"{source['name']}: request failed: {e}")
    print(f'Inserted {total} new entries')


if __name__ == '__main__':
    collect()
