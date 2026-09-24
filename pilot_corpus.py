"""Prepare a traceable pilot package without inventing Reddit metadata."""
import argparse
import hashlib
import json
from pathlib import Path
from annotation_report import load_closure

def prepare(closure, sample_text, editorial=None):
    manifest, adjudication, rows = load_closure(closure)
    samples = [json.loads(line) for line in sample_text.splitlines() if line.strip()]
    source = {row['id_comentario']:row for row in samples}
    if len(source) != len(samples) or set(source) != {r['id_comentario'] for r in rows}:
        raise ValueError('La muestra no corresponde al cierre.')
    decisions = {r['id_comentario']:r for r in adjudication['casos']}
    edits = {}
    if editorial is not None:
        edits = {r['id_comentario']:r for r in editorial['registros']}
        expected = {r['id_comentario'] for r in rows if r['id_comentario'] not in decisions}
        if len(edits) != len(editorial['registros']) or set(edits) != expected:
            raise ValueError('La revisión editorial no corresponde a las unidades sin adjudicación.')
    output=[]
    for row in rows:
        uid=row['id_comentario']; sample=source[uid]
        if sample['text'] != row['texto'] or sample['origen'] != 'sintetico':
            raise ValueError('Texto u origen inconsistente.')
        decision=decisions.get(uid)
        issues=['sin_metadatos_de_hilo_y_comunidad','piloto_sintetico_no_representativo']
        target=reason=None
        target_source='sin_resolver'
        if decision:
            if decision['decision_final'] != row['categoria_final']:
                raise ValueError('Adjudicación distinta de la categoría final.')
            target=decision['objetivo_final'];reason=decision['justificacion_final']
            target_source='adjudicacion_E3_reportada'
            if not target or not reason or not decision['fecha'] or not decision['evaluador_revisor']:
                raise ValueError('Adjudicación incompleta.')
        else:
            if row['categoria_original_a'] != row['categoria_original_b'] or row['categoria_final'] != row['categoria_original_a']:
                raise ValueError('Falta adjudicación para un desacuerdo.')
            if uid in edits:
                edit=edits[uid]
                if edit['texto'] != row['texto'] or edit['categoria'] != row['categoria_final'] or not edit['objetivo_normalizado'].strip():
                    raise ValueError('Texto, categoría u objetivo editorial inconsistente.')
                if edit['motivo_original_a'] != row['motivo_original_a'] or edit['motivo_original_b'] != row['motivo_original_b']:
                    raise ValueError('Los motivos originales no coinciden.')
                target=edit['objetivo_normalizado']
                target_source='normalizacion_editorial_asistida'
                issues.append('objetivo_estructurado_con_asistencia_no_acuerdo_humano_medido')
            else:
                issues.append('objetivo_final_no_ratificado')
        output.append(dict(id_comentario=uid,texto=row['texto'],idioma=sample['idioma'],
                           origen='sintetico',categoria_final=row['categoria_final'],
                           grupo_objetivo_final=target,justificacion_final=reason,
                           procedencia_objetivo=target_source,
                           justificacion_estado='adjudicada_E3' if decision else 'se_conservan_ambos_motivos_originales',
                           motivo_original_a=row['motivo_original_a'],motivo_original_b=row['motivo_original_b'],
                           resolucion=row['resolucion'],incidencias=issues,apto_entrenamiento=False))
    report=dict(n=len(output),categorias_completas=len(output),
                objetivos_adjudicados=sum(r['procedencia_objetivo']=='adjudicacion_E3_reportada' for r in output),
                objetivos_normalizados_con_asistencia=sum(r['procedencia_objetivo']=='normalizacion_editorial_asistida' for r in output),
                objetivos_por_ratificar=sum(r['grupo_objetivo_final'] is None for r in output),
                apto_entrenamiento=False,
                alcance='Paquete de revisión del piloto. No inventa subreddits, fechas de publicaciones o hilos.',
                source_sha256=hashlib.sha256(sample_text.encode()).hexdigest())
    return output,report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('closure',type=Path)
    parser.add_argument('sample',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--editorial',type=Path)
    args=parser.parse_args()
    editorial=json.loads(args.editorial.read_text(encoding='utf-8')) if args.editorial else None
    rows,report=prepare(args.closure,args.sample.read_text(encoding='utf-8'),editorial)
    report['cierre_manifest_sha256']=hashlib.sha256((args.closure/'manifest.json').read_bytes()).hexdigest()
    if args.editorial:
        report['revision_editorial_sha256']=hashlib.sha256(args.editorial.read_bytes()).hexdigest()
    args.output.mkdir(parents=True,exist_ok=False)
    corpus=args.output/'corpus_revision.jsonl'
    corpus.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n',encoding='utf-8')
    report['corpus_sha256']=hashlib.sha256(corpus.read_bytes()).hexdigest()
    (args.output/'calidad.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__ == '__main__':
    main()
