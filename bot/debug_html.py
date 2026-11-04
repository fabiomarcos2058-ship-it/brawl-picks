"""Mostra a estrutura das páginas do Brawl Planet pra ajustar o leitor de mapas."""
import re
import urllib.request


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 brawl-picks-vigia/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


for url in ["https://www.brawlplanet.com/pt-br/powerleague",
            "https://www.brawlplanet.com/pt-br/maps/hardrockmine_gemgrab"]:
    h = baixar(url)
    print("=" * 80, "\n", url, "tamanho", len(h))
    print("NEXT_DATA:", "__NEXT_DATA__" in h, "| self.__next_f:", "self.__next_f" in h)
    for palavra in ["rquivad", "Todos os ranques", "Ranqueada", "Mina rochosa", "Bolt", "58.8", "58,8"]:
        idx = [m.start() for m in re.finditer(re.escape(palavra), h)][:6]
        print(f"  {palavra!r}: {len(idx)} ocorrências {idx}")
    links = re.findall(r'href="(/pt-br/maps/[^"]+)"', h)
    print("  links de mapa:", len(links), links[:5])
    for palavra in ["rquivad", "Todos os ranques", "58.8"]:
        i = h.find(palavra)
        if i >= 0:
            print(f"--- contexto de {palavra!r} ---")
            print(h[max(0, i - 700): i + 900].replace("\n", " "))
