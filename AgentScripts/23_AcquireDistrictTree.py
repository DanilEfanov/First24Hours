import pathlib,json,urllib.request,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'ArtSource/Metadata/district-tree-files.json').read_text('utf-8-sig'))
info=meta['gltf']['2k']['gltf']
folder=ROOT/'ArtSource/Models/district_tree_small_02'
entries=[('tree.gltf',info)]+list(info.get('include',{}).items())
entries.append(('textures/tree_small_02_leaves_alpha_2k.png',meta['leaves_alpha']['2k']['png']))
manifest=[]
for relative,entry in entries:
    path=folder/relative;path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or hashlib.md5(path.read_bytes()).hexdigest()!=entry['md5']:
        request=urllib.request.Request(entry['url'],headers={'User-Agent':'First24Hours/1.0'})
        with urllib.request.urlopen(request,timeout=120) as response:data=response.read()
        assert hashlib.md5(data).hexdigest()==entry['md5']
        path.write_bytes(data)
    manifest.append({'file':str(path.relative_to(ROOT)),'url':entry['url'],'md5':entry['md5'],'size':path.stat().st_size})
    print(relative,path.stat().st_size,flush=True)
(ROOT/'ArtSource/Metadata/district-tree-downloads.json').write_text(json.dumps(manifest,indent=2))
