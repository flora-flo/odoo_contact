import os
import time
import unittest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from dotenv import load_dotenv

load_dotenv()


class TestOdooLogin(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.maximize_window()
        self.driver.get(os.getenv("ODOO_URL"))
        self.wait = WebDriverWait(self.driver, 10)  # Timeout augmenté à 10s
        self.test_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    def take_screenshot(self, name):
        """Prend un screenshot avec nom timestampé"""
        screenshot_name = f"screenshot_{self.test_start_time}_{name}.png"
        self.driver.save_screenshot(screenshot_name)
        print(f"Screenshot sauvegardé : {screenshot_name}")

    def test_login(self):
        """Test basique de connexion"""
        # Étape 1: Page de login
        self.take_screenshot("01_login_page")

        email = os.getenv("ODOO_EMAIL")
        password = os.getenv("ODOO_PASSWORD")

        # Étape 2: Saisie des identifiants
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "login")))
        email_field.send_keys(email)
        self.take_screenshot("02_email_entered")

        password_field = self.driver.find_element(By.NAME, "password")
        password_field.send_keys(password + Keys.RETURN)
        self.take_screenshot("03_password_submitted")

        # Étape 3: Vérification
        try:
            self.wait.until(EC.title_contains("Odoo"))  # Attente explicite
            self.take_screenshot("04_login_success")
            print("Connexion réussie - Page titre contient 'Odoo'")
        except Exception as e:
            self.take_screenshot("error_final_state")
            raise

        # Pause finale pour visualisation
        time.sleep(10)  # 10 secondes avant fermeture

    def tearDown(self):
        if hasattr(self, '_outcome') and any(self._outcome.errors):
            self.take_screenshot("final_error_state")
        self.driver.quit()



# if __name__ == "__main__":
#     unittest.main()
if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='reports'))
