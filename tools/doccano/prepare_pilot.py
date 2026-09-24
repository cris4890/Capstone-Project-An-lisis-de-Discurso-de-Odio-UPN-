"""Create synthetic pilot projects, without manufacturing human annotations."""
import json
import secrets
import local
import django
django.setup()
from django.contrib.auth.models import User
from projects.models import TextClassificationProject, Member
from roles.models import Role
from examples.models import Example
from label_types.models import CategoryType

credentials_path = local.DATA.parent / "accesos.json"
credentials = json.loads(credentials_path.read_text()) if credentials_path.exists() else {}
users = {}
for name in ["coordinador", "evaluador_a", "evaluador_b"]:
    user, created = User.objects.get_or_create(username=name)
    if created:
        password = secrets.token_urlsafe(18)
        user.set_password(password)
        user.is_staff = user.is_superuser = name == "coordinador"
        user.save()
        credentials[name] = password
    users[name] = user
credentials_path.write_text(json.dumps(credentials, indent=2), encoding="utf-8")
rows = [json.loads(line) for line in (local.ROOT / "tools/doccano/piloto_sintetico.jsonl").read_text(encoding="utf-8").splitlines()]
guideline = '''Prueba con datos SINTETICOS. No constituye anotacion humana validada.
Seleccione una clase: Odio, Ofensivo o Neutro. Si falta contexto, deje sin confirmar.
En Comments registre un unico comentario con este formato:
Objetivo: grupo atacado, o No aplica
Justificacion: motivo basado en el texto
No mire las decisiones del otro evaluador. Los proyectos estan separados.
Al terminar, confirme la unidad. El coordinador revisara completitud antes de exportar.
'''
projects = {}
for name in ["evaluador_a", "evaluador_b"]:
    project, created = TextClassificationProject.objects.get_or_create(
        name="Piloto sintetico - " + name,
        defaults=dict(description="12 comentarios ficticios; proyecto independiente por evaluador.",
                      guideline=guideline, created_by=users["coordinador"],
                      project_type="DocumentClassification", single_class_classification=True,
                      collaborative_annotation=False))
    for who, role in [("coordinador", "project_admin"), (name, "annotator")]:
        Member.objects.get_or_create(project=project, user=users[who], defaults={"role": Role.objects.get(name=role)})
    for label, color in [("Odio", "#B71C1C"), ("Ofensivo", "#E65100"), ("Neutro", "#1565C0")]:
        CategoryType.objects.get_or_create(project=project, text=label, defaults={"background_color": color})
    if created:
        for row in rows:
            Example.objects.create(project=project, text=row["text"], meta={k: v for k, v in row.items() if k != "text"})
    projects[name] = project.id
(local.DATA.parent / "piloto.json").write_text(json.dumps(projects, indent=2), encoding="utf-8")
print(json.dumps({"projects": projects, "examples_per_project": 12, "credentials": str(credentials_path), "human_annotations_created": 0}))
