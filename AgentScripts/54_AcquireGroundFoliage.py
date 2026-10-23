import pathlib,json,urllib.request,hashlib,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parents[1];entries=[]
for asset in ['shrub_01','grass_medium_01']:
    with urllib.request.urlopen(urllib.request.Request('https://api.polyhaven.com/files/'+asset,headers={'User-Agent':'First24Hours/1.0'}),timeout=60) as r:meta=json.load(r)
    (ROOT/f'ArtSource/Metadata/{asset}-files.json').write_text(json.dumps(meta,indent=2))
    item=meta['gltf']['2k']['gltf'];entries.append((asset+'/model.gltf',item));entries.extend((asset+'/'+n,v) for n,v in item['include'].items())
    for k in ['Alpha','alpha','dry_diff']:
        if k in meta:
            item=meta[k]['2k'].get('png') if k.lower()=='alpha' else meta[k]['2k'].get('jpg')
            if item:entries.append((asset+'/textures/'+item['url'].rsplit('/',1)[-1],item))
def fetch(entry):
    name,item=entry;path=ROOT/'ArtSource/Models/reference_cc0'/name;path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or hashlib.md5(path.read_bytes()).hexdigest()!=item['md5']:
        with urllib.request.urlopen(urllib.request.Request(item['url'],headers={'User-Agent':'First24Hours/1.0'}),timeout=120) as r:data=r.read()
        assert hashlib.md5(data).hexdigest()==item['md5'];path.write_bytes(data)
    print(name,path.stat().st_size,flush=True)
    return {'file':str(path.relative_to(ROOT)),'url':item['url'],'md5':item['md5'],'license':'CC0'}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:manifest=list(pool.map(fetch,entries))
(ROOT/'ArtSource/Metadata/ground-foliage-downloads.json').write_text(json.dumps(manifest,indent=2))
