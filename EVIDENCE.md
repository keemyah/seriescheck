# Preuves par brique

Données téléchargées le 2026-11-03 (les fichiers IMDb sont mis à jour chaque jour).

## Brique 6 : données sales, décisions écrites

Ce que je montre : un nettoyage de 307 637 séries IMDb, avec un journal produit par le code, et une règle absente du fichier.

- Journal de nettoyage : `cleaning_journal.json` (3 169 séries adultes retirées, 287 séries à année future retirées, 425 238 valeurs `\N` converties en manquant, 829 durées aberrantes remplacées par manquant).
- Effet mesuré : sur les mêmes lignes, la durée moyenne passe de 87,9 à 41,7 minutes, la médiane reste à 30,0.
- Règle que le fichier ne dit pas : un `endYear` manquant signifie « en cours » **ou** « non mis à jour ». Source : IMDb Help Center, « How do I change the end year of a series? » (https://help.imdb.com/article/contribution/titles/how-do-i-change-the-end-year-of-a-series/GGLM3TRYVJWDAQNG). 183 632 séries sont marquées « en cours ou non mise à jour ».
- Décision personnelle (pas une règle externe) : seuil de 1 000 votes pour une note jugée fiable (`MIN_VOTES` dans `clean.py`), soit 10 382 séries.

Fichiers : `clean.py`, `explore.py`, `cleaning_journal.json`.
Commande : `bash download_data.sh && python explore.py && python clean.py`

## Brique 1 : votre propre outil

Ce que je montre : une fonction que j'ai écrite, `compute`, que Qwen appelle dans une boucle que j'ai écrite, avec la trace d'un vrai appel et son résultat.

- L'outil : `compute(df, operation, column, year, genre, reliable_only)` dans `tools.py`. Il ne fait que 4 opérations (`count`, `median`, `max`, `percent`) sur 5 colonnes permises (liste blanche). Le modèle choisit les paramètres, le code fait le calcul.
- La boucle : `ask()` dans `agent.py`. Qwen reçoit la question et la description de l'outil ; s'il demande un appel, le code l'exécute et lui renvoie le résultat ; on s'arrête à sa réponse en texte, ou après 5 tours au maximum.
- La trace d'un vrai appel : `traces/2026-11-03_15-55-50.json`. À la question « Combien de séries Drama ont commencé en 2015 ? », Qwen a appelé `compute(operation="count", genre="Drama", year=2015)`, l'outil a renvoyé 1 591, et Qwen a répondu « Il y a eu 1591 séries de genre Drama qui ont commencé en 2015. » (15,4 s, modèle `qwen35-4b-8k`, raisonnement désactivé).
- Contrôle : 1 591 est aussi le chiffre obtenu en appelant `compute` directement, sans le modèle.
- Tests : `tests/test_tools.py` (13 tests de l'outil sur 8 séries écrites à la main) et `tests/test_agent.py` (7 tests de la boucle avec un faux modèle : exécution de l'outil, résultat renvoyé au modèle, arrêt après le nombre maximum de tours, outil ou paramètre inconnu refusé).

Fichiers : `tools.py`, `agent.py`, `traces/`, `tests/`.
Commande (Ollama lancé) : `python agent.py "Combien de séries Drama ont commencé en 2015 ?"` crée une nouvelle trace dans `traces/`. Tests : `pytest -v`.

## Brique 3 : à venir
## Brique 8 : à venir
## Brique 9 : à venir
