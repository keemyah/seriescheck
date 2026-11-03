# Séance du 2026-10-03 : setup

Objectif : installer Qwen en local et fixer le contexte.

- Gardé tel quel : le Modelfile (2 lignes)
- Corrigé à la main : Rien
- Pseudo-code ou prompt réécrit : Rien

cat > ai_log/2026-11-03_setup/note.md << 'EOF'
# Séance du 2026-11-03 : setup, données et nettoyage

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
EOF
