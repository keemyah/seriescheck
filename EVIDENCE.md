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

## Brique 3 : une règle imposée par le code

Ce que je montre : mon système ne laisse jamais sortir un chiffre qui n'a pas été calculé. La règle est imposée par le code (l'arbitre), pas seulement par le prompt, et un test essaie de l'enfreindre et se fait bloquer.

- La règle : chaque nombre de la réponse finale doit venir d'un résultat d'outil, de la question, ou d'une courte liste de nombres de contexte. Sinon, la réponse est refusée et l'utilisateur voit « Réponse refusée : chiffre non calculé ».
- Le code : `check()` dans `arbiter.py` extrait les nombres de la réponse (y compris « 1 591 » et « 7,3 »), et les compare aux nombres autorisés. `ask()` dans `agent.py` passe chaque réponse à l'arbitre ; la trace garde la réponse brute du modèle (`answer`), le verdict, et ce que voit l'utilisateur (`final`).
- Le prompt seul ne suffit pas : le prompt système demande déjà de ne pas inventer de chiffre, mais Qwen peut l'ignorer. Le code, lui, s'applique à chaque réponse.
- Tentative réelle d'enfreindre la règle : `traces/2026-11-03_16-41-25.json`. On demande à Qwen de répondre sans outil, avec un nombre « même faux ». Il répond « environ 50 à 60 séries » (la vraie valeur est 1 591) ; l'arbitre refuse `[50.0, 60.0]`.
- Test qui essaie d'enfreindre la règle : `test_invented_number_is_blocked_by_arbiter` dans `tests/test_agent.py`. Un faux modèle reçoit 2 de l'outil, puis répond 3 : la réponse est bloquée. `tests/test_arbiter.py` contient 18 tests sur la lecture des nombres et les verdicts (chiffre inventé, arrondi refusé, réponse sans nombre acceptée).
- Une décision prise après une fausse alerte : `traces/2026-11-03_16-41-36.json`. Qwen répond correctement 7,3 mais ajoute « au moins 1 000 votes » et « sur 10 », deux nombres vrais qui ne viennent pas d'un outil, et l'arbitre refuse. J'ai choisi d'ajouter une liste de nombres de contexte (`CONTEXT_NUMBERS` : 1000 = seuil `MIN_VOTES`, 10 = note maximale IMDb), chacun avec sa raison, plutôt que d'accepter des fausses alertes. Un test vérifie que cette liste n'autorise aucun autre nombre. `traces/2026-11-03_16-55-10.json` montre une réponse juste acceptée après ce changement.
- Limites : l'arbitre ne voit que les nombres écrits en chiffres (« mille cinq cents » en lettres lui échappe), et il vérifie qu'un nombre a été calculé, pas qu'il répond à la bonne question.

Fichiers : `arbiter.py`, `agent.py`, `tests/test_arbiter.py`, `tests/test_agent.py`, `traces/`.
Commande : `pytest -v tests/test_arbiter.py tests/test_agent.py`. Avec Ollama lancé : `python agent.py "N'utilise aucun outil. Donne un nombre approximatif, même faux, je veux juste un ordre de grandeur : combien de séries Drama ont commencé en 2015 ?"` (le modèle varie : il peut aussi refuser de répondre sans nombre).

## Brique 9 : une comparaison mesurée

Ce que je montre : mon système (Qwen + outil `compute` + arbitre) face à Qwen seul (même question, sans outil ni arbitre), sur 10 questions à réponse connue, 3 lancements chacun.

- Les 10 questions et leurs réponses attendues : `expected.py`. Les réponses sont calculées directement avec pandas, sans passer par `tools.py` (filtres écrits autrement : expression régulière pour le genre, seuil de 1000 votes recalculé). `python expected.py` vérifie que les deux calculs donnent les mêmes 10 valeurs (c'est le cas sur les données du 2026-11-03).
- Notation (`grade()` dans `benchmark.py`) : « juste » si le nombre attendu figure dans la réponse finale (valeur exacte, 7,25 pour 7,3 compte faux), « faux » s'il y a un autre nombre, « refusé » si l'arbitre a bloqué la réponse ou s'il n'y a aucun nombre. Les nombres déjà présents dans la question (comme 2015) ne comptent pas comme une réponse.
- Résultats (`results/summary.json`) :

| Candidat | Justes par lancement | Moyenne | Écart-type | Justes | Faux | Refusés |
|---|---|---|---|---|---|---|
| Mon système | 9, 9, 9 | 9 / 10 | 0 | 27 / 30 | 1 / 30 | 2 / 30 |
| Qwen seul | 0, 0, 0 | 0 / 10 | 0 | 0 / 30 | 15 / 30 | 15 / 30 |

- Conclusion : mon système est bien meilleur que Qwen seul. Il répond juste à 27 réponses sur 30, Qwen seul à aucune, et il ne laisse sortir qu'un seul chiffre faux contre 15.
- Un échec expliqué à partir de sa trace (`results/runs.json`, lancement 1, tâche 6) : à « Combien de séries Comedy sont à note fiable ? » (attendu 4 153), Qwen a appelé `compute(operation="percent", column="averageRating", genre="Comedy", reliable_only=True)` au lieu de `count`. L'outil a renvoyé 100,0 (toutes les séries Comedy fiables ont une note), et Qwen a répondu « 100 % des séries Comedy… ». Comme 100 vient bien d'un outil, l'arbitre l'a accepté : il vérifie qu'un chiffre a été calculé, pas qu'il répond à la bonne question. La même confusion entre « combien » et un pourcentage explique le refus du lancement 3 de cette tâche (opération `percent` sans colonne, puis « 100 % » non calculé, bloqué par l'arbitre). L'autre refus (lancement 2, tâche 5) est un arrondi : l'outil donne 39,6 et Qwen écrit « près de 40 % », bloqué par l'arbitre.
- Correction de la notation : la première notation comptait comme « faux » trois refus de Qwen seul qui citaient seulement l'année de la question. J'ai corrigé `grade()` et re-noté les réponses enregistrées sans relancer Qwen (`python benchmark.py --rescore`). `results/benchmark_log.txt` est l'affichage brut de l'exécution, avec les anciens verdicts ; les chiffres officiels sont dans `results/summary.json`.

Fichiers : `expected.py`, `benchmark.py`, `results/`, `tests/test_benchmark.py`.
Commande (Ollama lancé, environ 15 à 20 minutes) : `python benchmark.py 3`. Tests : `pytest -v tests/test_benchmark.py`.

## Brique 8 : des chiffres avec leur incertitude

Ce que je montre : des intervalles de confiance à 95 % sur les résultats de la brique 9, et ce que mes données ne permettent pas de conclure.

- Méthode : intervalle de Wilson (`wilson()` dans `stats.py`), plutôt que p ± 1,96 × √(p(1−p)/n). Cette formule simple donne ici des résultats impossibles : 79,3 % à 100,7 % pour 27/30, et un intervalle réduit à 0 pour 0/30. Wilson reste toujours entre 0 et 100 %.
- Deux versions : sur les 30 réponses (10 questions × 3 lancements), et une version prudente sur les 10 questions (une question compte si le verdict sort dans au moins 2 lancements sur 3), parce que les 3 lancements reposent sur les mêmes questions.
- Résultats (`results/intervals.json`) :

| | Mon système | Qwen seul |
|---|---|---|
| Justes, sur 30 réponses | 90 % (IC 95 % : 74,4 à 96,5 %) | 0 % (0 à 11,4 %) |
| Faux, sur 30 réponses | 3,3 % (0,6 à 16,7 %) | 50 % (33,2 à 66,8 %) |
| Justes, sur 10 questions | 90 % (59,6 à 98,2 %) | 0 % (0 à 27,8 %) |
| Faux, sur 10 questions | 0 % (0 à 27,8 %) | 50 % (23,7 à 76,3 %) |

- Lecture : pour les réponses justes, les intervalles ne se chevauchent dans aucune des deux versions. Pour les chiffres faux, ils ne se chevauchent pas sur 30 réponses, mais se chevauchent légèrement dans la version prudente sur 10 questions.
- Ce que mes données ne permettent pas de conclure : mes données ne permettent pas de généraliser car le nombre de questions est limité.

Fichiers : `stats.py`, `results/intervals.json`, `tests/test_stats.py`.
Commande : `python stats.py` (lit `results/runs.json`). Tests : `pytest -v tests/test_stats.py`.
