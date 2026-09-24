import hashlib
import json
import pytest
from annotation_report import load_closure

def test_closure_rejects_modified_evidence(tmp_path):
    files={'adjudicacion_E3.json':'{}','piloto_categorias_finales.jsonl':json.dumps({'id_comentario':'one','categoria_final':'Neutro'})+'\n'}
    for name,text in files.items(): (tmp_path/name).write_text(text,encoding='utf-8')
    manifest={'n':1,'distribucion':{'Neutro':1},'archivos_sha256':{n:hashlib.sha256((tmp_path/n).read_bytes()).hexdigest() for n in files}}
    (tmp_path/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    assert len(load_closure(tmp_path)[2])==1
    (tmp_path/'piloto_categorias_finales.jsonl').write_text('{}',encoding='utf-8')
    with pytest.raises(ValueError,match='hash'):load_closure(tmp_path)
