Les bases du projet final
1. L’idée générale
On te demande de construire un petit système d’IA autour d’un modèle de langage (LLM) auquel on ne peut pas faire confiance d’emblée. Un LLM peut inventer un chiffre, se tromper de calcul ou faire une action dangereuse. Ton travail n’est donc pas « utiliser un LLM », c’est d’entourer le LLM de code, de vérifications et de mesures pour que ses réponses deviennent fiables.
Exemple : un LLM qui répond « il y a eu 12 345 trajets de vélo hier ». Un système fiable l’oblige à calculer ce chiffre avec du code, refuse tout chiffre non calculé, et mesure combien de fois il se trompe.
Le sujet est libre. Ce qui est imposé, c’est la structure.
2. Le vocabulaire de base
Terme	Sens simple
LLM	Modèle de langage (ici Qwen) : il reçoit du texte, il produit du texte.
Agent	Un LLM dans une boucle : il réfléchit, appelle un outil, lit le résultat, recommence.
Harness	Le « cadre » autour du modèle : la boucle, les outils, les règles, les logs.
Outil (tool)	Une fonction que tu écris (ex. run_python) et que le modèle peut demander d’appeler.
MCP	Un protocole standard pour exposer des outils via un serveur. Ton serveur MCP offre des outils à n’importe quel harness compatible.
Garde-fou	Une règle imposée par le code (pas par le prompt). Un prompt se contourne, du code non.
Contexte	Ce que le modèle « voit » à un instant donné, mesuré en tokens (≈ morceaux de mots).
Quantification (Q4_K_M)	Compression du modèle (poids en ~4 bits) pour qu’il tienne en ~3 Go au lieu de beaucoup plus, avec une petite perte de qualité.
GGUF	Le format de fichier du modèle utilisé par llama.cpp.
Benchmark	Un ensemble de tâches à réponse connue pour mesurer objectivement un système.
3. Le modèle et ton setup (la partie à vérifier en premier)
Tout le monde utilise le même petit modèle, Qwen3.5-4B (Q4_K_M, ~3 Go), sur ton propre ordinateur. Cela rend les résultats reproductibles et comparables.
Tu as 3 façons de le faire tourner. Il suffit d’en choisir une.
Option A : llama.cpp
llama-server -m Qwen3.5-4B-Q4_K_M.gguf --port 8080 -c 16384 --jinja
-m : le fichier modèle
--port 8080 : le serveur écoute sur localhost:8080
-c 16384 : ta taille de contexte (16K tokens). Sans cela, il réserve 256K tokens de mémoire et ton RAM explose.
--jinja : utilise le bon format de conversation, nécessaire pour que le modèle appelle des outils correctement.
Option B : Ollama (plus simple à installer)
ollama pull qwen3.5:4b-q4_K_M
Pense à fixer num_ctx (équivalent de -c). Vérifie avec ollama list que le tag exact existe bien chez toi.
Option C : Cerebras (plan B uniquement)
Si ton ordinateur est trop faible : API gratuite, modèle qwen-3.8-27b, via https://api.cerebras.ai/v1.
Limites : 5 requêtes/minute et 1 million de tokens/jour. Ça compte surtout pour la brique 9 (beaucoup de lancements), donc il faudra planifier.
Tu dois le signaler dans ton README.
La clé va dans une variable d’environnement ($CEREBRAS_API_KEY), jamais dans le code ni le dépôt.
Checklist de prérequis
RAM : ~8 Go libres suffisent avec un contexte de 8K à 16K.
Disque : ~3 Go pour le modèle.
Python installé, plus git.
Un serveur de modèle qui répond. Test avec llama.cpp :
   curl http://localhost:8080/v1/models
Avec Ollama, ollama run qwen3.5:4b-q4_K_M puis écris « bonjour ». Avec Cerebras, un appel de test avec ta clé en variable d’environnement.
5. Un compte GitHub/Git pour le dépôt à rendre.
Ces serveurs exposent une API compatible OpenAI : ton code Python parlera au modèle de la même manière quelle que soit l’option choisie.
4. Les règles du jeu en une phrase
Ton projet doit : (1) tourner sur Qwen, (2) cocher 5 briques sur 9 de ton choix, (3) respecter 4 exigences R1 à R4. Projet individuel.
Pour la suite, voici la répartition des points :
10 points : tes 5 briques (2 points chacune)
3 points : R1 + R2 (ça tourne depuis le README, les tests passent)
2 points : R3 (journal d’usage de l’IA)
5 points : R4 (soutenance : tu dois expliquer le code)
Un point crucial : la soutenance pèse 5 points, et un code juste que tu ne sais pas expliquer ne rapporte rien. L’IA est autorisée, mais c’est toi qui dois comprendre chaque ligne.
5. Prochaines étapes
Une fois que tu as confirmé que le setup marche, je te propose de continuer dans cet ordre :
Les 4 exigences R1 à R4 (non négociables, donc à comprendre avant de coder)
Les 9 briques, une par une, avec ce que « prouver » veut dire pour chacune
Le choix de tes 5 briques et d’une idée de projet
Pour commencer, quelle machine as-tu (système d’exploitation et RAM), pour savoir si tu peux viser l’option A/B ou si tu dois prévoir Cerebras ?
Une précision d’abord
Aucune combinaison n’est imposée : le sujet demande 5 briques parmi 9, au choix. Les combinaisons 1-8-9 ou 1-7-9 que tu cites ne sont pas obligatoires. Ton instinct pour la brique 9 est bon, car c’est elle qui prouve que ton système fait mieux que le modèle seul.
Ma recommandation : briques 1, 3, 6, 8, 9
C’est l’idée « Analyste de données avec arbitre » du sujet, et c’est la plus simple des combinaisons, parce que le même jeu de données et les mêmes questions servent aux cinq briques. J’écarte volontairement la 7 (modèle appris), la 4 (seuils et matrices) et la 2 (MCP), qui ajoutent chacune un gros morceau à comprendre et à expliquer.
Le projet en une phrase
Un assistant qui répond à des questions chiffrées sur un jeu de données ouvert, et refuse tout chiffre qui n’a pas été calculé par du code.
Comment ça marche
L’utilisateur pose une question : « Quelle est la moyenne de X ? »
Le modèle demande d’appeler ton outil de calcul.
Ton code exécute le calcul sur les données nettoyées et renvoie le résultat.
Le modèle rédige sa réponse.
L’arbitre (du code) vérifie que chaque nombre de la réponse vient bien d’un résultat d’outil. Sinon, la réponse est refusée.
Ce que chaque brique devient
#	Brique	Dans ton projet	Preuve
1	Ton outil	Une fonction Python (par exemple calculer(colonne, opération)) que le modèle appelle	Trace d’un vrai appel et son résultat
3	Règle imposée par le code	L’arbitre : aucun chiffre non calculé ne sort	Un test qui force le modèle à inventer un chiffre et se fait bloquer
6	Données sales	Un jeu de données ouvert que tu nettoies avec un journal de nettoyage	Journal produit par le code, et une règle obtenue d’une personne ou de la notice du jeu de données (dis laquelle)
8	Incertitude	Intervalle de confiance sur le taux de réussite de chaque système	Les deux intervalles et la phrase sur ce que tes données ne permettent pas de conclure
9	Comparaison mesurée	10 questions ou plus à réponse connue, calculées par toi avec pandas ; ton système contre le modèle seul ; 3 lancements ou plus	Moyenne, dispersion, un échec expliqué par sa trace
Les briques 8 et 9 se nourrissent l’une l’autre : la 9 produit les résultats (par exemple 27 réussites sur 30), la 8 met un intervalle dessus. Tu n’as pas de seconde expérience à monter. Le même mécanisme de calcul d’intervalle sert d’ailleurs à expliquer les deux.
Les exigences R1 à R4 dans ce projet
R1 : README avec ollama pull, ollama create (ton Modelfile est déjà prêt), l’installation de Python, et une commande de lancement. Pas de clé nécessaire en local.
R2 : tests pytest sur ton code : le nettoyage, l’outil de calcul, l’arbitre (par exemple « une réponse avec le chiffre 42 non calculé est refusée »).
R3 : tu gardes l’export de tes conversations (celle-ci comprise) dans ai_log/, avec une note par séance.
R4 : le code à expliquer sera surtout l’outil, l’arbitre et la boucle, trois morceaux courts et logiques.
Pourquoi c’est le plus simple à défendre
Un seul fil conducteur, une phrase pour le résumer.
Pas d’apprentissage automatique ni de protocole à maîtriser.
Le côté « fiabilité » du sujet y est central : c’est exactement ce que le cours demande.
Les deux risques à connaître
Brique 8 : refaire 3 fois les mêmes 10 questions ne donne pas 30 observations indépendantes. Ta phrase sur les limites devra le dire, et c’est un bon point à montrer à la soutenance.
Qwen 4B appelle parfois mal les outils. Ces ratés alimenteront ton « échec expliqué » de la brique 9, ce qui nous arrange plutôt.
Ce qu’il me faut pour avancer
Il te reste à choisir le thème des données : un domaine que tu connais ou qui t’intéresse (sport, transports, musique, santé, cuisine, etc.). Plus tu connais le domaine, plus il sera facile de trouver la règle que le fichier ne dit pas (brique 6) et d’écrire des questions dont tu connais la réponse. Le jeu doit être ouvert (par exemple sur data.gouv.fr), de taille raisonnable (quelques milliers de lignes) et imparfait, avec des valeurs manquantes ou bizarres, c’est un avantage pour la brique 6.
Quel thème te parle ? Si tu hésites, donne-moi deux ou trois domaines et on les compare. Ensuite, on découpera le travail en étapes courtes.
j'aime bien la musique, la patisserie et les series mais je suis ouverte a tout domaine avec un bon jeu de donné sans infos personnelles
Ma recherche sur data.gouv.fr n’a rien donné de convaincant côté pâtisserie : j’ai trouvé des listes de lieux (cantines, boulangeries locales), mais pas de données chiffrées exploitables. Pour la musique et les séries, je n’ai pas encore vérifié de source précise. Voici donc deux pistes issues de ma connaissance générale, que nous vérifierons ensemble avant de t’engager.
Piste recommandée : les séries (jeux de données publics d’IMDb)
IMDb publie des fichiers téléchargeables gratuitement : liste des titres (type, année, genres, durée) et notes avec nombre de votes. Il n’y a pas de clé d’API, pas de compte nécessaire, et aucune donnée personnelle (ce sont des œuvres, pas des gens).
Pourquoi c’est bien adapté à ton projet :
Besoin	Ce que ça donne
Questions à réponse connue (brique 9)	« Combien de séries sorties en 2015 ? », « Note moyenne des séries Drama ? », « Genre le plus fréquent ? » : tu les calcules toi-même avec pandas
Données sales (brique 6)	Valeurs manquantes écrites \N, genres collés dans une seule cellule (Drama,Crime), années absentes, séries sans votes
Incertitude (brique 8)	Une note moyenne calculée sur peu de séries mérite un intervalle de confiance
Règle absente du fichier	Une note basée sur 5 votes n’est pas fiable, donc il faut un seuil minimum de votes. Tu la tires de la documentation du jeu de données ou d’une personne qui connaît bien les séries : tu cites ta source
Piste alternative : la pâtisserie (Open Food Facts)
C’est une base collaborative de produits alimentaires (biscuits, gâteaux, viennoiseries), avec sucre, graisses, et un score nutritionnel. Elle est très « sale » parce que saisie par des bénévoles : unités mélangées, libellés incohérents, valeurs aberrantes. C’est excellent pour la brique 6, mais la base est énorme, plus lourde à filtrer, et les questions sont moins évidentes à formuler.
Ma recommandation
Séries, pour trois raisons : le jeu est simple à comprendre (un titre, une année, un genre, une note), tu peux vérifier toi-même une réponse par du simple filtrage, et tu as de l’intérêt pour le sujet, ce qui aide à la soutenance.
Ce qu’il reste à vérifier avant de décider
Que les fichiers sont toujours disponibles avec les mêmes colonnes et que les conditions d’utilisation autorisent un usage de cours. De mémoire, c’est un usage non commercial, mais je veux le confirmer sur la page officielle.
Leur taille : ils sont gros, donc ton script devra les télécharger puis filtrer sur les séries uniquement. Tu mettras le script dans le dépôt, pas les données (c’est autorisé par le sujet).
Question : tu veux qu’on parte sur les séries ? Si oui, ma prochaine étape est d’ouvrir la page officielle des jeux de données pour confirmer ces deux points, puis de découper le travail en petites étapes. Si tu préfères la pâtisserie ou la musique, dis-le-moi et je cherche pareil.
oui partons sur les series
Vérifié : les deux fichiers dont on a besoin existent et sont utilisables dans ton cadre.
Ce que la page officielle confirme
Ces jeux de données sont destinés à un usage personnel et non commercial, et tu as le droit d’en garder des copies locales. Un projet de cours rentre dans ce cadre, mais tu ne dois pas republier les fichiers. 
imdb
Les fichiers se téléchargent depuis datasets.imdbws.com et sont rafraîchis chaque jour. Tes chiffres changeront donc légèrement d’un jour à l’autre, ce qui compte pour tes « réponses connues » : on fixera la date de téléchargement. 
imdb
La valeur \N désigne un champ manquant. C’est ta première donnée « sale ». 
imdb
Le champ genres peut contenir jusqu’à trois genres, et endYear n’est rempli que pour les séries. 
imdb
Le fichier de notes donne la note moyenne et le nombre de votes de chaque titre. 
github
Décisions pour rester simple et propre
On n’utilise que deux fichiers : title.basics (titres, années, genres) et title.ratings (notes, votes). On écarte name.basics, qui contient des informations sur des personnes réelles : ça évite tout souci de données personnelles (R1).
Les données vont dans un dossier data/ ignoré par Git. Le dépôt contiendra le script de téléchargement, ce que le sujet autorise.
Plan du projet en étapes courtes
Étape	Contenu	Brique
1	Environnement Python, téléchargement, premier coup d’œil	(base)
2	Nettoyage avec journal	6
3	L’outil de calcul appelé par le modèle	1
4	L’arbitre qui refuse les chiffres non calculés	3
5	Les 10 questions, les lancements, les intervalles	9 et 8
6	README, tests, journal d’IA (tout au long)	R1, R2, R3
Étape 1 : à faire maintenant
Dans ton terminal :
cd /Users/keemyah/Documents/CodingForAI/final
python3 -m venv .venv
source .venv/bin/activate
pip install pandas
mkdir -p data
printf ".venv/\ndata/\n" > .gitignore
curl -o data/title.basics.tsv.gz https://datasets.imdbws.com/title.basics.tsv.gz
curl -o data/title.ratings.tsv.gz https://datasets.imdbws.com/title.ratings.tsv.gz
ls -lh data
Ce que font ces commandes :
python3 -m venv .venv crée un environnement isolé pour que les bibliothèques de ce projet n’interfèrent pas avec le reste du Mac. source .venv/bin/activate l’active (ton prompt affichera (.venv)).
pip install pandas installe la bibliothèque de tableaux de données.
Le fichier .gitignore dit à Git de ne jamais enregistrer l’environnement ni les données.
curl télécharge les deux fichiers. Le premier est volumineux, donc l’attente peut durer un peu.
Si python3 n’existe pas ou si une commande échoue, copie-moi l’erreur. Une fois le téléchargement fini, dis-moi les tailles affichées par ls -lh data, et on regardera le contenu ensemble.

