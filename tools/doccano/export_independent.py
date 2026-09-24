"""Immutable read-only snapshot of both independent pilot projects."""
import json
from datetime import datetime, timezone
import local
import django
django.setup()
from django.db import transaction
from examples.models import Example, Comment
from labels.models import Category

def main():
    manifest = json.loads((local.DATA.parent/"independiente.json").read_text(encoding="utf-8"))
    records=[]
    with transaction.atomic():
        for evaluator,pid in manifest["projects"].items():
            for example in Example.objects.filter(project_id=pid).order_by("id"):
                comments=[dict(id=c.id,user=c.user.username,text=c.text,created_at=c.created_at.isoformat())
                          for c in Comment.objects.filter(example=example,user__username=evaluator).select_related("user").order_by("id")]
                labels=Category.objects.filter(example=example,user__username=evaluator).select_related("label")
                records.append(dict(project_id=pid,example_id=example.id,id_comentario=example.meta["id_comentario"],
                    evaluador=evaluator,texto=example.text,metadata=example.meta,
                    etiquetas=[r.label.text for r in labels],
                    evidencia_etiquetas=[dict(id=r.id,created_at=r.created_at.isoformat(),updated_at=r.updated_at.isoformat()) for r in labels],
                    comentarios=comments,confirmado=example.states.filter(confirmed_by__username=evaluator).exists()))
    now=datetime.now(timezone.utc)
    directory=local.DATA.parent/"importaciones"/now.strftime("%Y%m%dT%H%M%S%fZ")
    directory.mkdir(parents=True,exist_ok=False)
    snapshot=dict(schema=1,exported_at=now.isoformat(),manifest=manifest,
                  source_jsonl=(local.DATA.parent/"independiente_muestra.jsonl").read_text(encoding="utf-8"),records=records)
    path=directory/"snapshot.json"
    path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding="utf-8")
    print(path)

if __name__ == "__main__":
    main()
