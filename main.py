import os
from dotenv import load_dotenv
from notion import Notion
from anki_connect import AnkiConnect
from openai import OpenAI

load_dotenv()
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATASOURCE_ID = os.getenv('NOTION_DATASOURCE_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANKI_CONNECT_URL = os.getenv('ANKI_CONNECT_URL')

notion = Notion(notion_token=NOTION_TOKEN, data_source_id=NOTION_DATASOURCE_ID)
openai = OpenAI(api_key=OPENAI_API_KEY)
ac = AnkiConnect(ANKI_CONNECT_URL)

def main():
  try:
    print('Getting pages...')
    pages = notion.get_pages(openai)
    print('Importing cards into Anki...')
    ac.import_cards(pages, notion)
    print('Done.')
  except Exception as e:
    print(e)

if __name__ == "__main__": main()