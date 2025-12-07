import os
import itertools
from dotenv import load_dotenv
from notion_client import Client
from anki_connect import AnkiConnect

load_dotenv()
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATASOURCE_ID = os.getenv('NOTION_DATASOURCE_ID')

notion = Client(auth=NOTION_TOKEN)
ac = AnkiConnect()

# AnkiがOn/Offのレコードを全て取得し、フィールドリスト化する
def get_fields_list(Anki: bool = False):
  has_more = True
  cursor = None
  all_fields_list = []

  while (has_more):
    res = notion.data_sources.query(
      data_source_id=NOTION_DATASOURCE_ID,
      filter={
        'property': 'Anki',
        'checkbox': {
          'equals': Anki
        }
      },
      start_cursor=cursor
    )

    all_fields_list.append(create_fields_list([props['properties'] for props in res['results']]))
    has_more = res['has_more']
    cursor = res['next_cursor']

  return list(itertools.chain.from_iterable(all_fields_list))

def join_text(text_list):
  return ''.join([d['text']['content'] for d in text_list]) if text_list else ''

def create_fields_list(pages):
  fields_list = []

  for props in pages:
    fields_list.append({
      'UID': f"{props['ID']['unique_id']['prefix']}-{props['ID']['unique_id']['number']}",
      'Spelling': join_text(props['Spelling']['title']),
      'Parts': [ms['name'] for ms in props['Parts']['multi_select']] if props['Parts']['multi_select'] else [],
      'Meanings': join_text(props['Meanings']['rich_text']),
      'Example Sentences': join_text(props['Example Sentences']['rich_text']),
      'Translation': join_text(props['Translation']['rich_text']),
      'Notes': join_text(props['Notes']['rich_text'])
    })

  return fields_list

def main():
  try:
    print('Getting records...')
    fields_list = get_fields_list()
    print('Importing cards into Anki...')
    ac.import_cards(fields_list)
    print('Done.')
  except Exception as e:
    print(e)

if __name__ == "__main__": main()