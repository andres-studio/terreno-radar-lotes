#!/usr/bin/env python3
"""Public-source monitor. No cookies, logins, guessed prices or stale-date refreshes."""
import argparse, datetime as dt, hashlib, json, re, time, unicodedata
import urllib.request, urllib.parse, urllib.robotparser, urllib.error, xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
UA='TerrenoRadar/1.0 (+public listing research; no login)'

def normalized(s):
    return ''.join(c for c in unicodedata.normalize('NFD',str(s)) if unicodedata.category(c)!='Mn').lower().strip()

def canonical(url):
    u=urllib.parse.urlsplit(url)
    if u.scheme!='https' or not u.hostname or u.username or u.password: raise ValueError('Only public HTTPS sources')
    # Refuse loopback/private literal addresses, including imported source configuration.
    import ipaddress, socket
    for addr in socket.getaddrinfo(u.hostname,u.port or 443):
        if not ipaddress.ip_address(addr[4][0]).is_global: raise ValueError('Non-public address')
    q=urllib.parse.urlencode([(k,v) for k,v in urllib.parse.parse_qsl(u.query) if not k.lower().startswith('utm_') and k.lower() not in ('fbclid','gclid')])
    return urllib.parse.urlunsplit((u.scheme,u.netloc,u.path.rstrip('/') or '/',q,''))

class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        canonical(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)
OPENER=urllib.request.build_opener(PublicRedirect())

def request(url,limit=3000000):
    canonical(url)
    with OPENER.open(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=25) as r:
        if r.status!=200: raise ValueError('HTTP '+str(r.status))
        b=r.read(limit+1)
        if len(b)>limit: raise ValueError('Response too large')
        return b.decode(r.headers.get_content_charset() or 'utf-8',errors='replace')

robots={}
def allowed(url):
    origin='{0.scheme}://{0.netloc}'.format(urllib.parse.urlsplit(url))
    if origin not in robots:
        rp=urllib.robotparser.RobotFileParser()
        try: rp.parse(request(origin+'/robots.txt',250000).splitlines())
        except urllib.error.HTTPError as e:
            if e.code==404:rp.parse([])
            else:raise ValueError('robots.txt HTTP '+str(e.code)+'; skipped') from e
        except Exception as e: raise ValueError('robots.txt unavailable; skipped') from e
        robots[origin]=rp
    return robots[origin].can_fetch(UA,url)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ld=[]; self.in_ld=False; self.buf=''; self.text=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script': self.skip+=1; self.in_ld=a.get('type','').lower()=='application/ld+json';self.buf=''
        if tag=='style': self.skip+=1
    def handle_endtag(self,tag):
        if tag=='script':
            if self.in_ld:
                try:self.ld.append(json.loads(self.buf))
                except (ValueError,TypeError):pass
            self.in_ld=False;self.skip=max(0,self.skip-1)
        if tag=='style':self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if self.in_ld:self.buf+=data
        if not self.skip:self.text.append(data)

def objects(value):
    if isinstance(value,dict):
        yield value
        for k in ('@graph','mainEntity','itemListElement','item','about'):
            if k in value:yield from objects(value[k])
    elif isinstance(value,list):
        for v in value:yield from objects(v)

def positive(value):
    try:
        # JSON-LD expects a machine-readable decimal; never strip a decimal blindly.
        x=float(str(value).replace(',',''))
        return x if 0<x<1e15 else None
    except (ValueError,TypeError):return None

def structured(page,city,department):
    for root in page.ld:
        for item in objects(root):
            title=str(item.get('name',''))
            if not any(w in normalized(title) for w in ('lote','terreno','parcela')):continue
            address=item.get('address') or {}
            text=normalized(json.dumps([title,address,item.get('description','')],ensure_ascii=False))
            if normalized(city) not in text:continue
            if isinstance(address,dict) and address.get('addressRegion') and normalized(department) not in normalized(address['addressRegion']):continue
            offer=item.get('offers',{})
            if isinstance(offer,list):offer=next((o for o in offer if isinstance(o,dict)),{})
            if not isinstance(offer,dict):continue
            price=positive(offer.get('price'))
            if not price or offer.get('priceCurrency')!='COP':continue
            size=item.get('floorSize') or item.get('landArea') or {}
            area=None
            if isinstance(size,dict) and normalized(size.get('unitCode') or size.get('unitText')) in ('mtk','m2','m²','sqm','square meter','square metre'):
                area=positive(size.get('value'))
            return dict(title=title[:160],price=price,area=area,description='Datos del anuncio público. Consulta la fuente para la descripción completa; documentos pendientes.',sector=address.get('streetAddress','') if isinstance(address,dict) else '',kind='listing')
    return None

def extract(html,source):
    p=Page();p.feed(html)
    record=structured(p,source['city'],source['department'])
    if record:return record
    # A bounded, explicit parser for the pilot's original property page.
    text=' '.join(p.text)
    if source.get('parser')=='doomos' and normalized(source['city']) in normalized(text):
        price=re.search(r'\$\s*([0-9]{1,3}(?:\.[0-9]{3}){2,})',text)
        area=re.search(r'Área total\s*([\d.,]+)\s*m[²2]',text,re.I)
        if price and area:
            a=positive(area.group(1).replace('.','').replace(',','.'))
            return dict(title=source['title'],price=int(price.group(1).replace('.','')),area=a,sector=source.get('sector',''),description='Información extraída del anuncio. Área, títulos y disponibilidad pendientes de verificación.',kind='listing')
    if source.get('parser')=='wasi' and normalized(source['city']) in normalized(text):
        price=re.search(r'Precio de venta\s*\$\s*([0-9]{1,3}(?:\.[0-9]{3}){2,})',text,re.I)
        area=re.search(r'Área Terreno\s*:\s*([\d.,]+)\s*m[²2]',text,re.I)
        if price and area:
            return dict(title=source['title'],price=int(price.group(1).replace('.','')),area=positive(area.group(1).replace('.','').replace(',','.')),sector=source.get('sector',''),description='Datos publicados por el anunciante; documentos y disponibilidad pendientes de verificación.',kind='listing')
    if source.get('parser')=='espaciourbano' and normalized(source['city']) in normalized(text):
        # Read labeled headline fields, never prices or areas from related adverts.
        price=re.search(r'EN VENTA\s*\$\s*([0-9]{1,3}(?:,[0-9]{3}){2,})',text,re.I)
        area=re.search(r'Area total\s*([0-9,]+(?:\.[0-9]+)?)\s*M2',text,re.I)
        code=re.search(r'Código\s*([0-9]+)',text,re.I)
        expected=urllib.parse.parse_qs(urllib.parse.urlsplit(source['url']).query).get('xId',[None])[0]
        if price and area and code and code.group(1)==expected:
            return dict(title=source['title'],price=int(price.group(1).replace(',','')),area=positive(area.group(1)),sector=source.get('sector',''),kind=source.get('kind','listing'))
    if source.get('parser')=='ciencuadras' and normalized(source['city']) in normalized(text):
        price=re.search(r'Valor de compra\s*:\s*\$\s*([0-9]{1,3}(?:,[0-9]{3}){2,})',text,re.I)
        area=re.search(r'(?:Área lote|Área privada)\s*:\s*([\d,.]+)\s*m',text,re.I)
        if price and area:
            return dict(title=source['title'],price=int(price.group(1).replace(',','')),area=positive(area.group(1)),sector=source.get('sector',''),kind='listing')
    if source.get('parser')=='monte-horeb':
        # Independent lower bounds for a project; never divide them to infer $/m².
        m=re.search(r'áreas desde\s*([\d.]+)\s*m²\s*y\s*precios publicados desde\s*\$\s*([\d.,]+)\s*millones',text,re.I)
        if m and normalized(source['city']) in normalized(text):
            return dict(title=source['title'],price=int(float(m.group(2).replace(',','.'))*1000000),area=int(m.group(1).replace('.','')),price_from=True,area_from=True,sector='Sector por confirmar',description='Proyecto de varios lotes. Precio y área son mínimos independientes; no representan un mismo lote ni un precio por m².',kind='project')
    raise ValueError('No unambiguous COP listing data; retained as candidate')

def merge(old,record,now):
    result={**old,**record,'observed_at':now,'last_attempt_at':now,'last_check_status':'ok','status':'observed'}
    history=list(old.get('history',[]))
    snapshot={k:record.get(k) for k in ('price','area')};snapshot.update({k:bool(record.get(k)) for k in ('price_from','area_from')})
    if not history or any((bool(history[-1].get(k)) if k in ('price_from','area_from') else history[-1].get(k))!=v for k,v in snapshot.items()):history.append({'at':now,**snapshot})
    result['history']=history
    result['first_seen_at']=old.get('first_seen_at',old.get('observed_at',now))
    result['observation_method']='direct_public_page'
    result['source_cache_note']=None
    result.setdefault('consultations',[]).append({'at':now,'method':'direct_public_page','price':record.get('price'),'area':record.get('area')})
    result['consultations']=result['consultations'][-120:]
    return result

def discover(city,department):
    query=f'lotes venta "{city}" "{department}"'
    url='https://www.bing.com/search?format=rss&q='+urllib.parse.quote(query)
    if not allowed(url):raise ValueError('Discovery disabled by robots.txt')
    root=ET.fromstring(request(url))
    out=[]
    for e in root.findall('.//item')[:15]:
        title=e.findtext('title') or '';link=e.findtext('link') or '';desc=e.findtext('description') or ''
        if normalized(city) not in normalized(title+' '+desc):continue
        if not any(t in normalized(title) for t in ('lote','terreno','parcela')):continue
        try:link=canonical(link)
        except Exception:continue
        out.append(dict(url=link,title=title[:160],city=city,department=department,source=urllib.parse.urlsplit(link).hostname,parser='jsonld'))
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--municipio',default='Jardín');ap.add_argument('--departamento',default='Antioquia');ap.add_argument('--discover',action='store_true');ap.add_argument('--all',action='store_true');args=ap.parse_args()
    path=ROOT/'dist/data/catalog.json';catalog=json.loads(path.read_text());sources=json.loads((ROOT/'sources.json').read_text());now=dt.datetime.now(dt.timezone.utc).isoformat();results=[];candidates=[]
    if args.all:
        import subprocess, sys
        catalog_now=json.loads((ROOT/'dist/data/catalog.json').read_text())
        territories={(s['city'],s['department']) for s in sources+catalog_now['listings']}
        territories|={(r['city'],r['department']) for r in catalog_now.get('runs',[])}
        for city,department in sorted(territories):
            subprocess.run([sys.executable,__file__,'--municipio',city,'--departamento',department,'--discover'],check=True)
        return
    if args.discover:
        try:candidates=discover(args.municipio,args.departamento)
        except Exception as e:results.append({'source':'Bing RSS discovery','status':'error','reason':str(e)[:180]})
    selected=[s for s in sources if normalized(s['city'])==normalized(args.municipio) and normalized(s['department'])==normalized(args.departamento)]
    selected+=candidates
    by_url={x['url']:x for x in catalog['listings']};seen=set()
    for s in selected[:40]:
        url=s['url']
        if url in seen:continue
        seen.add(url);old=by_url.get(url)
        if s.get('mode')=='manual':
            results.append({'source':s['source'],'url':url,'status':'manual','reason':'Manual review required; prior observation retained'})
            continue
        try:
            if not allowed(url):raise ValueError('Blocked by robots.txt; skipped')
            html=request(url);record=extract(html,s)
            for key in ('includes_building','price_from','area_from','kind','advertiser_id','advertiser'):
                if key in s:record[key]=s[key]
            record.update(url=url,city=s['city'],department=s['department'],source=s['source'],id=old['id'] if old else hashlib.sha256(url.encode()).hexdigest()[:14])
            by_url[url]=merge(old or {},record,now)
            results.append({'source':s['source'],'url':url,'status':'ok'})
        except Exception as e:
            results.append({'source':s['source'],'url':url,'status':'error','reason':str(e)[:180]})
            if old:by_url[url]={**old,'last_attempt_at':now,'last_check_status':'error'}
        time.sleep(1)
    catalog['listings']=list(by_url.values());catalog.setdefault('runs',[]).append({'finished_at':now,'city':args.municipio,'department':args.departamento,'ok':sum(r['status']=='ok' for r in results),'errors':sum(r['status']=='error' for r in results),'details':results})
    catalog['runs']=catalog['runs'][-60:]
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
    (ROOT/'dist/data/candidates.json').write_text(json.dumps({'checked_at':now,'city':args.municipio,'candidates':candidates},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'ok':catalog['runs'][-1]['ok'],'errors':catalog['runs'][-1]['errors'],'listings':len(by_url)}))
if __name__=='__main__':main()
