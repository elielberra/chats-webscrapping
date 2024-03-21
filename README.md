# chats-webscrapping

## About
This is a web scrapping program that retrieves all the chats from all the users that interact with a messaging CRM. It starts by loading a testing selenium chrome driver. This browser handles the initial login into the CRM and enables the retrieval of the refresh token which will be in charge of retrieving the access token. Since the CRM has OAuth as an authentication method, this access token will grant access to the chat resources. The chats data will be fetched through requests to specific endpoints of the backend of the CRM. All the chats will be stored in JSON format into its own separate directory.


## How to Use It
### Requirements
- python 3
- python3.8-venv (on debian systems)

A .env file must be created with this structure (due to security reasons the values have been removed):
```
SITE_URL="insert_value"
SITE_USERNAME="insert_value"
SITE_PASSWORD="insert_value"
API_PROSPECTS_URL="insert_value"
API_PROSPECTS_URL_QUERY_PARAMS="insert_value"
API_PROSPECTS_NUM_RECORDS_PER_REQ="insert_value"
API_MESSAGES_URL="insert_value"
API_MESSAGES_URL_QUERY_PARAMS="insert_value"
API_GEN_REFRESH_TOKEN_URL="insert_value"
API_GEN_REFRESH_TOKEN_KEY="insert_value"
BASE_FILENAME="insert_value"
```
### How to Run It
Navigate to the directory of this repository with the terminal.

`cd <directory/of/this/repo>`

It is a good practice to first create and activate a virtual environment. To do so run the commands:
- on Debian systems:
```
sudo apt install python3.8-venv # (If not previously installed)
python3 -m venv webscrapping
source webscrapping/bin/activate
```
- on Windows:
```
py -m venv webscrapping
.\webscrapping\Scripts\activate
```

Install the dependencies:

`pip install -r requirements.txt`

In order to start this app run the command:

`python3 src/main.py`
