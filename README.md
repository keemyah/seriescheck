# SeriesCheck : un assistant qui ne donne que des chiffres calculés

Projet final de Coding for AI & Data Science. Un petit assistant répond à des questions chiffrées sur les séries TV (données ouvertes IMDb) et refuse tout chiffre qui n'a pas été calculé par du code.

État actuel : le modèle local, le nettoyage des données, l'outil de calcul, la boucle avec Qwen, l'arbitre, le benchmark et les intervalles de confiance fonctionnent.

## Prérequis

- Python 3.9 ou plus récent
- Ollama (https://ollama.com)
- Environ 8 Go de RAM et 4 Go de disque pour le modèle, plus environ 300 Mo pour les données

## Installation

1. Modèle Qwen3.5-4B (Q4_K_M) avec un contexte de 8192 tokens :

        ollama pull qwen3.5:4b-q4_K_M
        ollama create qwen35-4b-8k -f Modelfile

2. Environnement Python :

        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt

3. Données (jeux IMDb non commerciaux, téléchargés, non inclus dans le dépôt) :

        bash download_data.sh

4. Filtrage des séries puis nettoyage avec journal :

        python explore.py
        python clean.py

Résultat : `data/series_clean.csv` et `cleaning_journal.json`.

5. Tests (ils n'ont pas besoin du modèle ni des données) :

        pytest -v

6. Poser une question à l'assistant (Ollama doit être lancé) :

        python agent.py "Combien de séries Drama ont commencé en 2015 ?"

La réponse du modèle et la réponse finale s'affichent. Si la réponse contient un chiffre qui n'a pas été calculé par l'outil, l'arbitre la refuse. La trace de l'échange est écrite dans `traces/`.

7. Benchmark : le système face à Qwen seul, 10 questions, 3 lancements (Ollama lancé, environ 15 à 20 minutes), puis les intervalles de confiance :

        python benchmark.py 3
        python stats.py

Résultats : `results/summary.json` et `results/intervals.json`. Pour vérifier que les réponses attendues sont identiques à celles de l'outil : `python expected.py`.

## Données

Source : jeux de données publics d'IMDb (https://datasets.imdbws.com/), pour un usage personnel et non commercial. Les fichiers changent chaque jour : les chiffres peuvent varier légèrement.

## Autres dossiers

- `EVIDENCE.md` : une section par brique, avec la commande qui la reproduit
- `ai_log/` : journal d'usage de l'IA
