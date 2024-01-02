import requests
import json


def get_file_names_from_github(url):
    # Ajoute l'en-tête User-Agent pour éviter les problèmes de blocage par le serveur GitHub
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    # Envoie la requête GET pour obtenir le contenu HTML de la page
    response = requests.get(url, headers=headers)

    # Vérifie si la requête a réussi (statut 200)
    if response.status_code == 200:
        json_data = json.loads(response.text)

        file_names_path = [{'name': item['name'],
                            'path': "https://raw.githubusercontent.com/FrancoisBrucker/do-it/main/" + item['path']}
                           for item in json_data['payload']['tree']['items']]

        return file_names_path
    else:
        # Affiche un message d'erreur si la requête échoue
        print(f"Erreur lors de la récupération du contenu (code {response.status_code}).")
        return []


def filter_file_names(file_info, extension):
    return [file for file in file_info if file['name'].endswith(extension)]


class GithubFilesManager:
    def __init__(self):
        self.github_url = "https://github.com/FrancoisBrucker/do-it/tree/main/src/promos/2023-2024/Dang-Vu-Duc/mon/temps-1.2"
        self.github_raw_url = "https://raw.githubusercontent.com/epfl-si/epfl-timetable/master"

    def get_github_files(self):
        github_files = get_file_names_from_github(self.github_url)
        github_files = filter_file_names(github_files, ".xlsx")

        return github_files
