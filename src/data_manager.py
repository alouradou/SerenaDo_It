import pandas as pd


class DataManager:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)  # Chargez vos données depuis le fichier CSV

    def clean_data(self):
        # Implémentez vos logiques de nettoyage des données ici
        pass

    def get_event_data(self, row_index):
        # Retourne les données d'un événement à partir de l'index de la ligne
        return self.data.iloc[row_index]

# Exemple d'utilisation
# data_manager = DataManager('votre_fichier.csv')
# event_data = data_manager.get_event_data(0)
