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

## Brique 1 : à venir
## Brique 3 : à venir
## Brique 8 : à venir
## Brique 9 : à venir
