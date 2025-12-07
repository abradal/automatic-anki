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
  
  def import_cards(self, fields_list):
    for fields in fields_list:
      res = self.add_card(fields)

      if res['error'] == self.ERRORS['dup']:
        self.update_card(self.get_note_id(fields['UID']), fields)

    # 削除処理
    # notion_uids = [fields['UID'] for fields in fields_list]