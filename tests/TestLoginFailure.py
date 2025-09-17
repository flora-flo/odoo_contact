import unittest
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


class TestLoginFailure(unittest.TestCase):
    """Tests de login avec de fausses informations"""

    def setUp(self):
        # Configuration Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "https://healio-test.ddns.net/"  # Remplacez par votre URL
        self.test_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")


    def take_screenshot(self, name):
        """Prend un screenshot avec nom timestampé"""
        screenshot_name = f"screenshot_{self.test_start_time}_{name}.png"
        self.driver.save_screenshot(screenshot_name)
        print(f"Screenshot sauvegardé : {screenshot_name}")
    def test_login_with_wrong_password(self):
        """Test login avec mot de passe incorrect"""
        try:
            print("Test: Login avec mot de passe incorrect...")

            self.driver.get(f"{self.base_url}web/login")
            self.take_screenshot("login_page")
            # Remplir avec de fausses informations
            email_field = self.wait.until(
                EC.element_to_be_clickable((By.ID, "login"))
            )
            email_field.send_keys("flora@healio.tech")  # Email qui existe
            self.take_screenshot("email_existant")

            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys("faux_mot_de_passe_123")  # Mauvais mot de passe
            self.take_screenshot("Mauvais mot de passe")

            # Cliquer sur le bouton login
            login_button = self.driver.find_element(
                By.CSS_SELECTOR, "button[type='submit']"
            )
            login_button.click()

            # Vérifier que le message d'erreur apparaît
            error_message = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-danger"))
            )

            self.assertIsNotNone(error_message)
            print("✓ Message d'erreur détecté")
            self.assertIn("Wrong login/password", error_message.text)
            print("✓ Message d'erreur correct")
            self.take_screenshot("erreur correct")


        except TimeoutException:
            self.fail("Le message d'erreur ne s'est pas affiché")

    def test_login_with_wrong_email(self):
        """Test login avec email inexistant"""
        try:
            print("Test: Login avec email inexistant...")

            self.driver.get(f"{self.base_url}web/login")

            # Remplir avec email inexistant
            email_field = self.wait.until(
                EC.element_to_be_clickable((By.ID, "login"))
            )
            email_field.send_keys("email_inexistant_123@example.com")  # Email qui n'existe pas
            self.take_screenshot("email inexistant")

            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys("any_password_123")  # N'importe quel mot de passe
            self.take_screenshot("password")

            login_button = self.driver.find_element(
                By.CSS_SELECTOR, "button[type='submit']"
            )
            login_button.click()

            # Vérifier le message d'erreur
            error_message = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-danger"))
            )

            self.assertIsNotNone(error_message)
            print("✓ Message d'erreur détecté pour email inexistant")

        except TimeoutException:
            self.fail("Le message d'erreur ne s'est pas affiché pour email inexistant")

    def test_login_empty_fields(self):
        """Test login avec champs vides"""
        try:
            print("Test: Login avec champs vides...")

            self.driver.get(f"{self.base_url}web/login")

            # Ne rien remplir et cliquer directement
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            login_button.click()

            # Vérifier les messages de validation HTML5
            email_field = self.driver.find_element(By.ID, "login")
            password_field = self.driver.find_element(By.ID, "password")
            self.take_screenshot("aucune information")

            # Vérifier que les champs sont invalides
            self.assertEqual(email_field.get_attribute("required"), "true")
            self.assertEqual(password_field.get_attribute("required"), "true")
            print("✓ Validation HTML5 fonctionne")
            self.take_screenshot("attribut required")

        except Exception as e:
            self.fail(f"Erreur test champs vides: {e}")

    def test_login_sql_injection(self):
        """Test avec tentative d'injection SQL"""
        try:
            print("Test: Tentative d'injection SQL...")

            self.driver.get(f"{self.base_url}web/login")

            # Tentative d'injection SQL
            sql_payloads = [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "admin'--",
                "' UNION SELECT * FROM users --"
            ]
            self.take_screenshot("injection sql")

            for payload in sql_payloads:
                email_field = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "login"))
                )
                email_field.clear()
                email_field.send_keys(payload)

                password_field = self.driver.find_element(By.ID, "password")
                password_field.clear()
                password_field.send_keys(payload)
                self.take_screenshot("email_password")

                login_button = self.driver.find_element(
                    By.CSS_SELECTOR, "button[type='submit']"
                )
                login_button.click()
                self.take_screenshot("echec login")

                # Vérifier que le login échoue
                time.sleep(2)
                current_url = self.driver.current_url
                self.assertIn("web/login", current_url,
                              f"Login a réussi avec payload: {payload}")
                print(f"✓ Injection SQL bloquée: {payload}")

        except Exception as e:
            self.fail(f"Erreur test injection SQL: {e}")

    def tearDown(self):
        if self.driver:
            self.take_screenshot("final_error")
            self.driver.quit()


# if __name__ == "__main__":
#     unittest.main(verbosity=2)
if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='reports'))