from notion_client import Client
from generator import generate_example_and_translation

class Notion:
  def __init__(self, notion_token, data_source_id):
    self.notion = Client(auth=notion_token)
    self.data_source_id = data_source_id

  def create_fields(self, props, page_id, openai):
    def join_text(text_list):
      return ''.join([d['text']['content'] for d in text_list]) if text_list else ''

    spelling = join_text(props['Spelling']['title'])
    meanings = join_text(props['Meanings']['rich_text'])
    example = join_text(props['Example Sentences']['rich_text'])
    translation = join_text(props['Translation']['rich_text'])

    if spelling and meanings and (not example or not translation):
      example, translation = generate_example_and_translation(
        openai, spelling, meanings
      )

      self.update_page(page_id, {
        'Example Sentences': {
          'rich_text': [{
            'type': 'text',
            'text': { 'content': example }
          }]
        },
        'Translation': {
          'rich_text': [{
            'type': 'text',
            'text': { 'content': translation }
          }]
        }
      })

    return {
      'UID': f"{props['ID']['unique_id']['prefix']}-{props['ID']['unique_id']['number']}",
      'Spelling': spelling,
      'Parts': [ms['name'] for ms in props['Parts']['multi_select']] if props['Parts']['multi_select'] else [],
      'Meanings': meanings,
      'Example Sentences': example,
      'Translation': translation,
      'Notes': join_text(props['Notes']['rich_text'])
    }

  # AnkiがOffのページを全て取得する
  def get_pages(self, openai, Anki: bool = False):
    has_more = True
    cursor = None
    pages = []

    while (has_more):
      res = self.notion.data_sources.query(
        data_source_id=self.data_source_id,
        filter={
          'property': 'Anki',
          'checkbox': { 'equals': Anki }
        },
        start_cursor=cursor
      )

      results = res['results']

      for page in results:
        page_id = page['id']
        fields = self.create_fields(page['properties'], page_id, openai)

        # Spelling, Meaningsが空のページを除外
        if fields['Spelling'] and fields['Meanings']:
          pages.append({
            'page_id': page_id,
            'fields': fields
          })

      has_more = res['has_more']
      cursor = res['next_cursor']

    return pages

  def update_page(self, page_id, properties):
    self.notion.pages.update(
      page_id=page_id,
      properties=properties
    )