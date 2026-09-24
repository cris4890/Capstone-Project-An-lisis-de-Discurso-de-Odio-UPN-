import copy
import hashlib
import json
import pytest
from doccano_import import validate

def sample():
    source=json.dumps({'id_comentario':'u1','text':'Texto sintético'})+'\n'
    return dict(schema=1,manifest=dict(version='test',n=1,projects={'a':3,'b':4},
                source_sha256=hashlib.sha256(source.encode()).hexdigest()),source_jsonl=source,
                records=[dict(evaluador=name,project_id=pid,id_comentario='u1',texto='Texto sintético',
                    etiquetas=['Neutro'],confirmado=True,comentarios=[dict(user=name,
                    text='Objetivo: No aplica\nJustificacion: Sin ataque.\nRegistro: redacción asistida\nMotivo original: original')])
                    for name,pid in [('a',3),('b',4)]])

def test_retains_assistance_without_training_or_premature_kappa():
    data=sample();before=copy.deepcopy(data);result=validate(data)
    assert data==before
    assert result['pares_validos']==1
    assert result['resumen']['a']['con_asistencia_declarada']==1
    assert result['registros'][0]['justificacion']=='Sin ataque.'
    assert result['kappa'] is None and not result['habilitado_para_entrenamiento']

@pytest.mark.parametrize('change,error',[
    ('duplicate','duplicado'),('hash','hash'),('text','texto'),('project','Proyecto')])
def test_rejects_mismatched_evidence(change,error):
    data=sample()
    if change=='duplicate':data['records'].append(copy.deepcopy(data['records'][0]))
    if change=='hash':data['source_jsonl']+=' '
    if change=='text':data['records'][0]['texto']='Otra unidad'
    if change=='project':data['records'][0]['project_id']=999
    with pytest.raises(ValueError,match=error):validate(data)

def test_missing_b_and_unresolved_target_excluded():
    data=sample();data['records']=data['records'][:1]
    data['records'][0]['etiquetas']=['Odio']
    data['records'][0]['comentarios'][0]['text']='Objetivo: Grupo no identificado\nJustificacion: Lo rechaza.'
    result=validate(data)
    assert result['pares_validos']==0 and result['pares_excluidos']==1
    assert 'objetivo_de_odio_sin_resolver' in result['registros'][0]['incidencias']
    assert 'registro_ausente' in result['registros'][1]['incidencias']

def test_ambiguous_comments_require_review_not_latest_wins():
    data=sample();data['records'][0]['comentarios']*=2
    result=validate(data)
    assert 'comentario_ausente_o_multiple' in result['registros'][0]['incidencias']

def test_unconfirmed_and_blank_reason_not_accepted():
    data=sample();row=data['records'][0];row['confirmado']=False
    row['comentarios'][0]['text']='Objetivo: No aplica\nJustificacion: \nRegistro: relleno'
    result=validate(data)
    assert set(result['registros'][0]['incidencias'])=={'sin_confirmar','justificacion_vacia'}

def test_assistance_in_target_is_preserved():
    data=sample()
    data['records'][0]['comentarios'][0]['text']='Objetivo: No aplica\nJustificacion: Sin ataque.\nRegistro: campo Objetivo estructurado con asistencia.'
    assert validate(data)['resumen']['a']['con_asistencia_declarada']==1
