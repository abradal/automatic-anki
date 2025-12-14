import json
import re

def clean(s: str):
  if not isinstance(s, str):
    return s
  return s.strip().strip('"').rstrip('",').strip()

def extract(key: str, text: str):
  m = re.search(rf'"{key}"\s*:\s*"([^"]*)"', text)
  return m.group(1) if m else ''

def generate(openai, spelling: str, meanings: str):
  prompt = f"""
  You are an English assistant.
  Word: {spelling}
  {f'Meanings: {meanings}' if meanings else ''}

  Provide:
  {'- Concise meanings in Japanese' if not meanings else ''}
  - One simple natural English example sentence.
  - Japanese translation of the example sentence.

  Return ONLY valid JSON on a single line.
  No markdown, no comments, no trailing commas.
  {{{'"meanings": "...",' if not meanings else ''} "example": "...", "translation": "..."}}
  """

  res = openai.chat.completions.create(
    model='gpt-4.1-mini',
    messages=[{'role': 'user', 'content': prompt}],
    max_tokens=200
  )
  text = res.choices[0].message.content.strip()

  try:
    data = json.loads(text)
    return (
      clean(meanings or data.get('meanings', '')),
      clean(data.get('example', '')),
      clean(data.get('translation', ''))
      )
  except Exception:
    # fallback
    fb_meanings = extract('meanings', text)
    example = extract('example', text)
    translation = extract('translation', text)
    return (
      clean(meanings or fb_meanings),
      clean(example),
      clean(translation)
    )