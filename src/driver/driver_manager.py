from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
import json
import os

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-notifications')
    options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options = options)
    return driver

def login(driver):
    driver.get(os.getenv("SITE_URL"))
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='btnSubmitLogin']"))
    ).click()
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "email_signin"))
    ).send_keys(os.getenv("SITE_USERNAME"))
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "btn-next"))
    ).click()
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "password_signin"))
    ).send_keys(os.getenv("SITE_PASSWORD"))
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "btn-signin"))
    ).click()

def wait_for_browser_to_load(driver):
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "nav-btn-shared_inbox-icon"))
    )
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "shared_inbox"))
    ).click()
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "inbox-option-todo"))
    )

def extract_refresh_token_from_logs(driver, browser_logs):
    for log in browser_logs:
        log = json.loads(log["message"])["message"]
        if ("Network.responseReceived" in log["method"] and "params" in log.keys()):
            try:
                body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': log["params"]["requestId"]})
                log['body'] = body
                try:
                    log["body"]["body"] = json.loads(log["body"]["body"])
                    if "refresh_token" in log["body"]["body"]:
                         token_data = log["body"]["body"]
                         return token_data["refresh_token"]
                except json.JSONDecodeError:
                    pass
            except exceptions.WebDriverException:
                pass

def get_refresh_token():
    driver = create_driver()
    login(driver)
    wait_for_browser_to_load(driver)
    browser_logs = driver.get_log('performance')
    refresh_token = extract_refresh_token_from_logs(driver, browser_logs)
    driver.close()
    return refresh_token
