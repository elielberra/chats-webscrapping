import os
import copy
import requests
import json

from utils.file_utils import write_chat_file

def get_api_prospect_messages_data():
    messages_url = os.getenv("API_MESSAGES_URL")
    messages_query_params = os.getenv("API_MESSAGES_URL_QUERY_PARAMS")
    return messages_url, messages_query_params

def get_full_messages(chats, chats_dir_name, access_token):
    chats = copy.deepcopy(chats)
    for prospect_chat in chats:
        prospect_id = prospect_chat["lastOperations"][0]["prospect"]
        messages_base_url, messages_query_params = get_api_prospect_messages_data()
        headers = {'Authorization': access_token}
        prospect_messages_pending = True
        while prospect_messages_pending:
            message_id = prospect_chat["lastOperations"][0]["_id"]
            messages_url = f'{messages_base_url}/{prospect_id}/{message_id}?{messages_query_params}'
            try:
                response = requests.get(messages_url, headers=headers)
                if response.status_code == 200:
                    parsed_response = json.loads(response.text)
                    prospect_messages_segment = parsed_response["operations"]
                    prospect_chat["lastOperations"] = prospect_messages_segment + prospect_chat["lastOperations"]
                elif response.status_code == 204:
                    write_chat_file(prospect_chat, chats_dir_name)
                    prospect_messages_pending = False
                else:
                    raise requests.exceptions.HTTPError(f"Unexpected status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f'Not able to fech all the messages of prospect with id: {prospect_id}')
                raise SystemExit(e)
    return chats
