"""La regola del crollo regge in periodi diversi, o e' un fenomeno recente?

14 mercati su 19 positivi sembra molto, ma le materie prime si muovono insieme:
petrolio, benzina e gasolio sono quasi lo stesso mercato. Quindi il conteggio
e' ottimistico. Un controllo che NON dipende dalla correlazione fra mercati:
lo stesso effetto nella prima meta' del tempo e nella seconda.
Se c'e' solo di recente, e' un fenomeno, non una proprieta'.
"""
import json, glob, os, statistics as st, random
random.seed(17); COSTO=0.0005
NOMI={"GC_F":"oro","HG_F":"rame","SI_F":"argento","PL_F":"platino","PA_F":"palladio",
      "ALI_F":"alluminio","CL_F":"petrolio","NG_F":"gas","HO_F":"gasolio","RB_F":"benzina",
      "ZW_F":"grano","ZC_F":"mais","ZS_F":"soia","CT_F":"cotone","SB_F":"zucchero",
      "KC_F":"caffe","CC_F":"cacao","LE_F":"bovini","EURUSD_X":"EUR/USD"}
fn=lambda c,h,l,i: c[i]<min(l[i-24:i])
def diff(c,h,l,da,a,o):
    idx=[i for i in range(da+100,a-o-1) if fn(c,h,l,i)]
    v=[(c[i+o]/c[i]-1)-COSTO for i in idx]
    if len(v)<25: return None
    sp=range(da+100,a-o-1)
    casi=[(c[i+o]/c[i]-1)-COSTO for i in random.sample(list(sp), min(2000,len(list(sp))))]
    return st.mean(v)-st.mean(casi), len(v)
for o in (6,24):
    print(f"\n   orizzonte {o} giorni")
    print("   mercato        prima meta' del tempo   seconda meta'")
    A=[];B=[]
    for f in sorted(glob.glob("data/mercati/*_1d.json")):
        base=os.path.basename(f).replace("_1d.json","")
        D=json.load(open(f))
        c=[x for x in D["c"] if x]; h=[x for x in D["h"] if x]; l=[x for x in D["l"] if x]
        n=min(len(c),len(h),len(l)); c,h,l=c[:n],h[:n],l[:n]
        if n<900: continue
        a=diff(c,h,l,0,n//2,o); b=diff(c,h,l,n//2,n,o)
        if not a or not b: continue
        A.append(a[0]*100); B.append(b[0]*100)
        print(f"   {NOMI.get(base,base):<13} {a[0]*100:+8.3f}% (n={a[1]:>3})      {b[0]*100:+8.3f}% (n={b[1]:>3})")
    if A:
        print(f"   {'MEDIA':<13} {st.mean(A):+8.3f}%              {st.mean(B):+8.3f}%")
        print(f"   {'positivi':<13} {sum(1 for x in A if x>0)}/{len(A)}                   {sum(1 for x in B if x>0)}/{len(B)}")
        print("   -> " + ("regge in ENTRAMBI i periodi" if st.mean(A)>0 and st.mean(B)>0
              else "NON regge: e' un fenomeno di un periodo, non una proprieta'"))
