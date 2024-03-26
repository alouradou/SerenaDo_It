# SérénaDo_It

## Description

Ce projet a pour but d'importer les calendriers 3A sous forme de Google Spreadsheet ou Excel dans votre application de calendrier favorite.

## Installation

Nécessite Python 3.8 ou supérieur

### Mise en place du venv

Depuis le répertoire du projet :

```bash
python -m venv serenadoit .
source serenadoit/bin/activate
pip install -r requirements.txt
```

### Configuration

Mettre en place la base de données dans `./uploads/serenadoit.db`.

Depuis la racine du projet :
```bash
cd ./uploads
python ../src/db_manager.py
```

Cela doit créer un fichier `./uploads/serenadoit.db` avec les tables suivantes : 
- courses
- unknown_courses
- sheets

On peut changer le lieu de la db mais il faut s'assurer que le code le supporte.
Pour cela, exécuter le test associé après avoir exécuté `db_manager.py`.

## Déploiement sur serveur

### Méthode recommandée

Après avoir activé le venv : 

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:10410 run_prod:app --error-logfile logs/error.log --access-logfile logs/access.log -D
```
(-D pour detached)

Et vérifier que le serveur est bien en écoute sur le port 10410 et le processus lancé :
```bash
ps aux | grep gunicorn
netstat -tulnp | grep 10410
```

Pour arrêter le serveur :
```bash
ps aux | grep gunicorn
kill -9 <gunicorn_pid>
```


Redéployer sur le serveur nginx les fichiers statiques nécessaires (changements de styles, scripts, ajout d'images...) :
```bash
rm -r ~/node/static/styles ~/node/static/scripts ~/node/static/images
cp -r ./static ~/node/
```
### Méthode dépréciée

```bash
screen -ls
kill -9 <pid>
screen -dm -S serenadoit python main.py
```

En particulier, sur les serveurs qui redirigent vers des répertoires statiques, ne pas oublier :
```bash
cp -r ./static ~/node/
```
