"""Mostra a estrutura das páginas do Brawl Planet pra ajustar o leitor de mapas."""
import re
import urllib.request


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 brawl-picks-vigia/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


h = baixar("https://www.brawlplanet.com/pt-br/maps/hardrockmine_gemgrab")
print("h1:", re.findall(r"<h1[^>]*>(.*?)</h1>", h)[:2])
print("title:", re.findall(r"<title>(.*?)</title>", h)[:1])
ids = [(m.start(), m.group(1)) for m in re.finditer(r'id="([^"]*tab[^"]*)"', h)]
print("ids com tab:", ids[:20])
i = h.find("58.8", 190000)
print("--- contexto 202445 ---")
print(h[201200:205200])
slugs = re.findall(r'href="/pt-br/brawlers/([^"]+)"', h)
print("slugs de brawler:", len(slugs), sorted(set(slugs)))
