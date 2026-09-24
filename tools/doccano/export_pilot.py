"""Export original annotations and comments; no adjudication or invented labels."""
import json
import local
import django
django.setup()
from examples.models import Example, Comment
from labels.models import Category

projects = json.loads((local.DATA.parent / "piloto.json").read_text())
rows = []
for evaluator, project_id in projects.items():
    for example in Example.objects.filter(project_id=project_id):
        labels = list(Category.objects.filter(example=example,user__username=evaluator).values_list("label__text",flat=True))
        comments = list(Comment.objects.filter(example=example,user__username=evaluator).values("text","created_at"))
        rows.append({"id_comentario":example.meta["id_comentario"],"evaluador":evaluator,
                     "texto":example.text,"etiquetas":labels,"comentarios":comments,
                     "confirmado":example.states.filter(confirmed_by__username=evaluator).exists(),
                     "origen":"sintetico","adjudicado":False})
output = local.DATA.parent / "exportacion_piloto.jsonl"
output.write_text("\n".join(json.dumps(row,ensure_ascii=False,default=str) for row in rows)+"\n",encoding="utf-8")
print(f"Exportados {len(rows)} registros con sus comentarios: {output}")
