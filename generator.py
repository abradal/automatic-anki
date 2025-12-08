import json

def generate_example_and_translation(openai, spelling: str, meanings: str):
  prompt = f"""
  You are an English assistant.
  Word: {spelling}
  Meaning: {meanings}

  Provide:
  - One simple natural English example sentence.
  - Its Japanese translation.
  Output in the following JSON format:

  {{
    "example": "...",
    "translation": "..."
  }}
  """

  res = openai.chat.completions.create(
    model='gpt-4.1-mini',
    messages=[{'role': 'user', 'content': prompt}],
    max_tokens=200
  )
  text = res.choices[0].message.content

  try:
    data = json.loads(text)
    return data.get('example', ''), data.get('translation', '')
  except Exception:
    lines = text.split('\n')
    example = next((l.split(':', 1)[1].strip() for l in lines if 'example' in l.lower()), '')
    translation = next((l.split(':', 1)[1].strip() for l in lines if 'translation' in l.lower()), '')
    return example, translation