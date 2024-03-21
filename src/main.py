from dotenv import load_dotenv
from driver.driver_manager import get_refresh_token
from utils.time_utils import get_start_time_and_date
from utils.file_utils import create_chats_directory, write_metadata_file
from api.prospects import fetch_prospects_chats

if __name__ == '__main__':
    start_time, current_date = get_start_time_and_date()
    load_dotenv()
    chats_dir_name = create_chats_directory(current_date)
    refresh_token = get_refresh_token()
    chats_data = fetch_prospects_chats(chats_dir_name, refresh_token)
    write_metadata_file(start_time, current_date, chats_dir_name, chats_data)
