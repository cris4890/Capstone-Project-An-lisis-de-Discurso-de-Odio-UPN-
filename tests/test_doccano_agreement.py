import pytest
from doccano_agreement import compare

def rows(xs,ys):
    return ([dict(id_comentario=str(i),texto=str(i),numero_archivo=i+1,etiqueta_normalizada=x,justificacion_original='a') for i,x in enumerate(xs)],
            [dict(id_comentario=str(i),texto=str(i),categoria=y,justificacion='b') for i,y in enumerate(ys)])

def test_known_kappa_and_original_ambiguity():
    result=compare(*rows(['Odio','Odio','Neutro','Neutro',None],['Odio','Neutro','Neutro','Neutro','Odio']))
    assert result['pares']==4 and result['coincidencias']==3
    assert result['kappa']==pytest.approx(.5)
    assert len(result['excluidos'])==1 and len(result['desacuerdos'])==1

def test_single_class_has_undefined_kappa():
    assert compare(*rows(['Neutro'],['Neutro']))['kappa'] is None

def test_mismatched_units_rejected():
    a,b=rows(['Neutro'],['Odio']);b[0]['texto']='different'
    with pytest.raises(ValueError,match='texto'):compare(a,b)
