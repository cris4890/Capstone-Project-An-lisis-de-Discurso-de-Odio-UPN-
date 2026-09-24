"""Read-only ingestion of pilot snapshots. Never exports training labels."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

CLASSES = {"Odio", "Ofensivo", "Neutro"}

def fields(text):
    """Read only explicit fields; never treat original/provenance text as a reason."""
    parts = re.split(r"(?im)(?:^|\n)\s*(Objetivo|Justificaci[oó]n|Registro|Categor[ií]a original|Motivo original|Estado)\s*:\s*", text)
    found = {}
    for key, value in zip(parts[1::2], parts[2::2]):
        key = key.lower().replace("ó", "o")
        if key in found:
            raise ValueError("Campo repetido en comentario")
        found[key] = value.strip()
    return found

def validate(snapshot):
    if snapshot.get("schema") != 1:
        raise ValueError("Esquema de exportación no compatible")
    manifest = snapshot["manifest"]
    source = snapshot["source_jsonl"]
    if hashlib.sha256(source.encode("utf-8")).hexdigest() != manifest["source_sha256"]:
        raise ValueError("El hash de la muestra no coincide")
    corpus = [json.loads(line) for line in source.splitlines() if line.strip()]
    units = {r["id_comentario"]: r for r in corpus}
    if len(units) != len(corpus) or len(units) != manifest["n"]:
        raise ValueError("Muestra duplicada o tamaño incorrecto")
    evaluators = list(manifest["projects"])
    if len(evaluators) != 2:
        raise ValueError("Se requieren dos evaluadores")
    indexed = {}
    for row in snapshot["records"]:
        key = (row["evaluador"], row["id_comentario"])
        if key in indexed:
            raise ValueError("Registro duplicado")
        if key[0] not in evaluators or key[1] not in units:
            raise ValueError("Evaluador o unidad ajenos al manifiesto")
        if row["project_id"] != manifest["projects"][key[0]] or row["texto"] != units[key[1]]["text"]:
            raise ValueError("Proyecto o texto no corresponde a la muestra")
        indexed[key] = row
    imported = []
    for name in evaluators:
        for uid in units:
            row = indexed.get((name,uid))
            errors = []
            target = reason = None
            label = None
            assisted = False
            if row is None:
                errors.append("registro_ausente")
            else:
                labels = row["etiquetas"]
                if len(labels) != 1 or labels[0] not in CLASSES:
                    errors.append("categoria_ausente_o_invalida")
                else:
                    label = labels[0]
                if row["confirmado"] is not True:
                    errors.append("sin_confirmar")
                comments = row["comentarios"]
                if len(comments) != 1:
                    errors.append("comentario_ausente_o_multiple")
                else:
                    comment = comments[0]
                    if comment["user"] != name:
                        errors.append("autor_comentario_incorrecto")
                    try:
                        parsed = fields(comment["text"])
                    except ValueError:
                        parsed = {}
                        errors.append("campos_repetidos")
                    target = parsed.get("objetivo")
                    reason = parsed.get("justificacion")
                    assisted = any(term in comment["text"].lower() for term in ("asistid", "asistencia"))
                    if not target:
                        errors.append("objetivo_vacio")
                    if not reason:
                        errors.append("justificacion_vacia")
                    if label == "Odio" and target and any(s in target.lower() for s in ["no aplica", "no identificado", "no determinado"]):
                        errors.append("objetivo_de_odio_sin_resolver")
            imported.append(dict(evaluador=name,id_comentario=uid,categoria=label,
                                 objetivo=target,justificacion=reason,asistencia_declarada=assisted,
                                 incidencias=errors,valido_estructuralmente=not errors))
    summary = {}
    for name in evaluators:
        subset = [r for r in imported if r["evaluador"] == name]
        summary[name] = dict(total=len(subset),validos=sum(r["valido_estructuralmente"] for r in subset),
                             con_asistencia_declarada=sum(r["asistencia_declarada"] for r in subset),
                             incidencias=dict(Counter(e for r in subset for e in r["incidencias"])))
    lookup = {(r["evaluador"],r["id_comentario"]):r for r in imported}
    pairs = [(lookup[(evaluators[0],uid)],lookup[(evaluators[1],uid)]) for uid in units]
    valid_pairs = [(a,b) for a,b in pairs if a["valido_estructuralmente"] and b["valido_estructuralmente"]]
    disagreements = [dict(id_comentario=a["id_comentario"],categoria_a=a["categoria"],categoria_b=b["categoria"],
                          objetivo_a=a["objetivo"],objetivo_b=b["objetivo"],
                          categoria_distinta=a["categoria"]!=b["categoria"],
                          objetivo_textual_distinto=a["objetivo"]!=b["objetivo"])
                     for a,b in valid_pairs if a["categoria"]!=b["categoria"] or a["objetivo"]!=b["objetivo"]]
    return dict(schema=1,corpus_version=manifest["version"],resumen=summary,registros=imported,
                pares_validos=len(valid_pairs),pares_excluidos=len(pairs)-len(valid_pairs),
                diferencias_para_revision=disagreements,kappa=None,
                estado_acuerdo="Pendiente de cierre de ambos evaluadores y revisión de exclusiones y asistencia.",
                habilitado_para_entrenamiento=False,
                nota="Validación de estructura; no corrige interpretaciones ni acredita independencia humana. Diferencias textuales de objetivo requieren revisión semántica.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot",type=Path)
    args = parser.parse_args()
    result = validate(json.loads(args.snapshot.read_text(encoding="utf-8")))
    output = args.snapshot.parent / "validacion.json"
    with output.open("x",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    lines = ["# Validación de anotaciones de Doccano", "", result["nota"], ""]
    for name,data in result["resumen"].items():
        lines += [f"## {name}",f"Registros estructuralmente válidos: {data['validos']} de {data['total']}.",
                  f"Con asistencia de redacción declarada: {data['con_asistencia_declarada']}."]
        lines += [f"- {key}: {value}" for key,value in data["incidencias"].items()]
    lines += ["",f"Pares válidos: {result['pares_validos']}. Pares excluidos: {result['pares_excluidos']}.",
              result["estado_acuerdo"],"No se habilita entrenamiento ni adjudicación automática."]
    (args.snapshot.parent/"informe.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(result["resumen"],ensure_ascii=False))

if __name__ == "__main__":
    main()
