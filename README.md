# Brawl Picks

Ajudante de draft da ranked de Brawl Stars. Você escolhe o mapa, quem tem o
first pick e sua posição no time, marca os picks que já saíram e o site mostra
seus 5 melhores picks, com o motivo de cada um.

## O que tem

- **Draft:** sugestões pelo mapa, pelo modo e pelo ranked geral, com counter
  por classe e sugestão pros amigos.
- **Meta:** tiers sem os nerfados, nerfs e buffs do último balanceamento,
  Buffies e o top 3 de cada mapa do ranked.
- **Upar:** em quais brawlers vale gastar recurso.
- **Dicas:** como funciona a ranked e o que cada modo pede.
- **Conta:** seus brawlers no nível 11 e seus Buffies, salvos no navegador.

Os números vêm do [Brawl Time Ninja](https://brawltime.ninja/tier-list/ranked)
e do [Brawl Planet](https://www.brawlplanet.com/tier-list), e as mudanças das
[notas oficiais da Supercell](https://supercell.com/en/games/brawlstars/blog/).

## Publicar

O site é um arquivo só: `index.html`. Pra colocar no ar:

- **GitHub Pages:** Settings → Pages → Deploy from a branch → `main` / root.
- **Netlify:** importar o repositório, sem comando de build.

## Vigia

`bot/vigia.py` roda todo dia pelo GitHub Actions e abre uma issue quando sai
post novo no blog do Brawl Stars (Brawl Talk, notas de atualização,
balanceamento). Pra rodar na hora: aba **Actions** → **Vigia do Brawl Stars** →
**Run workflow**. Na primeira vez ele só registra os posts que já existem.

Este site não é afiliado à Supercell. Conteúdo de fã, seguindo a
[Fan Content Policy](https://supercell.com/en/fan-content-policy/).
