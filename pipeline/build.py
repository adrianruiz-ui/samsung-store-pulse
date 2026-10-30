"""Reconstruye data.json a partir de las reseñas crudas exportadas del navegador.
Uso: python pipeline/build.py ruta/a/samsung_resenas_AAAA-MM-DD.json [--out data.json]
"""
import json, re, os, sys, math, unicodedata, gzip, datetime
import numpy as np, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__))
def norm(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
TOP={
 'Atención y trato': r'servicio(?! tecnico)|atencion|atendi|amable|trato|asesor|asesoria|asesoro|actitud|grosero|groser|prepotent|servicial|educad|paciencia|paciente|explic|orient|ayud|apoy|resolvi|dudas|personal|vendedor|ejecutiv|chica|chico|joven|senorita|muchach',
 'Servicio técnico y reparación': r'reparac|reparar|repar|servicio tecnico|tecnico|pantalla|bateria|diagnost|refacci|pieza|display|centro de servicio|revision|falla|fallo|se apag|no prende|no enciende|mojad|camara|puerto|carga|actualiz|software|formate|soporte',
 'Garantía y políticas': r'garantia|carta factura|factura|comprobante|ticket|poliza|no procede|no aplica|politica|requisito',
 'Tiempos de espera': r'espera|esperar|esper|tarda|tardan|tardaron|tardo|horas|hora y|rapid|rapidez|agil|fila|turno|cita|demora|dias|semanas|lento|tiempo',
 'Precio, promociones y pago': r'precio|caro|barato|promoc|descuento|oferta|meses sin intereses|msi|costo|cobr|pago|pagar|tarjeta|financ|credito|bono|cupon|diferido',
 'Stock y disponibilidad': r'no tenian|no tienen|no habia|disponib|existencia|agotad|inventario|stock|apartad|pedido|surtir',
 'Producto y experiencia demo': r'probar|prueba|demostr|exhib|conocer|modelos|fold|flip|galaxy s|s2[0-9]|s1[0-9]|ultra|watch|reloj|tablet|tab s|buds|anillo|ring|equipo nuevo|celular nuevo|televis|pantalla grande|novedad',
 'Accesorios y micas': r'mica|funda|protector|cargador|accesorio|cable|templad',
 'Samsung Care+ y seguros': r'care|seguro|samsung care',
 'Galaxy Canje / trade-in': r'canje|trade|tomaron mi|recib(i|ieron) mi (equipo|celular)|dar a cuenta|a cuenta',
 'Configuración y datos': r'transfer|pasar (mis|la) informacion|datos|configur|smart switch|respaldo|contactos|whatsapp|instal',
 'Compra en línea y entregas': r'en linea|online|pagina|recoger|pick|envio|entrega|paqueteria|app|tienda en linea',
 'Tienda e instalaciones': r'instalacion|tienda (muy )?(bonita|limpia|amplia|grande|chica|pequena)|espacio|ubicacion|lugar|local|ambiente|limpi|ordenad',
}
TOPRE={k:re.compile(v) for k,v in TOP.items()}
NAMES=set(norm(x) for x in open(os.path.join(HERE,'names.txt')).read().split())
AMBIG={'luz','rosa','ale','angel','jesus','pilar','sara','eva','andy','lupita','isabel','gloria','regina','dulce','perla','martin','cesar','marco','victor','salvador','ruth','reyes'}
NAMES2=NAMES-AMBIG
CTX=re.compile(r'(?:(?:servicio|atencion|apoyo|ayuda|asesoria|trato)\s+(?:de|del|por parte de)\s+(?:(?:el|la|joven|senorita|srita|sr|sra|asesor|asesora|ing|lic)\.?\s+)?|(?:atendio|atendido por|atendida por|gracias a|felicito a|felicidades a|recomiendo a|pregunten por|pregunta por|el joven|la senorita|la srita|el asesor|la asesora|el tecnico|la tecnica)\s+(?:el\s+|la\s+)?)([a-z]{3,})')
STOP={'todo','todos','todas','los','las','calidad','excelente','muy','primera','parte','cliente','clientes','tienda','samsung','personal','equipo','ustedes','ellos','que','una','uno','del','con','mis','sus','buen','buena','gran','nada','esta','este','servicio','atencion','tecnico','tecnicos','ventas','venta','manera','forma','mucho','mucha','bien','otro','otra','alguien','nadie','ella','ellas','quien','nuestro','dicha','dicho','sucursal','staff','gente','chicos','chicas','jovenes','encargado','encargada','gerente','asesores','vendedores','mejor','buenisimo','ustedes','areas','area','cada','tal','primer'}
def staff_named(t):
    n=norm(t)
    toks=set(re.findall(r'[a-z]{3,}',n))
    if toks & NAMES2: return True
    return any(m.group(1) not in STOP for m in CTX.finditer(n))
def months(d):
    d=norm(d).replace('fecha de edicion: ','')
    m=re.search(r'hace (un|una|\d+) (dia|dias|semana|semanas|mes|meses|ano|anos)',d)
    if not m: return None
    n=1 if m.group(1) in('un','una') else int(m.group(1)); u=m.group(2)
    return n/30 if u.startswith('dia') else n/4.3 if u.startswith('sem') else n if u.startswith('mes') else n*12

import re
FR=re.compile(r"tard|lent[oa]|demor|esper[eéoa]|espera\b|falta|faltan|no ten[ií]an|no tuvieron|no encontr|no hab[ií]a|car[oa]s?\b|precio|poco amabl|groser|mala gana|\bmal[oa]?\b|no me gust|molest|calor|ruido|mus[ií]ca|no quedo|no se pudo|deberian|ojala|\bmeh\b|despot|burl|un tanto serio|no estoy|no contest|lamentabl|area de oportunidad|mejorar|surtido|variedad|disponibilidad|stock|no ayuda|mejor el servicio|sin embargo, con")
CON=re.compile(r"\bpero\b|sin embargo|aunque|lo malo|lo unico|solo que|\bsolo\b")
NEG=re.compile(r"pesim|horrib|terrib|peor|no sirv|grosero|prepot|decepcion|fraude|rater|nefast|no lo recomiendo|no recomiendo|no vuelvo|no regreso")
POS=re.compile(r"excelente|exelente|muy bien|buen[oa]?\b|amabl|atent|gracias|recomiend|rapid|eficien|genial|perfect|encant|satisfech|profesional|pacien|servicial|resolvi|solucion")
def sentiment(stars, text):
    n=norm(text or '')
    if not n.strip(): return 'Positivo' if stars>=4 else ('Negativo' if stars<=2 else 'Neutral')
    if stars>=4:
        if CON.search(n) and FR.search(n): return 'Mixto'
        if NEG.search(n): return 'Mixto'
        return 'Positivo'
    if stars<=2:
        if POS.search(n) and not NEG.search(n) and not FR.search(n) and len(n)<120: return 'Positivo'  # e.g. wrong-star praise
        if CON.search(n) and POS.search(n) and FR.search(n) and not NEG.search(n): return 'Mixto'
        return 'Negativo'
    if NEG.search(n): return 'Negativo'
    if POS.search(n) and not FR.search(n): return 'Positivo'
    if POS.search(n): return 'Mixto'
    return 'Negativo' if FR.search(n) else 'Mixto'

DEV=[
 ('Galaxy S26', r'\bs ?26\b'), ('Galaxy S25', r'\bs ?25\b'), ('Galaxy S24', r'\bs ?24\b'),
 ('Galaxy S (anteriores)', r'\bs(?:2[0-3]|1\d)\b|galaxy s ?(?:2[0-3]|1\d|9|8)\b|\bs ?2[0-3] (?:ultra|plus|fe)'),
 ('Z Fold', r'\bz? ?fold ?\d*'), ('Z Flip', r'\bz? ?flip ?\d*'),
 ('Galaxy A', r'\ba(?:0\d|1\d|2\d|3\d|5\d|7\d)\b|galaxy a ?\d\d'),
 ('Galaxy Tab', r'\btab\b|tablet|tableta'),
 ('Galaxy Watch', r'\bwatch\b|reloj|smartwatch'),
 ('Galaxy Buds', r'\bbuds\b|audifono'),
 ('Galaxy Ring', r'galaxy ring|\banillo\b'),
 ('TV y monitores', r'\btv\b|televis|pantalla de \d|smart tv|the frame|monitor|odyssey'),
 ('Línea blanca', r'refri|lavadora|secadora|aire acondicionado|microondas|aspiradora'),
 ('iPhone', r'iphone|\bapple\b|\bios\b'),
 ('Otras marcas', r'xiaomi|motorola|huawei|oppo|honor\b|pixel'),
]

DEVRE=[(k,re.compile(v)) for k,v in DEV]
def devices(n): return [k for k,rx in DEVRE if rx.search(n)]
def months2(d):
    x=norm((d or '').replace('\xa0',' ')).replace('fecha de edicion: ','')
    m=re.search(r'hace (un|una|\d+) (minuto|minutos|hora|horas|dia|dias|semana|semanas|mes|meses|ano|anos)',x)
    if not m: return np.nan
    n=1 if m.group(1) in('un','una') else int(m.group(1)); u=m.group(2)
    return 0.01 if u.startswith(('min','hor')) else n/30 if u.startswith('dia') else n/4.3 if u.startswith('sem') else n if u.startswith('mes') else n*12

def main(raw_path,out_path):
    RAW=json.load(open(raw_path))
    BASE=json.load(open(os.path.join(HERE,'stores.json')))
    CUR=json.load(open(os.path.join(HERE,'curated.json')))
    S=[dict(b) for b in BASE]; idx={s['id']:i for i,s in enumerate(S)}
    rawby={x['store']:x for x in RAW}
    for s in S:
        x=rawby.get(s['id'])
        if x and x.get('rating'): s['calif']=x['rating']
        if x and x.get('total'): s['resenas_maps']=x['total']
    rows=[dict(store=x['store'],**r) for x in RAW for r in x['reviews'] if x['store'] in idx]
    df=pd.DataFrame(rows)
    df['t']=df.t.fillna(''); df['n']=df.t.map(norm); df['has_text']=df.t.str.len()>0
    df['lg']=df.lg.astype(bool); df['resp']=df.resp.astype(bool)
    TOPK=list(TOP)
    for k,rx in TOPRE.items(): df[k]=df.n.map(lambda s:bool(rx.search(s)))
    df['ase']=df.t.map(staff_named)&df.has_text
    df['meses']=df.d.map(months2)
    df['dev']=df.n.map(devices)
    SC={'Positivo':0,'Mixto':1,'Negativo':2,'Neutral':3}
    df['sc']=[SC[sentiment(r,t)] if h else 3 for r,t,h in zip(df.r,df.t,df.has_text)]
    df['neg']=df.sc==2; df['fric']=df.sc==1
    t=df[df.has_text].copy(); W6=t[t.meses<=6]
    p6=W6.neg.mean(); pall=t.neg.mean()
    g=W6.groupby('store').agg(n=('neg','size'),k=('neg','sum'))
    m=g.k.sum()/g.n.sum(); v=np.var(g.k/g.n); mn=g.n.mean()
    phi=max(1e-4,(v-m*(1-m)/mn)/(m*(1-m))); ab=(1/phi-1) if phi<1 else 50; a0,b0=m*ab,(1-m)*ab
    t['mb']=t.meses.map(lambda x: int(min(11,math.floor(x))) if x==x and x<12 else None)
    TK=['atencion','tecnico','garantia','espera','precio','stock','producto','accesorios','care','canje','datos','online','tienda']
    for s in S:
        sub=t[t.store==s['id']]
        if not len(sub) or s['estatus']!='activa': continue
        vc=sub.sc.value_counts(); n=len(sub)
        s['sent']=[round(100*vc.get(i,0)/n,1) for i in range(3)]; s['ntxt']=n
        e=sub.explode('dev').dropna(subset=['dev']); s['dev']=[[k,int(c)] for k,c in e.dev.value_counts().head(4).items()]
        s['asesor']=round(100*sub.ase.mean(),1)
        ng=sub[sub.neg]; s['temas_neg']={TK[j]:int(ng[k].sum()) for j,k in enumerate(TOPK)}
        w=sub[sub.meses<=6]; n6=len(w); k6=int(w.neg.sum())
        s['n6']=n6; s['k6']=k6; s['neg6']=round(100*k6/n6,1) if n6 else None
        s['eb6']=round(100*(k6+a0)/(n6+a0+b0),1)
        if n6:
            z=(k6/n6-p6)/math.sqrt(p6*(1-p6)/n6); s['z6']=round(z,2)
            s['flag']='alto' if z>3.09 else ('alto?' if z>1.96 else ('bajo' if z<-1.96 else 'normal'))
        else: s['flag']='normal'; s['z6']=0
        lg=sub[sub.lg]; s['lg_neg']=round(100*lg.neg.mean(),1) if len(lg)>=15 else None
        s['mon']=[[int((sub.mb==i).sum()),int(((sub.mb==i)&sub.neg).sum())] for i in range(12)]
    K={}
    K['resenas']=int(len(df)); K['tiendas']=int(df.store.nunique()); K['con_texto']=int(len(t))
    K['p6']=round(100*p6,2); K['pall']=round(100*pall,2); K['n6']=int(len(W6))
    K['pct_asesor']=round(100*t.ase.mean(),1)
    pol=df[df.store=='SS069']; K['pct_resp_polanco']=round(100*pol.resp.mean(),1) if len(pol) else None
    crit=t[t.r<=3]; K['n_crit']=int(len(crit)); K['resp_crit']=round(100*(1-crit.resp.mean()),1)
    K['n_dev']=int(t.dev.map(bool).sum())
    K['lg']={lab:dict(pct5=round(100*(q.r==5).mean(),1),neg=round(100*q[q.has_text].neg.mean(),1)) for lab,q in [('lg',df[df.lg]),('nolg',df[~df.lg])]}
    K['lg_share']=round(100*df.lg.mean(),1); K['lg_stars']=round(df[df.lg].r.mean(),2); K['nolg_stars']=round(df[~df.lg].r.mean(),2)
    a=t.groupby('ase').neg.mean(); lq=t[t.lg]; la=lq.groupby('ase').neg.mean()
    K['asesor']=dict(neg_con=round(100*a.get(True,0),1),neg_sin=round(100*a.get(False,0),1),lg_con=round(100*la.get(True,0),1),lg_sin=round(100*la.get(False,0),1))
    def rr(mask):
        A=t[mask]; Bq=t[~mask]; k1,n1,k2,n2=int(A.neg.sum()),len(A),int(Bq.neg.sum()),len(Bq)
        if k1==0 or n1==0 or k2==0: return None
        r=(k1/n1)/(k2/n2); se=math.sqrt(1/k1-1/n1+1/k2-1/n2)
        return dict(n=int(n1),share=round(100*n1/len(t),2),k=k1,neg=round(100*k1/n1,1),rr=round(r,2),lo=round(r*math.exp(-1.96*se),2),hi=round(r*math.exp(1.96*se),2))
    DRV=[]
    for tp in TOPK:
        x=rr(t[tp].astype(bool))
        if x: x['tema']=tp; DRV.append(x)
    DEVK=[k for k,_ in DEV]; DEVS=[]
    for k in DEVK:
        mask=t.dev.map(lambda L:k in L)
        if mask.sum()<15: continue
        x=rr(mask)
        if not x: continue
        x['dev']=k; DEVS.append(x)
    fm=t.dev.map(lambda L:any(z.startswith('Z ') for z in L)); FOLD=rr(fm)
    DATA=t.n.str.contains(r'pas(?:ar|aron|o|e) (?:mi |la |toda |mis )?(?:informacion|datos|contactos|whats)|migra|traspas|smart switch|respaldo|configur')
    REPm=t['Servicio técnico y reparación'].astype(bool)
    def tmet(mask):
        q=t[mask]; n=len(q); rec=q[q.meses<=6]; old=q[q.meses>6]
        shr=len(rec)/max(1,(t.meses<=6).sum()); sho=len(old)/max(1,(t.meses>6).sum())
        st=q.groupby('store').size()
        return dict(n=int(n),share=round(100*n/len(t),1),neg=round(100*q.neg.mean(),1) if n else 0,pct5=round(100*(q.r==5).mean(),1) if n else 0,
                    stores=int((st>=3).sum()),trend=round(shr/sho,2) if sho else None,top=[[idx[s_],int(c)] for s_,c in st.sort_values(ascending=False).head(3).items()])
    TM={'asesor':tmet(t.ase),'datos':tmet(DATA),'reparacion':tmet(REPm),'plegables':tmet(fm)}
    for key,mask in [('reparacion',REPm),('plegables',fm)]:
        vv=t[mask&t.neg].store.value_counts().head(3); TM[key]['top_neg']=[[idx[s_],int(c)] for s_,c in vv.items()]
    g2=t.groupby('store').ase.agg(['mean','size']); g2=g2[g2['size']>=60].sort_values('mean',ascending=False).head(3)
    TM['asesor']['top']=[[idx[s_],round(100*v_)] for s_,v_ in g2['mean'].items()]
    def tmask(row): return sum(1<<j for j,k in enumerate(TOPK) if row[k])
    tm_=df[TOPK].values
    R=[]
    for i,r in enumerate(df.itertuples()):
        R.append([idx[r.store],int(r.r) if r.r==r.r else 0,None if r.meses!=r.meses else round(float(r.meses),2),r.d,r.t,
                  int(sum(1<<j for j,v_ in enumerate(tm_[i]) if v_)),int(r.ase),int(r.sc),int(sum(1<<DEVK.index(k) for k in r.dev)),int(r.lg),int(r.resp)])
    # competencia: curated groups + count of new mentions
    U=r'iphone|\bapple\b|xiaomi|motorola|huawei|telcel|liverpool|palacio|amazon|mercado ?libre|tienda (?:en )?linea|en linea'
    known=set(q[0] for g_ in CUR['comp'] for q in g_['rows'])
    newc=int(sum(1 for x in t[t.n.str.contains(U)].t if x not in known))
    corte=max(x.get('scraped','')[:10] for x in RAW)
    MES=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
    y,mo,d=corte.split('-'); K['corte']=corte
    out=dict(corte=f'{int(d)} {MES[int(mo)-1]} {y}',temas=TOPK,temas_k=TK,devk=DEVK,stores=S,reviews=R,kpis=K,drivers=DRV,devices=DEVS,fold=FOLD,tm=TM,
             val=CUR['val'],quotes=CUR['quotes'],comp=CUR['comp'],comp_total=CUR['comp_total'],comp_new=newc,prior=[a0,b0])
    json.dump(out,open(out_path,'w'),ensure_ascii=False,separators=(',',':'),default=lambda o:o.item() if hasattr(o,'item') else str(o))
    # keep a compressed snapshot for week-over-week comparisons
    hist=os.path.join(HERE,'history'); os.makedirs(hist,exist_ok=True)
    with gzip.open(os.path.join(hist,f'raw_{corte}.json.gz'),'wt',encoding='utf-8') as f: json.dump(RAW,f,ensure_ascii=False)
    print(f'OK {corte}: {K["resenas"]} reseñas, {K["tiendas"]} tiendas, críticas 6m {K["p6"]}%, fuera de rango {sum(1 for s in S if s.get("flag") in ("alto","alto?"))}, menciones de competencia nuevas sin clasificar {newc}')

if __name__=='__main__':
    a=sys.argv[1:]; out='data.json'
    if '--out' in a: i=a.index('--out'); out=a[i+1]; del a[i:i+2]
    main(a[0],out)
