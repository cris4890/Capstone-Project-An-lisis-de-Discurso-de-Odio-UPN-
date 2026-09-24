"""Read verified pilot closures without altering annotations or training data."""
import hashlib
import json
from pathlib import Path
from collections import Counter

def load_closure(directory):
    directory = Path(directory)
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    names = ('adjudicacion_E3.json', 'piloto_categorias_finales.jsonl')
    for name in names:
        raw = (directory/name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest['archivos_sha256'][name]:
            raise ValueError('La evidencia no coincide con su hash registrado.')
    adjudication = json.loads((directory/names[0]).read_text(encoding='utf-8'))
    rows = [json.loads(line) for line in (directory/names[1]).read_text(encoding='utf-8').splitlines() if line.strip()]
    if len(rows) != manifest['n'] or len({r['id_comentario'] for r in rows}) != len(rows):
        raise ValueError('Cantidad o identificadores inconsistentes.')
    if dict(Counter(r['categoria_final'] for r in rows)) != manifest['distribucion']:
        raise ValueError('Distribución inconsistente.')
    return manifest, adjudication, rows

def render_annotation_report(root):
    import pandas as pd
    import streamlit as st
    st.subheader('Anotación y acuerdo')
    st.caption('Piloto sintético de Doccano · Independiente de la ejecución de modelos seleccionada.')
    closures = sorted((Path(root)/'private/doccano/cierres').glob('*/manifest.json'), reverse=True)
    if not closures:
        st.info('Todavía no hay cierres de anotación disponibles en este equipo.')
        return
    selected = st.selectbox('Cierre del piloto', [p.parent.name for p in closures])
    directory = next(p.parent for p in closures if p.parent.name == selected)
    try:
        manifest, adjudication, rows = load_closure(directory)
        # The closure points to original comparison evidence by content hash.
        comparison = None
        for path in (Path(root)/'private/doccano/comparaciones').glob('*/resultado.json'):
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() == adjudication['comparacion_original_sha256']:
                comparison = json.loads(raw)
                break
    except (OSError, ValueError, KeyError, TypeError):
        st.error('No se pudo verificar este cierre. Revisa la integridad de sus evidencias.')
        return
    st.warning('Datos sintéticos. El acuerdo no mide precisión del modelo ni valida resultados sobre Reddit real.')
    a,b,c = st.columns(3)
    a.metric('Comentarios con categoría final', manifest['n'])
    b.metric('Coincidencias originales', manifest['coincidencias_originales'])
    c.metric('Casos adjudicados', manifest['adjudicaciones'])
    if comparison:
        a,b,c = st.columns(3)
        a.metric('Pares originales comparables', comparison['pares'])
        b.metric('Acuerdo observado', f"{comparison['acuerdo_observado']:.1%}")
        kappa = comparison['kappa']
        c.metric('Kappa previo a adjudicación', 'No definido' if kappa is None else f'{kappa:.3f}')
        st.caption('Se excluyó una categoría original ambigua. El cálculo conserva las respuestas anteriores a las revisiones asistidas.')
        with st.expander('Matriz de acuerdo original'):
            st.write('Filas: evaluador A. Columnas: evaluador B.')
            st.dataframe(pd.DataFrame(comparison['matriz_filas_a_columnas_b'], index=comparison['clases'], columns=comparison['clases']))
    else:
        st.info('La comparación original no está disponible o no coincide con el hash del cierre. No se muestran sus métricas.')
    st.write('Categorías finales del piloto')
    st.dataframe(pd.DataFrame([{'Categoría':k,'Cantidad':v} for k,v in manifest['distribucion'].items()]),hide_index=True)
    info = adjudication['identidad_y_fecha_real_del_tercero']
    st.caption(f"Revisor: {info['codigo']} · Fecha comunicada: {info['fecha_revision']} · Adjudicación registrada según confirmación del usuario.")
    st.caption('Se documentó asistencia en redacción y objetivos. La identidad e independencia de los participantes no se verificaron mediante esta aplicación.')
    with st.expander('Consultar los seis casos adjudicados'):
        for case in sorted(adjudication['casos'],key=lambda r:r['numero']):
            st.write(f"Caso {case['numero']} · {case['decision_final']}")
            st.text(case['texto'])
            st.text('Objetivo: '+case['objetivo_final'])
            st.text('Motivo: '+case['justificacion_final'])
    st.download_button('Descargar categorías finales del piloto', (directory/'piloto_categorias_finales.jsonl').read_bytes(),
                       file_name='piloto_sintetico_categorias_finales.jsonl',mime='application/x-ndjson')
    st.caption('La descarga conserva decisiones originales y adjudicaciones. No inicia entrenamiento ni cambia los proyectos de Doccano.')
    closure_hash = hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest()
    for quality_path in sorted((Path(root)/'private/doccano').glob('corpus_revision_*/calidad.json'), reverse=True):
        try:
            quality = json.loads(quality_path.read_text(encoding='utf-8'))
            if quality.get('cierre_manifest_sha256') != closure_hash:
                continue
            payload = (quality_path.parent/'corpus_revision.jsonl').read_bytes()
            if hashlib.sha256(payload).hexdigest() != quality['corpus_sha256']:
                st.error('El paquete consolidado no coincide con su evidencia de integridad.')
                break
            st.subheader('Paquete consolidado del piloto')
            st.write(f"{quality['n']} comentarios · {quality['objetivos_adjudicados']} objetivos adjudicados · "
                     f"{quality.get('objetivos_normalizados_con_asistencia',0)} objetivos normalizados con asistencia.")
            st.caption('Las 44 normalizaciones son editoriales; no son adjudicaciones nuevas de E3. Se conservan los dos motivos originales cuando hay coincidencia de categoría.')
            st.download_button('Descargar piloto con objetivos y motivos',payload,
                               file_name='piloto_sintetico_consolidado.jsonl',mime='application/x-ndjson')
            st.caption('Paquete del piloto para revisión y demostración; no incorporado al entrenamiento de investigación.')
            break
        except (OSError, ValueError, KeyError, TypeError):
            st.error('No se pudo leer el paquete consolidado del piloto.')
            break
