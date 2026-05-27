# Agent1

Assistant général autonome propulsé par Claude Opus 4.7, avec outils fichier / shell / web search, thinking adaptatif et prompt caching.

## Caractéristiques

- **Modèle** Claude Opus 4.7 (adaptive thinking + effort tunable)
- **Outils intégrés** lecture/écriture/listing de fichiers, exécution bash sandboxée, recherche web côté serveur
- **Tool runner** boucle agentique gérée par le SDK, exécution multi-tour automatique
- **Prompt caching** sur le system prompt pour réduire les coûts à chaque tour
- **Conversation persistante** sauvegarde/restauration via commandes slash
- **CLI riche** rendu Markdown, prompt couleur, affichage des appels d'outils

## Installation

```bash
git clone <repo>
cd agent1
cp .env.example .env          # mets ta clé Anthropic dedans
./run.sh
```

`run.sh` crée un venv, installe les dépendances et lance l'agent. Première run = quelques secondes pour `pip install`.

## Configuration (.env)

| Variable | Défaut | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | **Obligatoire.** Clé API Anthropic. |
| `AGENT_MODEL` | `claude-opus-4-7` | ID du modèle Claude. |
| `AGENT_EFFORT` | `high` | `low` \| `medium` \| `high` \| `xhigh` \| `max` |
| `AGENT_MAX_TOKENS` | `32000` | Budget de sortie par tour. |
| `AGENT_WORKSPACE` | `./workspace` | Dossier sandbox où les outils opèrent. |

## Commandes interactives

| Commande | Action |
|---|---|
| `/help` | Liste les commandes |
| `/clear` | Réinitialise l'historique de conversation |
| `/save [nom]` | Sauvegarde la conversation (nom auto si omis) |
| `/load <nom>` | Recharge une conversation sauvée |
| `/quit` ou `/exit` | Quitte |

## Architecture

```
agent/
├── config.py    # Chargement .env + sandbox workspace
├── tools.py     # 4 outils custom (read_file, write_file, list_dir, run_bash)
├── core.py      # Boucle agentique + sérialisation messages
├── ui.py        # Rendu rich (markdown, panels, prompts)
└── main.py      # CLI + dispatch slash commands
```

L'agent utilise le tool runner du SDK Anthropic (`client.beta.messages.tool_runner`) qui :

1. Envoie un message + définitions d'outils à Claude
2. Itère automatiquement : appel outil → résultat → appel outil → …
3. Termine quand `stop_reason == "end_turn"`

Le system prompt est marqué `cache_control: ephemeral` — à partir du 2ᵉ tour, il est lu depuis le cache (~0.1× coût input).

## Sandbox

Tous les outils fichier valident que le chemin reste sous `AGENT_WORKSPACE`. `run_bash` s'exécute avec `cwd=workspace` et timeout 60 s par défaut.

## Exemple d'usage

```
you ❯ crée un script Python qui calcule la suite de Fibonacci jusqu'à 100, sauvegarde-le, puis exécute-le
⚙  write_file(path='fib.py', content='def fib(n):...')
⚙  run_bash(command='python fib.py')

J'ai créé `fib.py` et exécuté le script. Voici la suite jusqu'à 100 :
0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89

you ❯ /save fibonacci_demo
ℹ  saved to /home/user/agent1/conversations/fibonacci_demo.json
```
