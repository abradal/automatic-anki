import requests
import json

class AnkiConnect:
  ANKI_CONNECT_URL = 'http://192.168.1.6:8765'
  PEV = 'Passive English Vocab'
  ERRORS = {
    'dup': 'cannot create note because it is a duplicate',
  }

  def request(self, payload):
    res = requests.post(self.ANKI_CONNECT_URL, json=payload)
    return json.loads(res.text)
  
  def add_card(self, fields):
    payload = {
      'action': 'addNote',
      'version': 6,
      'params': {
        'note': {
          'deckName': self.PEV,
          'modelName': f'{self.PEV}',
          'fields': { **fields, 'Parts': ', '.join(fields['Parts']) },
          'options': {
            'allowDuplicate': False
          },
          'tags': fields['Parts']
        }
      }
    }

    return self.request(payload)

  def get_note_id(self, uid):
    payload = {
      'action': 'findNotes',
      'version': 6,
      'params': {
        'query': f'"note:{self.PEV}" "UID:{uid}"'
      }
    }

    res = self.request(payload)
    return res['result'][0]

  def update_card(self, note_id, fields):
    payload = {
      'action': 'updateNote',
      'version': 6,
      'params': {
        'note': {
          'id': note_id,
          'fields': { **fields, 'Parts': ', '.join(fields['Parts']) },
          'options': {
            'allowDuplicate': False
          },
          'tags': fields['Parts']
        }
      }
    }

    return self.request(payload)
  
  def import_cards(self, pages, notion):
    for page in pages:
      fields = page['fields']
      res = self.add_card(fields)

      if res['error'] == self.ERRORS['dup']:
        self.update_card(self.get_note_id(fields['UID']), fields)
      elif res['error']:
        print(f'Failed to import card ({fields["Spelling"]}) - {res["error"]}')
        continue

      notion.set_checkbox_on(page['page_id'])