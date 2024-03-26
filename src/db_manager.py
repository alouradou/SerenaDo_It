import sqlite3

courses_aliases = {
    "common": [
        "bonjour !", "tc1 : agilité", "lancement projet 3a", "tc1 : système d'information",
        "tc1 : gestion des sources", "tc1 : service design", "prez &pok", "do_it circus",
        "langues", "projet 3a", "vacances", "filière métier", "tronc commun 3a",
        "prez mon 2", "prez pok", "point pok sprint 1", "point pok sprint 2", "prez mon 1", "pok&mon",
        "cap 1a/3a/conception si", "prez projet", "rencontre w3g", "débrief", "conférence métier", "stage 3A",
        "CAP 1A/3A / Conception SI", "TC1 : Service Design (Démarrage à 8h45)", 'conf  "product manager"',
        "prez MON 1 (13h30-15h30)", "rentrée"
    ],
    "écosystème digital": ["écosystème digital", "eco-système digital", "Eco-système digital"],
    "numérique et travail": ["numérique et travail", "numérique & travail"],
    "low code": ["low code", "no/low code"],
    "OPS / Unix": ["OPS / Unix", "ops"],
    "UX design": ["UX design", "UX design et expression besoin"],
    "principe théorique de la gestion de projet": ["principe théorique de la gestion de projet",
                                                   "fondamentaux gestion de projet"],
    "Stratégie d'entreprise & SI": ["Stratégie d'entreprise & SI", "Stratégie & SI", "stratégje & si"],
    "Architecture et gouvernance du SI": ["Architecture et gouvernance du SI", "Architecture SI", "architecture si",
                                          "Architecture des SI"],
    "conception des SI": ["conception des SI", "conception SI"],
    "développement web from 0 to hero": ["développement web from 0 to hero", "web 0 to hero"],
    "java / gradle": ["java / gradle", "java/ gradle"],
    "bonnes pratiques": ["bonnes pratiques", "Structuration d'un projet Info", "Programmation par les tests"],
    "UI- parcours utilisateur": ["UI- parcours utilisateur", "User interface"],
    "Equipe performante": ["Equipe performante", "Equipe performante"],
    "lean engineering": ["lean engineering", "lean engineering"],
    "IT et dynamique des organisations / change management": ["IT et dynamique des organisations / change management",
                                                              "IT & dynamique organisationnelle"],
    "Monitoring": ["Monitoring", "Monitoring des SI"],
    "cybersécurité & management des risques": ["cybersécurité & management des risques", "Cybersécurité",
                                               "cybersécurité & management des risques", "cybersécu"],
    "AWS / docker": ["AWS / docker", "AWS, docker"],
    "réseaux": ["réseaux"],
    "structure de données": ["structure de données", "structures de données"],
    "Project management office GP avancée": ["Project management office GP avancée", "Gestion de projet avancé"],
    "UI avancée - théorie & testing": ["UI avancée - théorie & testing", "User interface avancé"],
    "analyse comportementale": ["analyse comportementale", "people analytics"]
}


def init_database(path='./serenadoit.db'):
    # Connexion à la base de données SQLite
    conn = sqlite3.connect(path)
    # Affihcer les tables
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND "
                   "(name='courses' OR name='unknown_courses' OR name='sheets')")
    table_exists = cursor.fetchone()

    # Si la table existe déjà, la supprimer
    if table_exists:
        try:
            cursor.execute("DROP TABLE courses")
            cursor.execute("DROP TABLE unknown_courses")
            cursor.execute("DROP TABLE sheets")
            conn.commit()
        except sqlite3.Error as e:
            print("Erreur lors de la suppression de la table :", e)

    # Création de la table pour stocker les correspondances
    try:
        cursor.execute('''CREATE TABLE courses (
                                id INTEGER PRIMARY KEY,
                                course_name TEXT,
                                alias TEXT
                            )''')
        cursor.execute('''CREATE TABLE unknown_courses (
                                id INTEGER PRIMARY KEY,
                                course_name TEXT UNIQUE,
                                additional_info TEXT
                            )''')
        cursor.execute('''CREATE TABLE sheets (
                                        id INTEGER PRIMARY KEY,
                                        sheet_id TEXT,
                                        sheet_name TEXT,
                                        student_sheet_id TEXT,
                                        student_sheet_name TEXT,
                                        date TEXT
                                    )''')
        conn.commit()
    except sqlite3.Error as e:
        print("Erreur lors de la création de la table :", e)

    # Insertion des données du dictionnaire dans la table
    for course_name, aliases in courses_aliases.items():
        for alias in aliases:
            cursor.execute("INSERT INTO courses (course_name, alias) VALUES (?, ?)", (course_name, alias))

    # Commit et fermeture de la connexion
    conn.commit()
    print("Database initialized.")
    conn.close()


# Fonction detect_matching modifiée
def detect_matching(cell, deleted_courses):
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()

    # Obtention de la liste des alias de cours supprimés
    deleted_aliases = [alias.lower() for key in deleted_courses for alias in courses_aliases.get(key, [])]

    if cell.value is None:
        conn.close()
        return False

    # Vérification si le nom de cours ou l'un de ses alias correspond à la liste des alias de cours supprimés
    course_name = cell.value.split('\n')[0].lower().strip()
    cursor.execute("SELECT COUNT(*) FROM courses WHERE course_name = ? OR alias = ?", (course_name, course_name))
    result = cursor.fetchone()[0]

    conn.close()
    return result > 0


if __name__ == "__main__":
    init_database()
