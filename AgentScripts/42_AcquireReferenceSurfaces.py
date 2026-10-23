import pathlib,json,urllib.request,hashlib,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parents[1]
entries=[]
for asset in ['asphalt_03','concrete_pavement','forest_leaves_02']:
    meta=json.loads((ROOT/f'ArtSource/Metadata/{asset}-files.json').read_text('utf-8-sig'))
    for key in ['Diffuse' if 'Diffuse' in meta else 'diff','nor_dx','Rough']:
        item=meta[key]['2k']['jpg'];entries.append((asset+'/'+item['url'].rsplit('/',1)[-1],item))
for asset in ['street_lamp_01','painted_wooden_sofa']:
    meta=json.loads((ROOT/f'ArtSource/Metadata/{asset}-files.json').read_text('utf-8-sig'))
    item=meta['gltf']['2k']['gltf'];entries.append((asset+'/model.gltf',item))
    entries.extend((asset+'/'+name,value) for name,value in item['include'].items())
def fetch(entry):
    name,item=entry;path=ROOT/'ArtSource/Models/reference_cc0'/name;path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or hashlib.md5(path.read_bytes()).hexdigest()!=item['md5']:
        with urllib.request.urlopen(urllib.request.Request(item['url'],headers={'User-Agent':'First24Hours/1.0'}),timeout=120) as r:data=r.read()
        assert hashlib.md5(data).hexdigest()==item['md5'],name
        path.write_bytes(data)
    print(name,path.stat().st_size,flush=True)
    return {'file':str(path.relative_to(ROOT)),'url':item['url'],'md5':item['md5'],'license':'CC0'}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:manifest=list(pool.map(fetch,entries))
(ROOT/'ArtSource/Metadata/reference-cc0-downloads.json').write_text(json.dumps(manifest,indent=2))
