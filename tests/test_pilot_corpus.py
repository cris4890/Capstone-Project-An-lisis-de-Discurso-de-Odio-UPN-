import json
import pytest
import pilot_corpus

def fixture(monkeypatch):
    row=dict(id_comentario='one',texto='Ejemplo',categoria_final='Neutro',categoria_original_a='Neutro',categoria_original_b='Neutro',motivo_original_a='a',motivo_original_b='b',resolucion='coincidencia_de_categorias_A_B')
    monkeypatch.setattr(pilot_corpus,'load_closure',lambda path: ({},{'casos':[]},[row]))
    return row,json.dumps(dict(id_comentario='one',text='Ejemplo',origen='sintetico',idioma='es'))

def test_no_fabricated_targets_or_training_metadata(monkeypatch):
    _,source=fixture(monkeypatch)
    rows,report=pilot_corpus.prepare('unused',source)
    assert rows[0]['grupo_objetivo_final'] is None
    assert report['objetivos_por_ratificar']==1 and not report['apto_entrenamiento']
    assert 'subreddit' not in rows[0] and 'id_hilo' not in rows[0]

def test_mismatched_source_rejected(monkeypatch):
    _,source=fixture(monkeypatch)
    with pytest.raises(ValueError):pilot_corpus.prepare('unused',source.replace('Ejemplo','Otro'))

def test_missing_adjudication_rejected(monkeypatch):
    row,source=fixture(monkeypatch);row['categoria_original_b']='Odio'
    with pytest.raises(ValueError,match='adjudicación'):pilot_corpus.prepare('unused',source)

def test_editorial_targets_not_counted_as_human_adjudications(monkeypatch):
    row,source=fixture(monkeypatch)
    edit=dict(id_comentario='one',texto='Ejemplo',categoria='Neutro',objetivo_normalizado='No aplica',motivo_original_a='a',motivo_original_b='b')
    rows,report=pilot_corpus.prepare('unused',source,{'registros':[edit]})
    assert report['objetivos_adjudicados']==0
    assert report['objetivos_normalizados_con_asistencia']==1
    assert report['objetivos_por_ratificar']==0
    assert rows[0]['justificacion_final'] is None
    assert rows[0]['motivo_original_a']=='a' and rows[0]['motivo_original_b']=='b'
    edit['categoria']='Odio'
    with pytest.raises(ValueError):pilot_corpus.prepare('unused',source,{'registros':[edit]})
