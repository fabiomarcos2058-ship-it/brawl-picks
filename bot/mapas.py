"""Atualiza os mapas da ranked.

Lê a página da ranked do Brawl Planet em português, pega só os mapas da
rotação atual (ignora "Mapas arquivados"), entra na página de cada mapa e
guarda os brawlers com maior taxa de vitória na ranqueada (Diamante 1 pra
cima). Salva tudo em data/mapas.json, que o site lê quando abre.

Roda todo dia. Se o pool de mapas mudar (fim de temporada), abre uma issue
dizendo quais mapas entraram e saíram.
"""
import datetime
import html as htmllib
import json
import os
import re
import sys
import time
import urllib.request

BASE = "https://www.brawlplanet.com"
RANKED = BASE + "/pt-br/powerleague"
SAIDA = os.path.join(os.path.dirname(__file__), "..", "data", "mapas.json")

MODOS = {"gemgrab": "gem", "brawlball": "ball", "hotzone": "zone",
         "heist": "heist", "bounty": "bounty", "knockout": "ko"}

# slug do Brawl Planet -> nome usado no site
NOMES = {"8-bit": "8-Bit", "el_primo": "El Primo", "jae-yong": "Jae-Yong",
         "larry_and_lawrie": "Larry & Lawrie", "mr._p": "Mr. P", "r-t": "R-T",
         "starr_nova": "Starr Nova"}

MIN_ESCOLHA = 1.0   # % de escolha mínima pra taxa de vitória ser confiável
TOP = 8             # quantos brawlers guardar por mapa


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 brawl-picks-vigia/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def nome_brawler(slug):
    return NOMES.get(slug) or " ".join(p.capitalize() for p in slug.split("_"))


def mapas_ativos():
    h = baixar(RANKED)
    fim = h.find(">Mapas arquivados<")
    if fim < 0:
        fim = len(h)
    vistos = []
    for slug in re.findall(r'href="/pt-br/maps/([^"]+)"', h[:fim]):
        if slug not in vistos:
            vistos.append(slug)
    return vistos


def ler_mapa(slug):
    h = baixar(f"{BASE}/pt-br/maps/{slug}")
    nome = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    nome = htmllib.unescape(re.sub(r"<[^>]+>", "", nome.group(1)).strip()) if nome else slug

    inicio = 0
    m = re.search(r'-ranked"\s+hidden', h)
    if m:
        inicio = m.start()
    linhas = []
    for corpo in re.findall(r"<tbody>(.*?)</tbody>", h[inicio:], re.S):
        achadas = re.findall(
            r'href="/pt-br/brawlers/([^"]+)".*?text-(?:emerald|red|zinc|amber|yellow|orange|rose|lime)-\d+">([\d.]+)</span>'
            r'.*?<span class="tabular-nums[^"]*">([\d.]+)</span>',
            corpo, re.S)
        if len(achadas) >= 40:
            linhas = achadas
            break
    tabela = [(nome_brawler(s), float(wr), float(esc)) for s, wr, esc in linhas]
    return nome, tabela


def abrir_issue(titulo, corpo):
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        print("(sem token, não abri issue)", titulo)
        return
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues",
        data=json.dumps({"title": titulo, "body": corpo}).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print("Issue aberta:", json.load(r).get("html_url"))


def main():
    slugs = mapas_ativos()
    print(f"{len(slugs)} mapas na rotação atual")
    if len(slugs) < 18:
        print("Poucos mapas encontrados. O site pode ter mudado; não vou sobrescrever nada.")
        sys.exit(1)

    mapas = []
    for slug in slugs:
        modo = MODOS.get(slug.rsplit("_", 1)[-1])
        if not modo:
            print("Modo desconhecido, pulei:", slug)
            continue
        try:
            nome, tabela = ler_mapa(slug)
        except Exception as e:
            print("Erro lendo", slug, e)
            tabela, nome = [], slug
        confiaveis = sorted([t for t in tabela if t[2] >= MIN_ESCOLHA], key=lambda t: -t[1])[:TOP]
        print(f"  {modo:6} {nome:28} {len(tabela):3} brawlers | " +
              ", ".join(f"{n} {wr}" for n, wr, _ in confiaveis[:3]))
        mapas.append({"slug": slug, "modo": modo, "nome": nome,
                      "top": [[n, wr, esc] for n, wr, esc in confiaveis]})
        time.sleep(1)

    com_dados = sum(1 for m in mapas if m["top"])
    if com_dados < len(mapas) * 0.6:
        print(f"Só {com_dados} de {len(mapas)} mapas com dados. Não vou sobrescrever.")
        sys.exit(1)

    anterior = []
    if os.path.exists(SAIDA):
        try:
            anterior = [m["slug"] for m in json.load(open(SAIDA)).get("mapas", [])]
        except Exception:
            anterior = []

    agora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    dados = {"fonte": "Brawl Planet, ranqueada Diamante 1 pra cima", "atualizado": agora, "mapas": mapas}
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)

    entraram = [m["nome"] for m in mapas if m["slug"] not in anterior]
    sairam = [s for s in anterior if s not in slugs]
    if anterior and (entraram or sairam):
        corpo = "O pool de mapas da ranked mudou e o `data/mapas.json` já foi atualizado.\n\n"
        if entraram:
            corpo += "**Entraram:** " + ", ".join(entraram) + "\n\n"
        if sairam:
            corpo += "**Saíram:** " + ", ".join(sairam) + "\n"
        abrir_issue("[Ranked] Mapas da temporada mudaram", corpo)
    print("Pronto:", agora)


if __name__ == "__main__":
    main()
