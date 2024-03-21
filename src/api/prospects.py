import json
import requests
import os
from utils.log import log_prospects_req_status
from api.tokens import get_new_access_token
from api.messages import get_full_messages

def get_api_prospects_data():
    prospects_url = os.getenv("API_PROSPECTS_URL")
    prospects_per_req = os.getenv("API_PROSPECTS_NUM_RECORDS_PER_REQ")
    prospects_query_params = os.getenv("API_PROSPECTS_URL_QUERY_PARAMS")
    return prospects_url, prospects_per_req, prospects_query_params

def check_if_chats_pending_for_retrieval(chats):
    return chats == []

def fetch_prospects_chats(chats_dir_name, refresh_token):
    prospects_base_url, records_per_req, prospects_query_params = get_api_prospects_data()
    records_pending = True
    pagination_num = 0
    chats_data = []
    while records_pending:
        log_prospects_req_status(pagination_num, records_per_req)
        prospects_req_url = f'{prospects_base_url}/{pagination_num}/{records_per_req}?{prospects_query_params}'
        access_token = f'Bearer {get_new_access_token(refresh_token)}'
        prospects_req_headers = {'Authorization': access_token}
        try:
            response = requests.get(prospects_req_url, headers=prospects_req_headers)
            parsed_response = json.loads(response.text)
            chats = parsed_response["prospects"]
            if check_if_chats_pending_for_retrieval(chats):
                records_pending = False
            else:
                chats_with_all_prospect_messages = get_full_messages(chats, chats_dir_name, access_token)
                chats_data.append(chats_with_all_prospect_messages)
                pagination_num += 1
        except requests.exceptions.RequestException as e:
            print(f'Not able to fech all the prospects chats. Failed batch pagination number: {pagination_num}')
            raise SystemExit(e)
    return chats_data
