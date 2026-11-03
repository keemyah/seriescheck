# Séance du 2026-11-03 (1) : setup, données et nettoyage

Outil d'IA : Claude (claude.ai), conversation exportée dans conversation.md.

Objectif : installer Qwen en local et fixer le contexte, choisir le thème et les données, nettoyer les données, mettre en place Git, le README et EVIDENCE.md.

## Gardé tel quel
- Le Modelfile (2 lignes).
- Les fichiers écrits par l'IA : explore.py, profile_data.py, extremes.py, clean.py, download_data.sh, README.md et EVIDENCE.md. Je les ai gardés pour l'instant sans changement (sauf ce qui est indiqué plus bas). J'ai compris leur but et leur fonctionnement. Je dois encore relire chaque ligne en détail avant la soutenance.
- README.md et EVIDENCE.md n'ont pas été modifiés pour l'instant.

## Corrigé à la main
- Dans clean.py : j'ai fixé le nombre minimum de votes à 1000 (MIN_VOTES). C'est un choix personnel, basé sur un tableau comparatif du nombre de séries restantes selon le seuil.

## Pseudo-code ou prompt réécrit
- Rien pour l'instant.

## Décisions prises par moi
- Thème : les séries TV. C'est un sujet qui m'intéresse, la base de données est facile d'accès et elle ne contient aucune information personnelle.
- Briques : j'ai choisi des briques cohérentes entre elles, qui créent une continuité tout au long du projet.
- Contenus adultes retirés : ils ne sont pas appropriés pour ce sujet.
- Séries à année de début future retirées : elles n'ont aucune autre information, donc elles ne sont pas utiles.
- Seuil de 1000 votes : voir plus haut.
- Seuil de 300 minutes pour les durées : proposé par l'IA, que j'ai gardé. Je le juge assez long pour couvrir un épisode réaliste mais particulièrement long. Les durées au-dessus sont considérées comme aberrantes et remplacées par une valeur manquante (829 durées concernées) : la série elle-même est conservée.

## Sources
- Sens d'un endYear manquant : page d'aide officielle d'IMDb, "How do I change the end year of a series?".


# Séance du 2026-11-03 (2) : outil de calcul, boucle avec Qwen, arbitre

Outil d'IA : Claude Code (application desktop), session exportée dans conversation_claude_code.md.

Objectif : tester l'outil de calcul, écrire la boucle où Qwen appelle l'outil (brique 1), écrire l'arbitre qui refuse les chiffres non calculés (brique 3), remplir EVIDENCE.md pour ces deux briques.

## Gardé tel quel
- Les fichiers écrits par l'IA : tools.py, tests/test_tools.py, agent.py (y compris son prompt système), tests/test_agent.py, arbiter.py, tests/test_arbiter.py, les sections Brique 1 et Brique 3 d'EVIDENCE.md, les ajouts au README (étapes 5 et 6), les lignes ajoutées à .gitignore et requirements.txt (pytest, requests).
- L'IA a aussi supprimé trois fichiers vides créés par erreur (conftest.pypip, install, pytest) et deux traces en double ou inutiles.
- J'ai lu agent.py et arbiter.py. Dans agent.py, le dernier bloc (`if __name__ == "__main__":`) n'est pas encore clair pour moi : à revoir avant la soutenance.

## Corrigé à la main
- Rien.

## Pseudo-code ou prompt réécrit
- Rien.

## Décisions prises par moi
- J'ai demandé une explication avant chaque étape, puis validé chaque étape et chaque commit.
- Règles de l'arbitre, proposées par l'IA et validées par moi : un arrondi est refusé (seul le nombre exact est accepté), pas de seconde chance donnée au modèle après un refus, une réponse sans nombre est acceptée.
- Liste de constantes dans l'arbitre (1000 et 10) : l'IA m'a proposé deux options après une fausse alerte (une réponse juste refusée à cause de « 1 000 votes » et « sur 10 »). J'ai choisi la liste de constantes plutôt que de garder l'arbitre strict, parce que ça évite des erreurs.

## Sources
- Aucune nouvelle source externe.


# Séance des 2026-11-03 et 2026-11-04 (3) : benchmark et intervalles de confiance

Outil d'IA : Claude Code (application desktop), même session, exportée dans conversation_claude_code.md.

Objectif : comparer mon système à Qwen seul (brique 9), calculer des intervalles de confiance sur les résultats (brique 8), remplir EVIDENCE.md pour ces deux briques.

## Gardé tel quel
- Les fichiers écrits par l'IA : expected.py, benchmark.py, stats.py, tests/test_benchmark.py, tests/test_stats.py, le paramètre `tools` ajouté à `call_ollama` dans agent.py, les sections Brique 8 et Brique 9 d'EVIDENCE.md, l'étape 7 du README.
- J'ai lu expected.py, benchmark.py et stats.py.

## Corrigé à la main
- Rien.

## Pseudo-code ou prompt réécrit
- Rien. Le prompt de Qwen seul (« Réponds à la question par un nombre, en une phrase. ») a été proposé par l'IA et validé par moi.

## Correction après le benchmark
- Après le premier lancement, l'IA a remarqué que la notation comptait comme « faux » trois refus de Qwen seul qui citaient seulement l'année de la question (par exemple 2015). J'ai validé la correction : les nombres de la question ne comptent plus comme une réponse. Les réponses enregistrées ont été re-notées sans relancer Qwen. Les scores « justes » n'ont pas changé ; Qwen seul passe de 18 faux / 12 refusés à 15 / 15.

## Décisions prises par moi
- J'ai validé la conception du benchmark : les 10 questions, les deux candidats, 3 lancements, des réponses attendues calculées sans passer par l'outil, et une notation stricte (7,25 pour 7,3 compte faux).
- Brique 8 : j'ai choisi l'intervalle de Wilson plutôt que la formule simple (qui dépasse 100 % ou donne un intervalle nul sur mes résultats), et de montrer aussi une version prudente sur les 10 questions.
- Mes phrases dans EVIDENCE.md :
  - conclusion : mon système est bien meilleur que Qwen seul, comme le montrent les résultats des briques 8 et 9 ;
  - limite : mes données ne permettent pas de généraliser car le nombre de questions est limité.

## Sources
- Aucune nouvelle source externe.
