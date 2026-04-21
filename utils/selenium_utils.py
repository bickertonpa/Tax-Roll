# utils/selenium_utils.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# -------------------------
# Wait and Click
# -------------------------

def wait_and_click(driver, xpath, timeout=15):
    """
    Waits for an element to be present and clicks it using JS.

    Args:
        driver: Selenium WebDriver
        xpath (str): XPath of the element
        timeout (int): max wait time

    Returns:
        WebElement
    """
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

    # Use JS click (more reliable for Angular sites like Ottawa's)
    driver.execute_script("arguments[0].click();", element)

    return element


# -------------------------
# Wait and Send Keys
# -------------------------

def wait_and_send_keys(driver, xpath, value, timeout=15, clear_first=True):
    """
    Waits for an input field and sends keys.

    Args:
        driver: Selenium WebDriver
        xpath (str): XPath of the input field
        value (str): value to input
        timeout (int): max wait time
        clear_first (bool): whether to clear field first

    Returns:
        WebElement
    """
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

    if clear_first:
        element.clear()

    if value:
        element.send_keys(value)

    return element


# -------------------------
# Wait for Results Page
# -------------------------

def wait_for_results(driver, timeout=15):
    """
    Waits for either:
        - results table
        - or error message

    Args:
        driver: Selenium WebDriver
        timeout (int)

    Returns:
        bool: True if something appeared, False if timeout
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: (
                d.find_elements(By.ID, "year1-tax-info") or
                d.find_elements(By.ID, "assessment-search-result-message")
            )
        )
        return True

    except Exception as e:
        print(f"Timeout waiting for results: {e}")
        return False


# -------------------------
# Optional: Wait for Element Visible
# -------------------------

def wait_for_visible(driver, xpath, timeout=15):
    """
    Wait until element is visible (not just present).
    Useful for debugging flaky UI behavior.
    """
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.XPATH, xpath))
    )