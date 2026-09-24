"""API checks rolled back: never retain simulated human decisions."""
import json
from datetime import datetime, timezone
import local
import django
django.setup()
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.test import APIClient
from examples.models import Example, Comment
from labels.models import Category
from label_types.models import CategoryType

projects = json.loads((local.DATA.parent / "piloto.json").read_text())
a, b = (User.objects.get(username=x) for x in projects)
pa, pb = projects.values()
unit = Example.objects.filter(project_id=pa).first()
checks = {}
client = APIClient()
checks["anonymous_denied"] = client.get(f"/v1/projects/{pa}/examples").status_code in (401,403)
client.force_authenticate(user=a)
checks["own_project_access"] = client.get(f"/v1/projects/{pa}/examples").status_code == 200
checks["other_project_denied"] = client.get(f"/v1/projects/{pb}/examples").status_code == 403
with transaction.atomic():
    label = CategoryType.objects.get(project_id=pa, text="Neutro")
    response = client.post(f"/v1/projects/{pa}/examples/{unit.id}/categories", {"example":unit.id,"label":label.id}, format="json")
    checks["category_saved"] = response.status_code == 201
    reason = "Objetivo: No aplica\nJustificacion: Prueba tecnica sintetica, no evaluacion humana."
    response = client.post(f"/v1/projects/{pa}/comments?example={unit.id}", {"text":reason}, format="json")
    checks["target_reason_saved"] = response.status_code == 201 and Comment.objects.filter(example=unit,user=a,text=reason).exists()
    client.force_authenticate(user=b)
    checks["other_comments_denied"] = client.get(f"/v1/projects/{pa}/comments?example={unit.id}").status_code == 403
    transaction.set_rollback(True)
checks["synthetic_annotations_rolled_back"] = not Category.objects.filter(example=unit).exists() and not Comment.objects.filter(example=unit).exists()
result = {"verified_at":datetime.now(timezone.utc).isoformat(),"checks":checks,"all_passed":all(checks.values()),"human_agreement_measured":False}
(local.DATA.parent / "verificacion.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result))
assert result["all_passed"]
