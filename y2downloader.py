import requests, json
import regex as re
from requests import Session

headers = {
	'Host': 'backend.svcenter.xyz',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
	'Accept': '*/*',
	'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
	'Accept-Encoding': 'gzip, deflate, br',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'X-Requested-Key': 'de0cfuirtgf67a',
	'Content-Length': '150',
	'Origin': 'https://www.y2meta.com',
	'Connection': 'keep-alive',
	'Referer': 'https://www.y2meta.com/',
	'Sec-Fetch-Dest': 'empty',
	'Sec-Fetch-Mode': 'cors',
	'Sec-Fetch-Site': 'cross-site',
	'Pragma': 'no-cache',
	'Cache-Control': 'no-cache',
	'TE': 'trailers',
}

def get_conversion_token(v_id, session):
	url = 'https://www.y2meta.com/youtube/' + v_id
	r = session.get(url)
	html = str(r.content, encoding='utf-8')
	match = re.search(pattern="client_token='(.+?)'", string=html)
	return match.group(1)
def get_token(v_url, v_id):
	headers = {
		'Host': 'www.y2meta.com',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
		'Accept': '*/*',
		'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
		'Accept-Encoding': 'gzip, deflate, br',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'X-Requested-With': 'XMLHttpRequest',
		'Content-Length': '146',
		'Origin': 'https://www.y2meta.com',
		'Connection': 'keep-alive',
		'Referer': f'https://www.y2meta.com/youtube/{v_id}',
		'Cookie': '__cflb=0H28vE9u5mhC7eHFatfCKY413DzgeSGpT8FuDE3jBSm',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-origin',
		'Pragma': 'no-cache',
		'Cache-Control': 'no-cache',
		'TE': 'trailers',
	}
	headers = {
		'Host': 'www.y2meta.com',
		'Accept-Encoding': 'gzip, deflate, br',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'X-Requested-With': 'XMLHttpRequest',
		'Content-Length': '146',
		'Origin': 'https://www.y2meta.com',
		'Connection': 'keep-alive',
		'Referer': f'https://www.y2meta.com/youtube/{v_id}',
		'Cookie': '__cflb=0H28vE9u5mhC7eHFatfCKY413DzgeSGpT8FuDE3jBSm',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-origin',
		'TE': 'trailers',
	}
	session = Session()
	site = f'https://www.y2meta.com/youtube/{v_id}'
	session.head(site)
	c_token = get_conversion_token(v_id, session)
	data = {
		'url': v_url,
		'q_auto': '1',
		'ajax': '1',
		'token': c_token,
	}
	r = session.post(
		'https://www.y2meta.com/analyze/ajax',
		data=data, headers=headers, stream=True,timeout=33600
	)
	from pathlib import Path
	temp_file = Path('temp.txt')
	with temp_file.open('wb') as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk: f.write(chunk)
	html = json.loads(temp_file.read_bytes())['result']
	token = re.search('k__id.+?"(.+?)\\"', html).group(1)
	expiration = re.search('k_time.+?(\d+)', html).group(1)
	v_title = re.search('class="caption text-left">\\r\\n\s+<b>(.+?)</b>', html).group(1)
	return token, expiration, session, v_title

def download_video(url):
	match = re.search(
		pattern=r'\?v=(?P<id>.+?)&|\?v=(?P<id>.+)',
		string=url)
	if match is None: raise Exception()

	v_id = match['id']
	print('v_id:', v_id)
	token, expiration, session, v_title = get_token(url, v_id)
	print('token:', token)
	quality = 320
	backend = 'https://backend.svcenter.xyz/api/convert-by-45fc4be8916916ba3b8d61dd6e0d6994'
	data = {
		'v_id': v_id,
		'fquality': quality,
		'ftype': 'mp3',
		'token': token,
		'timeExpire': expiration,
		'client': 'y2meta.com',
	}
	r = session.post(backend, data=data, headers=headers)
	if r.status_code != 200:
		print('\033[33m', r.content, '\033[0m')
		exit()
	try:
		info = json.loads(r.content)
		d_url = info['d_url']
	except:
		print('\033[33m', r.content, '\033[0m')
		exit()
	print('\033[32m', v_title, '\033[0m', sep='')
	print(d_url)

url = 'https://www.youtube.com/watch?v=cD7JNtrgiKQ&list=PL7vLhuxGed2yCb97tGgCw7HX9nB01iqKC&index=5'
download_video(url)

# token = get_token(url, 'hG2SCu1HXpE')
# print(token)