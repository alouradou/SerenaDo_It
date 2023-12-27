from src.data_manager import DataManager
from src.calendar_manager import CalendarManager
from src.app import MainApp


def main():
    # Chemin vers le fichier de données (dans l'url google sheets)
    sheet_id = ***REMOVED***

    data_manager = DataManager(sheet_id, sheet_name=***REMOVED***)

    df = data_manager.excel_to_dataframe(***REMOVED***)

    print(df)


if __name__ == "__main__":
    main()
