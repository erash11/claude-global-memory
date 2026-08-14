import sys, zipfile
from xml.etree import ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def ptext(p):
    return ''.join(t.text or '' for t in p.iter(W+'t'))
def style(p):
    s=p.find(W+'pPr/'+W+'pStyle')
    return s.get(W+'val') if s is not None else ''
def walk(el, out, depth=0):
    for child in el:
        if child.tag==W+'p':
            txt=ptext(child).strip()
            st=style(child)
            if txt:
                out.append(f"{'  '*depth}[{st}] {txt}" if st else f"{'  '*depth}{txt}")
        elif child.tag==W+'tbl':
            out.append(f"{'  '*depth}<<TABLE>>")
            for row in child.findall(W+'tr'):
                cells=[]
                for tc in row.findall(W+'tc'):
                    cells.append(' / '.join(ptext(p).strip() for p in tc.iter(W+'p') if ptext(p).strip()))
                out.append(f"{'  '*depth}| " + " || ".join(cells))
            out.append(f"{'  '*depth}<</TABLE>>")
        elif child.tag==W+'sdt' or child.tag==W+'body':
            walk(child,out,depth)
        else:
            walk(child,out,depth)
z=zipfile.ZipFile(sys.argv[1])
root=ET.fromstring(z.read('word/document.xml'))
out=[]
walk(root.find(W+'body'),out)
print('\n'.join(out))
