import os
from dotenv import load_dotenv
from notion import Notion
from anki_connect import AnkiConnect

load_dotenv()
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATASOURCE_ID = os.getenv('NOTION_DATASOURCE_ID')

notion = Notion(token=NOTION_TOKEN, data_source_id=NOTION_DATASOURCE_ID)
ac = AnkiConnect()

def main():
  try:
    print('Getting pages...')
    pages = notion.get_pages()
    print('Importing cards into Anki...')
    ac.import_cards(pages, notion)
    print('Done.')
  except Exception as e:
    print(e)

if __name__ == "__main__": main()