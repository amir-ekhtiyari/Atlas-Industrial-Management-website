import ast, struct, sys
def unq(s): return ast.literal_eval(s)
def parse(path):
    msgs={}; cur=None; key=None; fuzzy=False
    def flush():
        nonlocal cur
        if cur and 'msgid' in cur and not cur.get('fuzzy'):
            mid=cur['msgid']
            if 'msgctxt' in cur: mid=cur['msgctxt']+'\x04'+mid
            if 'msgid_plural' in cur:
                mid=mid+'\x00'+cur['msgid_plural']
                strs=[cur[k] for k in sorted(k for k in cur if k.startswith('msgstr['))]
                val='\x00'.join(strs)
            else: val=cur.get('msgstr','')
            if val or mid=='': 
                if all(val.split('\x00')) or mid=='': msgs[mid]=val
        cur=None
    for line in open(path,encoding='utf-8'):
        line=line.rstrip('\r\n')
        if line.startswith('#~') : continue
        if line.startswith('#,') and 'fuzzy' in line:
            flush(); cur={'fuzzy':True}; continue
        if line.startswith('#') or not line.strip():
            if not line.strip(): flush()
            continue
        if line.startswith('"'):
            cur[key]+=unq(line); continue
        k,rest=line.split(' ',1)
        if k in('msgid','msgctxt') and cur and ('msgstr' in cur or any(x.startswith('msgstr[') for x in cur)): flush()
        if cur is None: cur={}
        if k=='msgid' and 'msgctxt' not in cur and 'msgid' in cur: flush(); cur={}
        key=k; cur[k]=unq(rest)
    flush(); return msgs
def write(msgs,out):
    keys=sorted(msgs)
    ids=b''; strs=b''; offs=[]
    for k in keys:
        kb=k.encode(); vb=msgs[k].encode()
        offs.append((len(ids),len(kb),len(strs),len(vb)))
        ids+=kb+b'\0'; strs+=vb+b'\0'
    n=len(keys); ko=28; vo=ko+n*8; ids_start=vo+n*8; strs_start=ids_start+len(ids)
    out_b=struct.pack('Iiiiiii',0x950412de,0,n,ko,vo,0,0)
    for o in offs: out_b+=struct.pack('ii',o[1],o[0]+ids_start)
    for o in offs: out_b+=struct.pack('ii',o[3],o[2]+strs_start)
    open(out,'wb').write(out_b+ids+strs)
m=parse(sys.argv[1]); write(m,sys.argv[2]); print(len(m))
