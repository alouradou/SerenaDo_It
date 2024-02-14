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

### Déploiement sur serveur

## Méthode recommandée

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

## Méthode déconseillée (ancienne)

```bash
screen -ls
kill -9 <pid>
screen -dm -S serenadoit python main.py
```

En particulier, sur les serveurs qui redirigent vers des répertoires statiques, ne pas oublier :
```bash
cp -r ./static ~/node/
```
