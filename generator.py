import json

def clean(s: str):
  if not isinstance(s, str): return s
  return s.strip().strip('"').rstrip(',').strip()

def generate(openai, spelling: str, meanings: str):
  prompt = f"""
  You are an English assistant.
  Word: {spelling}
  {f'Meanings: {meanings}' if meanings else ''}

  Provide:
  {'- Concise meanings in Japanese' if not meanings else ''}
  - One simple natural English example sentence.
  - Japanese translation of example sentence.
  Output in the following JSON format:

  {{
    {'"meanings": "...",' if not meanings else ''}
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

    # meaningsがあればそれを返し、exampleやtranslationは両方上書きする
    return (
      clean(meanings or data.get('meanings', '')),
      clean(data.get('example', '')),
      clean(data.get('translation', ''))
    )
  except Exception:
    lines = text.split('\n')

    example = next((l.split(':', 1)[1].strip() for l in lines if 'example' in l.lower()), '')
    translation = next((l.split(':', 1)[1].strip() for l in lines if 'translation' in l.lower()), '')
    return clean(meanings), clean(example), clean(translation)