#!/usr/bin/env python3
"""Offline, exact-version Herdr localization with local verified rollback."""
from pathlib import Path
import argparse,base64,ctypes,datetime,gzip,hashlib,json,os,platform,plistlib,shutil,struct,subprocess,sys
ROOT=Path(__file__).resolve().parent
EXPECTED='985e70ce4d78c58ceb1e5e6ea2ccb03231d46fef18a0e04ec6ca5380a4099805'
BINARY=Path('Contents/MacOS/Herdr')
STATE=ROOT/'安裝紀錄.json'
def sha(data):return hashlib.sha256(data).hexdigest()
def package_revision():
 tool=Path(__file__).resolve()
 return sha(tool.read_bytes()+(tool.parent/'payload.json.gz').read_bytes())

def save_json(path,value):
 data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
 temp=path.with_name(path.name+'.new')
 fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(temp,path)
 finally:
  if temp.exists():temp.unlink()
def payload():
 data=json.loads(gzip.decompress((ROOT/'payload.json.gz').read_bytes()))
 if data['format']!=1 or data['original_sha256']!=EXPECTED:raise RuntimeError('中文化資料格式或版本不正確。')
 return data

def require_app(app):
 if app.is_symlink() or (app/BINARY).is_symlink():raise RuntimeError('App 或執行檔是符號連結，已停止以避免修改其他位置。')
 info=plistlib.loads((app/'Contents/Info.plist').read_bytes())
 if info.get('CFBundleIdentifier')!='dev.herdr.app' or info.get('CFBundleShortVersionString')!='0.1.16':raise RuntimeError('此工具僅支援 Herdr App（macOS 桌面版）0.1.16，其他版本不會套用。')
 return (app/BINARY).read_bytes()

def running(app):
 # Inspect the kernel executable path as well as argv: aliases and symlinked
 # command-line launchers must not hide a running instance from the installer.
 executable=str((app/BINARY).resolve())
 result=subprocess.run(['/bin/ps','-axo','pid=,command='],capture_output=True,text=True,check=True)
 proc=ctypes.CDLL('/usr/lib/libproc.dylib')
 proc.proc_pidpath.argtypes=[ctypes.c_int,ctypes.c_void_p,ctypes.c_uint32]
 proc.proc_pidpath.restype=ctypes.c_int
 for line in result.stdout.splitlines():
  words=line.strip().split(None,1)
  if not words:continue
  pid=int(words[0]);buf=ctypes.create_string_buffer(4096)
  count=proc.proc_pidpath(pid,buf,len(buf))
  if count>0 and os.fsdecode(buf.value)==executable:return True
  if len(words)>1 and words[1].startswith(executable):return True
 return False

def entitlements(binary):
 at=32
 for _ in range(struct.unpack_from('<I',binary,16)[0]):
  cmd,size=struct.unpack_from('<II',binary,at)
  if cmd==0x1d:
   off,length=struct.unpack_from('<II',binary,at+8)
   magic,total,count=struct.unpack_from('>III',binary,off)
   if magic!=0xfade0cc0:break
   for i in range(count):
    kind,rel=struct.unpack_from('>II',binary,off+12+i*8)
    if kind==5:
     blob_magic,blob_len=struct.unpack_from('>II',binary,off+rel)
     assert blob_magic==0xfade7171
     return plistlib.loads(binary[off+rel+8:off+rel+blob_len])
  at+=size
 raise RuntimeError('無法讀取原版 App 權限設定，未簽署或安裝。')

def patch_bytes(binary):
 d=payload()
 if sha(binary)!=EXPECTED:raise RuntimeError('執行檔指紋不符，可能已更新或修改；沒有套用任何修補。')
 out=bytearray(binary);end=0
 for p in sorted(d['patches'],key=lambda v:v['offset']):
  off,n=p['offset'],p['length'];new=base64.b64decode(p['data'],validate=True)
  if off<end or off+n>len(binary) or len(new)!=n or sha(binary[off:off+n])!=p['original_sha256']:raise RuntimeError('中文化資料驗證失敗。')
  out[off:off+n]=new;end=off+n
 if sha(out)!=d['unsigned_patched_sha256']:raise RuntimeError('中文化成品驗證失敗。')
 return out

def inventory(app):
 result={}
 for p in app.rglob('*'):
  if p.is_symlink():raise RuntimeError('App 含有未預期的符號連結。')
  if p.is_file():result[str(p.relative_to(app))]=sha(p.read_bytes())
 return result

def prepare(source,destination):
 original=require_app(source);modified=patch_bytes(original)
 if destination.exists():raise RuntimeError('暫存 App 已存在，為避免覆蓋而停止：'+str(destination))
 destination.parent.mkdir(parents=True,exist_ok=True)
 shutil.copytree(source,destination,copy_function=shutil.copy2)
 try:
  (destination/BINARY).write_bytes(modified)
  info_path=destination/'Contents/Info.plist';info=plistlib.loads(info_path.read_bytes())
  info['CFBundleDevelopmentRegion']='zh-Hant';info['CFBundleLocalizations']=['zh-Hant']
  info_path.write_bytes(plistlib.dumps(info))
  locale=destination/'Contents/Resources/zh-Hant.lproj';locale.mkdir()
  (locale/'InfoPlist.strings').write_bytes(plistlib.dumps({
   'NSAppleEventsUsageDescription':'在 Herdr 裡執行的終端機程式可透過 AppleScript 控制其他應用程式。',
   'NSCameraUsageDescription':'在 Herdr 裡執行的終端機程式可以使用相機。',
   'NSMicrophoneUsageDescription':'在 Herdr 裡執行的終端機程式可以使用麥克風（例如用於語音輸入）。'
  }))
  ent_file=destination.parent/'原版權限.plist';ent_file.write_bytes(plistlib.dumps(entitlements(original)))
  temp=ROOT/'work/tmp';temp.mkdir(parents=True,exist_ok=True)
  env={**os.environ,'TMPDIR':str(temp)+'/' ,'CODESIGN_ALLOCATE':'/usr/bin/codesign_allocate'}
  result=subprocess.run(['/usr/bin/codesign','--force','--sign','-','--timestamp=none','--options','runtime','--entitlements',str(ent_file),'--generate-entitlement-der',str(destination)],env=env,capture_output=True,text=True)
  if result.returncode:raise RuntimeError('本機簽署失敗：'+result.stderr.strip())
  result=subprocess.run(['/usr/bin/codesign','--verify','--deep','--strict',str(destination)],env=env,capture_output=True,text=True)
  if result.returncode:raise RuntimeError('簽章驗證失敗：'+result.stderr.strip())
  ent_file.unlink()
 except BaseException:
  shutil.rmtree(destination)
  raise
 return sha((destination/BINARY).read_bytes())

def find_app():
 candidates=[Path('/Applications/Herdr.app'),Path.home()/'Applications/Herdr.app']
 found=[p for p in candidates if p.is_dir()]
 if len(found)!=1:raise RuntimeError('找不到唯一的 Herdr.app，請先確認安裝位置。')
 return found[0]

def select_default_layout():
 # Public release: do not read or change personal Herdr configuration.
 return None

def install():
 app=find_app();original=require_app(app)
 if STATE.exists():
  state=json.loads(STATE.read_text())
  if state.get('status')=='installed' and str(app)==state['app'] and sha(original)==state['patched_sha256']:
   if state.get('package_revision')==package_revision():
    print('這份 Herdr 已套用目前這版繁體中文。');return
   raise RuntimeError('目前安裝的是較早的中文化。請先雙擊「還原英文版.command」，再雙擊「一鍵安裝繁體中文.command」套用新版文案。')
 if running(app):raise RuntimeError('請先用 ⌘Q 結束 Herdr，再雙擊安裝。工具不會關閉你的程式或終端機。')
 patch_bytes(original) # fail before creating any backup or staging
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
 if not os.access(app.parent,os.W_OK) or not os.access(ROOT,os.W_OK):raise RuntimeError('沒有寫入 App 或工具資料夾的權限，未執行置換。請使用有權限的本機帳號。')
 stage_parent=ROOT/'work'/('install-'+stamp);stage=stage_parent/'Herdr.app'
 app_parent=app.parent.resolve()
 if os.stat(ROOT).st_dev!=os.stat(app_parent).st_dev:raise RuntimeError('專案與 App 不在同一磁碟，未執行置換。')
 try:signed_hash=prepare(app,stage)
 except BaseException:
  if stage_parent.exists():shutil.rmtree(stage_parent)
  raise
 backup_parent=ROOT/'backups'/stamp;backup_parent.mkdir(parents=True)
 backup=backup_parent/'Herdr.app';before=inventory(app)
 record={'status':'prepared','package_revision':package_revision(),'app':str(app),'backup':str(backup),'original_sha256':EXPECTED,'patched_sha256':signed_hash,'files':before,'layout_change':None,'created':datetime.datetime.now().astimezone().isoformat()}
 save_json(backup_parent/'manifest.json',record)
 # Recheck just before the swap; there is never a running-app overwrite.
 if running(app) or sha((app/BINARY).read_bytes())!=EXPECTED:
  shutil.rmtree(stage_parent);shutil.rmtree(backup_parent)
  raise RuntimeError('Herdr 狀態已改變，未安裝。請稍後重試。')
 moved=False;installed=False;prior_state=STATE.read_bytes() if STATE.exists() else None
 try:
  os.rename(app,backup);moved=True
  if inventory(backup)!=before:raise RuntimeError('原版備份驗證失敗。')
  os.rename(stage,app);installed=True
  record['layout_change']=select_default_layout()
  record['status']='installed';save_json(STATE,record);save_json(backup_parent/'manifest.json',record)
 except BaseException:
  # Roll back the app first, even when a config/record write has failed.
  if installed:os.rename(app,stage)
  if moved:os.rename(backup,app)
  if prior_state is None:
   if STATE.exists():STATE.unlink()
  else:save_json(STATE,json.loads(prior_state))
  change=record.get('layout_change')
  if change:
   config=Path(change['path']);data=json.loads(config.read_text())
   if data.get('layout')==change['after']:data['layout']=change['before'];save_json(config,data)
  raise
 finally:
  if stage_parent.exists():shutil.rmtree(stage_parent)
 print('已套用繁體中文。請正常開啟 Herdr。\n原版備份：'+str(backup)+'\n要還原時，雙擊「還原英文版.command」。')

def restore():
 if not STATE.exists():raise RuntimeError('沒有本工具的安裝紀錄，未改動 App。')
 state=json.loads(STATE.read_text())
 if state['status']=='restored':print('已經還原英文版。');return
 app=Path(state['app']);backup=Path(state['backup'])
 if backup.resolve().parent.parent!= (ROOT/'backups').resolve():raise RuntimeError('備份位置驗證失敗。')
 if running(app):raise RuntimeError('請先用 ⌘Q 結束 Herdr，再雙擊還原。')
 if inventory(backup)!=state['files']:raise RuntimeError('原版備份指紋不符，未還原。')
 if not app.exists() or sha((app/BINARY).read_bytes())!=state['patched_sha256']:raise RuntimeError('目前 App 已更新或變更，為避免覆蓋而停止還原。')
 temp=ROOT/'work'/('removed-'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.app')
 # Preflight config reads before moving either App. Never overwrite later
 # unrelated settings: restore just the single layout key changed by us.
 config=None;before_config=None;after_config=None
 change=state.get('layout_change')
 if change:
  candidate=Path(change['path'])
  if candidate.exists() and not candidate.is_symlink():
   before_config=json.loads(candidate.read_text())
   if before_config.get('layout')==change['after']:
    config=candidate;after_config={**before_config,'layout':change['before']}
 temp.parent.mkdir(parents=True,exist_ok=True)
 os.rename(app,temp);moved=False;layout_written=False
 try:
  os.rename(backup,app);moved=True
  if config is not None:save_json(config,after_config);layout_written=True
  state['status']='restored';save_json(STATE,state)
 except BaseException:
  if moved:os.rename(app,backup)
  os.rename(temp,app)
  if layout_written:save_json(config,before_config)
  raise
 try:shutil.rmtree(temp)
 except OSError:print('英文版已還原，但未能清理測試副本：'+str(temp))
 print('已還原原版英文 Herdr。')

def main():
 if platform.system()!='Darwin' or platform.machine() not in ('arm64','aarch64'):raise RuntimeError('僅支援 Apple Silicon Mac。')
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','restore','check']);args=parser.parse_args()
 if args.action=='install':install()
 elif args.action=='restore':restore()
 elif args.action=='check':
  app=find_app();binary=require_app(app);patch_bytes(binary);print('版本與 SHA-256 符合：Herdr App 0.1.16（macOS Apple Silicon 桌面版）。可套用。')

if __name__=='__main__':
 try:main()
 except Exception as e:
  print('未完成：'+str(e),file=sys.stderr);sys.exit(1)
