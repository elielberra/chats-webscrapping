import os
import unicodedata
import json
from utils.time_utils import get_execution_time

def create_chats_directory(current_date):
    dir_name = f'{current_date}{os.getenv("BASE_FILENAME")}'
    os.mkdir(dir_name)
    return dir_name

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

def write_metadata_file(start_time, current_date, chats_dir_name, chats_data):
    execution_time = get_execution_time(start_time)
    metadata_filename = f'{current_date}{os.getenv("BASE_FILENAME")}--metadata.txt'
    metadata_filepath = os.path.join(chats_dir_name, metadata_filename)
    with open(metadata_filepath, 'w', encoding='utf-8') as metadata_file:
        metadata_file.write(f"Date of backup: {current_date}\n")
        metadata_file.write(f"Time to create the backup: {execution_time}\n")
        metadata_file.write(f"Total number of chats saved: {len(chats_data)}\n")
