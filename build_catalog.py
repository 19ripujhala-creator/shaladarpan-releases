"""Publish download metadata only. This is not Shaladarpan application source."""
import json,os,re,urllib.request
from pathlib import Path
repo=os.environ.get('GITHUB_REPOSITORY','19ripujhala-creator/shaladarpan-releases')
names={'android':['Shaladarpan-Android.apk','Shaladarpan.apk'],'ios':['Shaladarpan-iOS.ipa','Shaladarpan.ipa'],'windows':['Shaladarpan-Windows.zip','Shaladarpan-Windows.exe']}
def catalog(releases):
 result={};versions={}
 for r in releases:
  if r.get('draft') is not False or r.get('prerelease') is not False:continue
  version=str(r.get('tag_name','')).removeprefix('v')
  if not re.fullmatch(r'\d{1,6}(\.\d{1,6}){1,3}',version):continue
  number=tuple((list(map(int,version.split('.')))+[0]*4)[:4])
  for platform,accepted in names.items():
   if platform in versions and versions[platform]>=number:continue
   asset=next((a for name in accepted for a in r.get('assets',[]) if a.get('name')==name and a.get('state')=='uploaded' and a.get('size',0)>0 and str(a.get('browser_download_url','')).startswith('https://github.com/'+repo+'/releases/download/')),None)
   if asset:
    versions[platform]=number
    result[platform]={'version':version,'url':asset['browser_download_url'],'notes':str(r.get('body') or '')[:4000]}
 return {'schema':1,'releases':result}
if __name__=='__main__':
 token=os.environ['GH_TOKEN']
 request=urllib.request.Request('https://api.github.com/repos/'+repo+'/releases?per_page=100',headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'Shaladarpan-release-catalog'})
 with urllib.request.urlopen(request,timeout=30) as response:releases=json.load(response)
 Path('releases.json').write_text(json.dumps(catalog(releases),indent=2)+'\n',encoding='utf-8')
