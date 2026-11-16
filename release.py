#!/usr/bin/env python3
"""Build a reproducible release from an explicit allowlist; no runtime data."""
from pathlib import Path
import base64,gzip,hashlib,json,re,stat,zipfile
ROOT=Path(__file__).resolve().parent
TITLE='Herdr App（macOS 桌面版）繁體中文化'
VERSION='0.1.16'
FILES=('RELEASE_NOTES.md','README.md','PUBLISHING.md','LICENSE','NOTICE.md','licenses/THIRD-PARTY-NOTICES.txt','.gitignore','中文化工具.py','payload.json.gz','一鍵安裝繁體中文.command','還原英文版.command','release.py')
def sha(data):return hashlib.sha256(data).hexdigest()
def inspect(path,data):
 if path=='payload.json.gz':
  value=json.loads(gzip.decompress(data))
  chunks=[json.dumps({k:v for k,v in value.items() if k!='patches'}).encode()]
  chunks.extend(base64.b64decode(p['data'],validate=True) for p in value['patches'])
  chunks.extend(p['path'].encode() for p in value['patches'])
 else:chunks=[data]
 for chunk in chunks:
  text=chunk.decode('utf-8',errors='ignore')
  # Detect concrete account/volume paths, not the generic patterns below.
  if re.search(r'/(?:Users|Volumes)/[A-Za-z0-9_.-]+(?:/|\\)',text):raise ValueError('Local absolute path in '+path)
  if re.search(r'[A-Za-z]:\\Users\\[A-Za-z0-9_.-]+\\',text):raise ValueError('Local account path in '+path)
  if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s+[A-Za-z0-9+/]{20}',text):raise ValueError('Private-key data in '+path)
 if path.endswith('.command') and b'/opt/anaconda' in data:raise ValueError('Machine-specific Python launcher')

def main():
 for name in FILES:
  p=ROOT/name
  if p.is_symlink() or not p.is_file():raise ValueError('Missing or linked release file: '+name)
  inspect(name,p.read_bytes())
 hashes=''.join(sha((ROOT/name).read_bytes())+'  '+name+'\n' for name in FILES)
 (ROOT/'SHA256SUMS').write_text(hashes,encoding='utf-8')
 target=ROOT.parent/(TITLE+'-v'+VERSION+'.zip');temporary=target.with_suffix('.zip.new')
 try:
  with temporary.open('xb') as stream:
   with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for name in (*FILES,'SHA256SUMS'):
     item=zipfile.ZipInfo(TITLE+'/'+name,date_time=(2026,1,1,0,0,0));item.create_system=3;item.compress_type=zipfile.ZIP_DEFLATED;item.extra=b'';item.comment=b''
     mode=0o755 if name.endswith('.command') else 0o644
     item.external_attr=(stat.S_IFREG|mode)<<16
     archive.writestr(item,(ROOT/name).read_bytes())
  temporary.replace(target)
 finally:
  if temporary.exists():temporary.unlink()
 (target.parent/(target.name+'.sha256')).write_text(sha(target.read_bytes())+'  '+target.name+'\n',encoding='utf-8')
 print(json.dumps({'archive':target.name,'files':len(FILES)+1,'bytes':target.stat().st_size,'sha256':sha(target.read_bytes())},ensure_ascii=False))
if __name__=='__main__':main()
