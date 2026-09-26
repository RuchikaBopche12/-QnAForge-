import json
import re
from typing import Callable
from google import genai
from google.genai import types

def chunk_text(text: str, max_chars: int = 10000):
    text = re.sub(r'\s+', ' ', text).strip()
    if not text: return []
    chunks=[]; start=0
    while start < len(text):
        end=min(start+max_chars,len(text))
        if end < len(text):
            split_at=text.rfind('. ',start,end)
            if split_at > start+max_chars//2: end=split_at+1
        chunks.append(text[start:end].strip()); start=end
    return chunks

def parse_json_response(response):
    raw=(getattr(response,'text','') or '').strip()
    if raw.startswith('```'):
        raw=re.sub(r'^```(?:json)?\s*','',raw); raw=re.sub(r'\s*```$','',raw)
    try: return json.loads(raw)
    except json.JSONDecodeError:
        m=re.search(r'(\[.*\]|\{.*\})',raw,re.S)
        if m: return json.loads(m.group(1))
        raise ValueError('The AI returned invalid JSON.')

def clean_qna(items):
    out=[]
    if not isinstance(items,list): return out
    for item in items:
        if isinstance(item,dict):
            q=str(item.get('question','')).strip(); a=str(item.get('answer','')).strip()
            if q and a: out.append({'question':q,'answer':a})
    return out

def deduplicate(items):
    seen=set(); out=[]
    for item in items:
        key=re.sub(r'\W+',' ',item['question'].lower()).strip()
        if key and key not in seen: seen.add(key); out.append(item)
    return out

def generate_english_qna(client,model,chunk,count):
    prompt=f'''Create exactly {count} meaningful, context-aware Q&A pairs from the source text.\nRules: questions must be answerable from the source; do not invent facts; avoid duplicates; answers concise but complete; return ONLY valid JSON.\nFormat: [{{"question":"...","answer":"..."}}]\n\nSOURCE:\n{chunk}'''
    response=client.models.generate_content(model=model,contents=prompt,config=types.GenerateContentConfig(temperature=0.1,response_mime_type='application/json'))
    return clean_qna(parse_json_response(response))

def translate_qna(client,model,items,language):
    if not items: return []
    payload=json.dumps(items,ensure_ascii=False)
    prompt=f'''Translate the following Q&A pairs into {language}. Preserve EXACTLY {len(items)} items, exact order, and translate both questions and answers. Do not summarize, add, remove, merge or split. Return ONLY valid JSON in this format: [{{"question":"...","answer":"..."}}]\n\nINPUT:\n{payload}'''
    response=client.models.generate_content(model=model,contents=prompt,config=types.GenerateContentConfig(temperature=0.0,response_mime_type='application/json'))
    translated=clean_qna(parse_json_response(response))
    if len(translated)!=len(items): raise ValueError(f'{language} translation returned {len(translated)} items; expected {len(items)}.')
    return translated

def generate_qna_multilingual(text:str,api_key:str,model:str='gemini-3.5-flash-lite',qna_per_chunk:int=5,max_chars:int=10000,progress_callback:Callable[[int,str],None]|None=None):
    client=genai.Client(api_key=api_key); chunks=chunk_text(text,max_chars)
    if not chunks: raise ValueError('No usable text found.')
    english=[]; total_steps=len(chunks)+2
    for index,chunk in enumerate(chunks,1):
        if progress_callback: progress_callback(int((index-1)/total_steps*100),f'Generating English Q&A from chunk {index}/{len(chunks)}...')
        english.extend(generate_english_qna(client,model,chunk,qna_per_chunk))
    english=deduplicate(english)[:qna_per_chunk]
    if not english: raise ValueError('The model did not generate usable English Q&A.')
    if progress_callback: progress_callback(int(len(chunks)/total_steps*100),'Translating Q&A into Hindi...')
    hindi=translate_qna(client,model,english,'Hindi')
    if progress_callback: progress_callback(int((len(chunks)+1)/total_steps*100),'Translating Q&A into Marathi...')
    marathi=translate_qna(client,model,english,'Marathi')
    if not (len(english)==len(hindi)==len(marathi)): raise ValueError('English, Hindi and Marathi Q&A counts do not match.')
    print('========== LANGUAGE CHECK =========='); print('English:',len(english)); print('Hindi:',len(hindi)); print('Marathi:',len(marathi)); print('====================================')
    return {'English':english,'Hindi':hindi,'Marathi':marathi}
