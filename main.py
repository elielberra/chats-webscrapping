from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
import json
import requests
import time
from datetime import datetime, timedelta
import copy
import unicodedata

def get_start_time_and_date(): 
    start_time = time.time()
    current_date = datetime.now().strftime("%Y-%m-%d__%H-%M")
    return start_time, current_date

def create_chats_directory(current_date):
    dir_name = f'{current_date}{os.getenv("BASE_FILENAME")}'
    os.mkdir(dir_name)
    return dir_name

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

def get_refresh_token_from_logs(browser_logs):
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

def get_api_prospects_data():
    return os.getenv("API_PROSPECTS_URL"), os.getenv("API_PROSPECTS_NUM_RECORDS_PER_REQ"), os.getenv("API_PROSPECTS_URL_QUERY_PARAMS")

def get_new_access_token(refresh_token):
    body = {"refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": "app"}
    oauth_api_key =  os.getenv("API_GEN_REFRESH_TOKEN_KEY")
    headers = {'Authorization': oauth_api_key}
    new_acces_token_url = os.getenv("API_GEN_REFRESH_TOKEN_URL")
    response = requests.post(new_acces_token_url, json=body, headers=headers)
    if response.status_code == 200:
        parsed_response = json.loads(response.text)
        return parsed_response["access_token"]
    
def get_full_messages(chats, chats_dir_name, access_token):
    chats = copy.deepcopy(chats)
    for prospect_chat in chats:
        prospect_id = prospect_chat["lastOperations"][0]["prospect"]
        chats_base_url = os.getenv("API_CHATS_URL")
        chats_query_params = os.getenv("API_CHATS_URL_QUERY_PARAMS")
        headers = {'Authorization': access_token}
        prospect_chats_pending = True
        while prospect_chats_pending:
            message_id = prospect_chaft["lastOperations"][0]["_id"]
            chats_url = f'{chats_base_url}/{prospect_id}/{message_id}?{chats_query_params}'
            response = requests.get(chats_url, headers=headers)
            if response.status_code == 200:
                parsed_response = json.loads(response.text)
                prospect_chats = parsed_response["operations"]
                prospect_chat["lastOperations"] = prospect_chats + prospect_chat["lastOperations"]
            elif response.status_code == 204:
                write_chat_file(prospect_chat, chats_dir_name)
                prospect_chats_pending = False
            else:
                print(response.status_code)
                print(response.text)
                print("Not able to fech all the records of prospect", prospect_id)
                break
    return chats

def check_if_chats_pending_for_retrieval(chats):
    return chats == []

def format_delta_date(delta):
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_execution_time(start_time):
    end_time = time.time()
    execution_time_seconds = end_time - start_time
    execution_time_timedelta = timedelta(seconds=execution_time_seconds)
    execution_time_formatted =format_delta_date(execution_time_timedelta)
    return execution_time_formatted

def get_person_data(chat):
    try:
        first_name = chat.get("firstName", "")
        last_name = chat.get("lastName", "")
        email = chat.get("emails", [{"address": ""}])[0].get("address", "") if chat.get("emails") else ""
        phone = chat.get("phones", [{"originalNumber": ""}])[0].get("originalNumber", "") if chat.get("phones") else ""
        source = chat.get("interest", {}).get("source", "")
        return first_name, last_name, email, phone, source
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        
def normalize_text(filename):
    normalized_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('utf-8')
    return normalized_filename

def sanitize_filename(filename):
    invalid_chars = '/\:*?"<>|'
    filename_no_invalid_chars = filename
    for char in invalid_chars:
        filename_no_invalid_chars = filename_no_invalid_chars.replace(char, '_')
    filename_no_whitespace = ' '.join(filename_no_invalid_chars.split())
    max_filename_length = 255
    filename_sliced = filename_no_whitespace[:max_filename_length]
    filename_std = unicodedata.normalize('NFKD', filename_sliced).encode('ASCII', 'ignore').decode('utf-8')
    return filename_std

def write_chat_file(chat, chats_dir_name):
    first_name, last_name, phone, email, source = get_person_data(chat) 
    chat_filename = f'{first_name}_{last_name}_{phone}_{email}-{source}.json'
    print(chat_filename)
    chat_filename_clean = sanitize_filename(chat_filename)
    chat_filepath = os.path.join(chats_dir_name, chat_filename_clean)
    with open(chat_filepath, 'w', encoding='utf-8') as chat_file:
        json.dump(chat, chat_file, indent=2, ensure_ascii=False)

def write_metadata_file(start_time, current_date, chats_dir_name):
    execution_time = get_execution_time(start_time)
    metadata_filename = f'{current_date}{os.getenv("BASE_FILENAME")}--metadata.txt'
    metadata_filepath = os.path.join(chats_dir_name, metadata_filename)
    with open(metadata_filepath, 'w', encoding='utf-8') as metadata_file:
        metadata_file.write(f"Date of backup: {current_date}\n")
        metadata_file.write(f"Time to create the backup: {execution_time}\n")
        metadata_file.write(f"Total number of chats saved: {len(chats_data)}\n")

start_time, current_date = get_start_time_and_date()
load_dotenv()
chats_dir_name = create_chats_directory(current_date)
driver = create_driver()
login(driver)
wait_for_browser_to_load(driver)
browser_logs = driver.get_log('performance')
refresh_token = get_refresh_token_from_logs(browser_logs)
driver.close()
prospects_base_url, records_per_req, prospects_query_params = get_api_prospects_data()
records_pending = True
pagination_num = 0
chats_data = []

while records_pending:
    access_token = f'Bearer {get_new_access_token(refresh_token)}'
    headers = {'Authorization': access_token}
    prospects_url = f'{prospects_base_url}/{pagination_num}/{records_per_req}?{prospects_query_params}'
    record_num_start = ((pagination_num + 1) * int(records_per_req)) - (int(records_per_req) - 1)
    record_num_end = (pagination_num + 1) * int(records_per_req)
    print(f'Bringing records: from {record_num_start} to {record_num_end}')
    response = requests.get(prospects_url, headers=headers)
    if response.status_code == 200:
        parsed_response = json.loads(response.text)
        chats = parsed_response["prospects"]
        if check_if_chats_pending_for_retrieval(chats):
            records_pending = False
        else:
            chats_with_all_prospect_messages = get_full_messages(chats, chats_dir_name, access_token)
            chats_data.append(chats_with_all_prospect_messages)
            pagination_num += 1
    else:
        print(response.status_code)
        print(response.text)
        print("Not able to fech all the chats batch", pagination_num)
        break

write_metadata_file(start_time, current_date, chats_dir_name)
