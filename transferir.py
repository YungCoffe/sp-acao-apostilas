import hashlib, json, re, urllib.request, http.cookiejar
from pathlib import Path
from html import unescape
items = json.loads('[{"file": "matematica1.pdf", "http": 200, "url": "https://tmpfiles.org/wXAIavZ6MEGb/matematica1.pdf", "status": "success", "size": 59060186, "sha256": "ca8a89d25179f41782600482238b372f14f28f648e077cb645465942cc26f9e3"}, {"file": "matematica2.pdf", "parts": [{"url": "https://tmpfiles.org/wHAwa8Z3UvvM/mat2part0.bin", "sha256": "39efc77b6e14cefa55d416358e0e26948b247c3ba6bdf16fcba59d2007190b2c"}, {"url": "https://tmpfiles.org/w5Aka4ZfUb34/mat2part1.bin", "sha256": "9535bf0abdfd11550838e5e4c9f5e6a720c5abc1696b84e5c51eefccc17af8eb"}], "sha256": "9b4f8e40b4bca80638b4612876ffc7ce68a8d5fc30e86f49aa32d986478e18c7"}, {"file": "matematica3.pdf", "http": 200, "url": "https://tmpfiles.org/wPADaXZqM4BM/matematica3.pdf", "status": "success", "size": 67404236, "sha256": "1cfbf4b728946353e811ad90abb1e676694f251104093183827d08d8bbc88213"}, {"file": "portugues1.pdf", "http": 200, "url": "https://tmpfiles.org/wjAOaJZrMq2k/portugues1.pdf", "status": "success", "size": 35375890, "sha256": "f0c8d7b486de47130a665bb6e09635dfb9d71dcccb84984fc06ed51fad759341"}, {"file": "portugues2.pdf", "http": 200, "url": "https://tmpfiles.org/wUAUa9ZAM4h6/portugues2.pdf", "status": "success", "size": 44626847, "sha256": "5d0b0b2b5124eab869ae09e04ed857c7a508ede4a188cc7c8c31e89f3d900788"}, {"file": "portugues3.pdf", "http": 200, "url": "https://tmpfiles.org/w6ALapZQM2P7/portugues3.pdf", "status": "success", "size": 69921666, "sha256": "2a6d7d37b0d3c33e26c390db129dd6888e88fad2718ffefad8ada0699cb4d82b"}]')

def get_file(url, target):
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    with op.open(url, timeout=90) as res: html = res.read().decode()
    hits = re.findall(r'href=["\']([^"\']+/dl/[^"\']+)["\']', html)
    if len(hits) != 1: raise RuntimeError('Link de download indisponível')
    with op.open(unescape(hits[0]), timeout=180) as res, open(target, 'wb') as out:
        while True:
            b = res.read(1024*1024)
            if not b: break
            out.write(b)

for item in items:
    name=item['file']
    if 'parts' in item:
        chunks=[]
        for i, part in enumerate(item['parts']):
            path=f'{name}.part{i}'
            get_file(part['url'],path)
            if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=part['sha256']: raise RuntimeError('checksum da parte')
            chunks.append(path)
        with open(name,'wb') as out:
            for path in chunks:
                with open(path,'rb') as src:
                    while True:
                        b=src.read(1024*1024)
                        if not b: break
                        out.write(b)
                Path(path).unlink()
    else:
        get_file(item['url'],name)
    if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=item['sha256']: raise RuntimeError('checksum do PDF: '+name)
    print(name,'OK',flush=True)
