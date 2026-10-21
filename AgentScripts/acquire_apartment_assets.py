"""Public CC0 files only. No accounts, purchasing, checkout or license acceptance."""
import json, hashlib, pathlib, urllib.request, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
HEADERS = {'User-Agent': 'First24Hours-EnvironmentProduction/1.0', 'Referer': 'https://polyhaven.com/'}
MODELS = ['sofa_02','SchoolDesk_01','painted_wooden_chair_02','desk_lamp_arm_01','book_encyclopedia_set_01','alarm_clock_01','vintage_electric_kettle']
TEXTURES = ['wood_floor_worn','painted_plaster_wall','floor_tiles_04','fabric_pattern_05']
manifest = []
def download(entry, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or hashlib.md5(path.read_bytes()).hexdigest() != entry['md5']:
        req = urllib.request.Request(entry['url'], headers=HEADERS)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    data = response.read()
                assert hashlib.md5(data).hexdigest() == entry['md5'], 'Checksum mismatch'
                path.write_bytes(data)
                break
            except Exception:
                if attempt == 2: raise
                time.sleep(1)
    manifest.append({'file': str(path.relative_to(ROOT)), 'url': entry['url'], 'md5': entry['md5'], 'bytes': path.stat().st_size})
for name in MODELS:
    meta = json.loads((ROOT / ('ArtSource/Metadata/'+name+'.json')).read_text('utf-8-sig'))
    info = meta['gltf']['2k']['gltf']
    folder = ROOT / 'ArtSource/Models' / name
    download(info, folder / (name+'.gltf'))
    for relative, entry in info.get('include', {}).items():
        download(entry, folder / relative)
    print('Downloaded model:', name, flush=True)
for name in TEXTURES:
    meta = json.loads((ROOT / ('ArtSource/Metadata/'+name+'.json')).read_text('utf-8-sig'))
    for channel in [('col_01' if name == 'fabric_pattern_05' else 'Diffuse'), 'nor_dx', 'Rough']:
        info = meta[channel]['2k']['jpg']
        download(info, ROOT / 'ArtSource/Textures' / name / pathlib.PurePosixPath(info['url']).name)
    print('Downloaded texture:', name, flush=True)
(ROOT/'ArtSource/download-manifest.json').write_text(json.dumps(manifest,indent=2))
print('Verified files:', len(manifest), flush=True)
