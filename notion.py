import itertools
from notion_client import Client

class Notion:
  def __init__(self, token, data_source_id):
    self.notion = Client(auth=token)
    self.data_source_id = data_source_id

  def create_fields(self, props):
    def join_text(text_list):
      return ''.join([d['text']['content'] for d in text_list]) if text_list else ''

    return {
      'UID': f"{props['ID']['unique_id']['prefix']}-{props['ID']['unique_id']['number']}",
      'Spelling': join_text(props['Spelling']['title']),
      'Parts': [ms['name'] for ms in props['Parts']['multi_select']] if props['Parts']['multi_select'] else [],
      'Meanings': join_text(props['Meanings']['rich_text']),
      'Example Sentences': join_text(props['Example Sentences']['rich_text']),
      'Translation': join_text(props['Translation']['rich_text']),
      'Notes': join_text(props['Notes']['rich_text'])
    }

  # AnkiがOffのページを全て取得する
  def get_pages(self, Anki: bool = False):
    has_more = True
    cursor = None
    pages = []

    while (has_more):
      res = self.notion.data_sources.query(
        data_source_id=self.data_source_id,
        filter={
          'property': 'Anki',
          'checkbox': {
            'equals': Anki
          }
        },
        start_cursor=cursor
      )

      results = res['results']

      pages.append([{
        'page_id': p['id'],
        'fields': self.create_fields(p['properties'])
      } for p in results])

      has_more = res['has_more']
      cursor = res['next_cursor']

    return list(itertools.chain.from_iterable(pages))

  def set_checkbox_on(self, page_id):
    self.notion.pages.update(
      page_id=page_id,
      properties={
        'Anki': {
          'checkbox': True
        }
      }
    )