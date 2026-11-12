"""Chrome WebDriver factory. Selenium Manager resolves the matching ChromeDriver."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from betting_qa.config import Settings


def create_driver(settings: Settings) -> WebDriver:
    width, height = settings.window_size
    options = Options()
    if settings.headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={width},{height}")
    # Same date/number formatting on every machine (the app renders in the browser locale).
    options.add_argument("--lang=en-US")
    options.add_experimental_option("prefs", {"intl.accept_languages": "en-US,en"})
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})  # console log for evidence
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(width, height)
    return driver
