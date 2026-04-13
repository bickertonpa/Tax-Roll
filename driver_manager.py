# driver_manager.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class DriverManager:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None

    def start(self):
        options = Options()

        if self.headless:
            options.add_argument("--headless=new")  # modern Chrome

        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=1")

        self.driver = webdriver.Chrome(options=options)
        return self.driver

    def stop(self):
        if self.driver:
            self.driver.quit()