"""Vigia do blog do Brawl Stars.

Roda no GitHub Actions uma vez por dia. Lê a página de notícias do Brawl Stars
no site da Supercell, guarda os posts já vistos em data/vistos.json e abre uma
issue no repositório pra cada post novo (Brawl Talk, notas de atualização,
balanceamento etc.).

Na primeira vez só registra o que já existe, pra não abrir dezenas de issues.
"""
import json
import os
import re
import sys
import urllib.request

BLOG = "https://supercell.com/en/games/brawlstars/blog/"
VISTOS = os.path.join(os.path.dirname(__file__), "..", "data", "vistos.json")

TIPOS = [
    ("brawl-talk", "Brawl Talk"),
    ("release-notes", "Notas de atualização"),
    ("balance", "Balanceamento"),
    ("ranked", "Ranked"),
    ("buffie", "Buffies"),
]


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "brawl-picks-vigia/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def posts(html):
    achados = []
    for caminho in re.findall(r'href="(/en/games/brawlstars/blog/[a-z0-9\-]+/[a-z0-9\-]+/?)"', html):
        url = "https://supercell.com" + caminho.rstrip("/") + "/"
        if url not in achados:
            achados.append(url)
    return achados


def tipo(url):
    for chave, nome in TIPOS:
        if chave in url:
            return nome
    return "Notícia"


def titulo(url):
    slug = url.rstrip("/").split("/")[-1]
    return slug.replace("-", " ").strip().capitalize()


def abrir_issue(url):
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    t = tipo(url)
    corpo = {
        "title": f"[{t}] {titulo(url)}",
        "body": (
            f"Saiu um post novo no blog do Brawl Stars:\n\n{url}\n\n"
            "Se mudar brawler, mapa, Buffie ou regra da ranked, peça pro Claude "
            "atualizar os dados do Draft Ranked (`index.html`)."
        ),
    }
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues",
        data=json.dumps(corpo).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        print("Issue aberta:", json.load(r).get("html_url"))


def main():
    html = baixar(BLOG)
    atuais = posts(html)
    if not atuais:
        print("Não achei posts na página. O layout do site pode ter mudado.")
        sys.exit(1)

    primeira_vez = not os.path.exists(VISTOS)
    vistos = [] if primeira_vez else json.load(open(VISTOS))
    novos = [u for u in atuais if u not in vistos]

    if primeira_vez:
        print(f"Primeira execução: registrei {len(atuais)} posts sem abrir issue.")
    else:
        for url in novos:
            abrir_issue(url)
        print(f"{len(novos)} post(s) novo(s).")

    os.makedirs(os.path.dirname(VISTOS), exist_ok=True)
    with open(VISTOS, "w") as f:
        json.dump(sorted(set(vistos + atuais)), f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
