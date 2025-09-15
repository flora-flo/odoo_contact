import os
import time
import pandas as pd
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from dotenv import load_dotenv

load_dotenv()


class TestMultipleContactsCreation(unittest.TestCase):
    """Test de création multiple de contacts depuis Excel"""

    def setUp(self):
        # Configuration Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")

        # Initialisation du driver
        self.service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=options)
        self.wait = WebDriverWait(self.driver, 15)

        # Charger les données Excel
        self.contacts_data = self.load_contacts_from_excel("Contact.xlsx")

    def load_contacts_from_excel(self, file_path=None):
        """Charger les contacts depuis un fichier Excel"""
        try:
            # Obtenir le chemin absolu du script actuel
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Chemin absolu vers le fichier Excel
            if file_path is None:
                file_path = os.path.join(current_dir, 'Contact.xlsx')

            print(f"Recherche du fichier à: {file_path}")

            # Vérifier si le fichier existe
            if not os.path.exists(file_path):
                print(f"ERREUR: Fichier non trouvé à l'emplacement: {file_path}")

                # Lister les fichiers dans le dossier tests pour debug
                print(f"Fichiers dans le dossier tests: {os.listdir(current_dir)}")

                # Chercher tous les fichiers Excel
                excel_files = [f for f in os.listdir(current_dir) if f.lower().endswith(('.xlsx', '.xls'))]
                if excel_files:
                    print(f"Fichiers Excel trouvés: {excel_files}")
                    # Utiliser le premier fichier Excel trouvé
                    file_path = os.path.join(current_dir, excel_files[0])
                    print(f"Utilisation du fichier: {file_path}")
                else:
                    print("Aucun fichier Excel trouvé. Création d'un exemple...")
                    return self.create_example_excel()

            # Lecture du fichier Excel
            df = pd.read_excel(file_path)
            print(f"Fichier Excel chargé: {len(df)} contacts trouvés")
            print(f"Colonnes disponibles: {list(df.columns)}")

            # Aperçu des données
            print("Aperçu des données:")
            print(df.head())

            return df.to_dict('records')

        except Exception as e:
            print(f"Erreur lecture Excel: {e}")
            import traceback
            traceback.print_exc()
            return []
    def login_to_odoo(self):
        """Connexion à Odoo"""
        try:
            self.driver.get(os.getenv("ODOO_URL") + "/web")

            login_field = self.wait.until(
                EC.element_to_be_clickable((By.ID, "login"))
            )
            login_field.send_keys(os.getenv("ODOO_EMAIL"))

            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(os.getenv("ODOO_PASSWORD") + Keys.RETURN)

            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".o_main_navbar"))
            )
            return True

        except Exception as e:
            print(f"Echec connexion: {e}")
            return False

    def access_contact_form(self):
        """Accéder au formulaire de création"""
        try:
            form_url = f"{os.getenv('ODOO_URL')}/web#cids=1&menu_id=96&action=122&model=res.partner&view_type=form"
            self.driver.get(form_url)

            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".o_form_view"))
            )
            return True

        except Exception as e:
            print(f"Echec accès formulaire: {e}")
            return False

    def fill_contact_form(self, contact_data):
        """Remplir le formulaire avec les données d'un contact"""
        try:
            # Mapping de tous les champs incluant le name
            fields_mapping = [
                ('name', [
                    "input[name='name']",
                    "input[placeholder='e.g. Brandon Freeman']",
                    "input[placeholder*='Brandon Freeman']",
                    "input[id='o_field_input_200']",
                    "input[id='o_field_input_281']",
                    "input.o_input[type='text']"
                ]),
                ('phone', ["input[name='phone']"]),
                ('email', ["input[name='email']"]),
                ('company', ["input[name='company']"]),
                ('street', ["input[name='street']"]),
                ('street2', ["input[name='street2']"]),
                ('city', ["input[name='city']"]),
                ('zip', ["input[name='zip']"]),
                ('mobile', ["input[name='mobile']"]),
                ('website', ["input[name='website']"])
            ]

            # Remplir chaque champ
            for field_name, selectors in fields_mapping:
                if field_name in contact_data and pd.notna(contact_data[field_name]):
                    value = str(contact_data[field_name])
                    field_filled = False

                    # Essayer chaque sélecteur pour ce champ
                    for selector in selectors:
                        try:
                            element = self.wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            element.clear()
                            element.send_keys(value)
                            print(f"✓ {field_name} rempli: {value}")
                            field_filled = True
                            time.sleep(0.2)
                            break
                        except Exception as e:
                            continue

                    if not field_filled:
                        print(f" {field_name} non trouvé avec les sélecteurs: {selectors}")

            return True

        except Exception as e:
            print(f"Erreur remplissage: {e}")
            return False
    def submit_contact_form(self):
        """Soumettre le formulaire"""
        try:
            save_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.o_form_button_save"))
            )
            save_button.click()

            # Attendre la création
            time.sleep(3)
            return True

        except Exception as e:
            print(f"Erreur soumission: {e}")
            return False

    def verify_contact_created(self, contact_name):
        """Vérifier qu'un contact a été créé"""
        try:
            # Vérifier l'URL (doit contenir un ID)
            if "id=" in self.driver.current_url:
                return True

            # Vérifier le titre
            if contact_name in self.driver.title:
                return True

            # Vérifier le mode lecture seule
            try:
                name_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='name']")
                if name_field.get_attribute("readonly"):
                    return True
            except:
                pass

            return False

        except Exception as e:
            print(f"Erreur vérification: {e}")
            return False

    def get_contacts_count(self):
        """Compter le nombre de contacts dans la base"""
        try:
            # Aller à la liste des contacts
            list_url = f"{os.getenv('ODOO_URL')}web#cids=1&menu_id=96&action=122&model=res.partner&view_type=kanban"
            self.driver.get(list_url)
            time.sleep(3)

            # Compter les éléments de contact
            contact_elements = self.driver.find_elements(By.CSS_SELECTOR, ".o_kanban_record")
            return len(contact_elements)

        except Exception as e:
            print(f"Erreur comptage contacts: {e}")
            return 0

    def create_single_contact(self, contact_data, index):
        """Créer un seul contact"""
        print(f"\nCréation du contact {index + 1}: {contact_data.get('name', 'Sans nom')}")

        if not self.access_contact_form():
            return False

        if not self.fill_contact_form(contact_data):
            return False

        if not self.submit_contact_form():
            return False

        if not self.verify_contact_created(contact_data.get('name', '')):
            print(f"Échec vérification contact {index + 1}")
            return False

        print(f"SUCCÈS: Contact {index + 1} créé")
        return True

    def test_multiple_contacts_creation(self):
        """Test de création multiple de contacts"""
        if not self.contacts_data:
            self.skipTest("Aucune donnée Excel chargée")

        if not self.login_to_odoo():
            self.fail("Échec de la connexion")

        # Nombre initial de contacts
        initial_count = self.get_contacts_count()
        print(f"Nombre initial de contacts: {initial_count}")

        # Créer chaque contact
        success_count = 0
        failed_contacts = []

        for i, contact_data in enumerate(self.contacts_data):
            success = self.create_single_contact(contact_data, i)
            if success:
                success_count += 1
            else:
                failed_contacts.append(contact_data.get('name', f'Contact {i + 1}'))

        # Vérification finale
        final_count = self.get_contacts_count()
        expected_count = initial_count + success_count

        print(f"\n" + "=" * 50)
        print("RÉCAPITULATIF DE CRÉATION")
        print("=" * 50)
        print(f"Contacts à créer: {len(self.contacts_data)}")
        print(f"Contacts créés avec succès: {success_count}")
        print(f"Contacts échoués: {len(failed_contacts)}")
        print(f"Contacts attendus en base: {expected_count}")
        print(f"Contacts actuels en base: {final_count}")

        if failed_contacts:
            print(f"Contacts échoués: {', '.join(failed_contacts)}")

        # Vérifications unitaires
        self.assertEqual(success_count, len(self.contacts_data) - len(failed_contacts),
                         "Incohérence dans le nombre de contacts créés")

        self.assertEqual(final_count, expected_count,
                         f"Incohérence dans la base: attendu {expected_count}, trouvé {final_count}")

        if success_count == len(self.contacts_data):
            print("SUCCÈS: Tous les contacts créés avec succès")
        else:
            self.fail(f"ÉCHEC: {len(failed_contacts)} contact(s) non créé(s)")

    def tearDown(self):
        self.driver.quit()


# if __name__ == "__main__":
#     unittest.main()
    if __name__ == "__main__":
        import xmlrunner

        unittest.main(testRunner=xmlrunner.XMLTestRunner(output='reports'))