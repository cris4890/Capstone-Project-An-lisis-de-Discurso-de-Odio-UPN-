"""Independent synthetic workflow pilot. No reference labels or model predictions."""
import hashlib
import json
import random
import uuid
import local
import django
django.setup()
from django.db import transaction
from django.contrib.auth.models import User
from projects.models import TextClassificationProject, Member
from roles.models import Role
from examples.models import Example
from label_types.models import CategoryType

VERSION = "independiente-sintetico-v1"
TEXTS = [
    ("es", "La biblioteca debería abrir también los domingos."),
    ("es", "Tu explicación es una porquería; aprende antes de opinar."),
    ("es", "No alquilaría mi departamento a alguien solo por ser extranjero."),
    ("es", "Mi vecina llegó de otro país y organiza las actividades del barrio."),
    ("es", "Esa respuesta fue cruel, aunque discrepo de llamarla discurso de odio."),
    ("es", "Las personas de esa religión no deberían ocupar cargos públicos."),
    ("es", "No se debe negar un empleo a una persona por su religión."),
    ("es", "Vaya genio: borraste todos los archivos otra vez."),
    ("es", "Una rampa beneficiaría a quienes usan silla de ruedas y a otras personas."),
    ("es", "Las personas con discapacidad no deberían poder matricularse aquí."),
    ("es", "Leí la frase ‘las mujeres no sirven para dirigir’ y la rechacé en la reunión."),
    ("es", "Prefiero evaluar la experiencia de cada candidato antes de votar."),
    ("es", "Cállate, imbécil; nadie te pidió una explicación."),
    ("es", "Todos los hombres son incapaces de cuidar a un niño."),
    ("es", "Mi crítica es a esa organización religiosa y a su manejo del dinero."),
    ("es", "No quiero que mi hijo comparta clase con niños de esa etnia."),
    ("es", "Que alguien critique una ley no significa que ataque a toda una comunidad."),
    ("es", "Qué asco de comentario has escrito."),
    ("es", "Las parejas del mismo sexo deberían quedar fuera del programa de vivienda."),
    ("es", "Se burlaron de mi acento y pedí que dejaran de hacerlo."),
    ("es", "La gente mayor no debería tener derecho a votar."),
    ("es", "Esta aplicación necesita botones más grandes y un contraste mejor."),
    ("es", "Claro, porque hablar otro idioma te vuelve automáticamente sospechoso. Qué absurdo."),
    ("es", "No volveré a contratar a ese proveedor porque incumplió el plazo."),
    ("es", "Esa gente no debería estar aquí."),
    ("en", "Could someone explain how the new bus timetable works?"),
    ("en", "You are an arrogant fool who never listens."),
    ("en", "People from that ethnic group should be refused service."),
    ("en", "The restaurant should provide menus in more than one language."),
    ("en", "I oppose the institution's policy, not the people who follow that faith."),
    ("en", "Women are naturally unfit to make important decisions."),
    ("en", "Calling women unfit to lead is a stereotype we should challenge."),
    ("en", "Wonderful work, you managed to break the only working printer."),
    ("en", "Disabled students deserve the same opportunities as everyone else."),
    ("en", "We should keep disabled people out of public events."),
    ("en", "That proposal is poorly argued and lacks reliable evidence."),
    ("en", "Your entire argument is garbage."),
    ("en", "People of that religion cannot be trusted, any of them."),
    ("en", "A moderator removed a post that demanded a ban on a religious group."),
    ("en", "I need more information before deciding whether the policy is fair."),
    ("en", "Gay people should not be allowed to become teachers."),
    ("en", "Being gay has nothing to do with someone's ability to teach."),
    ("en", "Stop wasting our time with your pathetic excuses."),
    ("en", "Young people should lose their right to participate in elections."),
    ("en", "The survey compares age groups but does not describe every individual."),
    ("en", "Yeah, blaming every immigrant for one person's mistake makes perfect sense. Not."),
    ("en", "I reported a message mocking someone's disability."),
    ("en", "Those people are always the problem."),
    ("en", "Nobody should be excluded from the meeting because of their nationality."),
    ("en", "Your behavior yesterday was unacceptable; please apologize."),
]

def main():
    assert len(TEXTS) == len(set(text for _, text in TEXTS)) == 50
    source = [dict(text=text, idioma=language, origen="sintetico",
                   corpus_version=VERSION, id_comentario=str(uuid.uuid5(uuid.NAMESPACE_URL, VERSION+str(i))))
              for i, (language, text) in enumerate(TEXTS)]
    random.Random(210926).shuffle(source)
    payload = "\n".join(json.dumps(row, ensure_ascii=False) for row in source)+"\n"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    manifest_path = local.DATA.parent / "independiente.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous["source_sha256"] != digest:
            raise ValueError("La muestra cambió: cree otra versión; no modifique un piloto en curso.")
    coordinator = User.objects.get(username="coordinador")
    manual = (local.ROOT / "docs/manual_anotacion.md").read_text(encoding="utf-8")
    guideline = '''# Piloto independiente con textos sintéticos
Dos personas diferentes deben trabajar con una cuenta cada una. No compartir respuestas
ni usar predicciones o respuestas sugeridas. La práctica anterior de 12 textos no se incluye.
Lea el manual antes de comenzar. Use Comments con dos campos:
Objetivo: grupo o atributo atacado, o No aplica
Justificacion: motivo de la decisión apoyado en el texto
Seleccione una sola clase y confirme solo cuando los campos estén completos.
Si no hay contexto suficiente: escriba la duda y deje SIN CONFIRMAR, sin forzar una clase.
No puede inferir edad, etnia o intención a partir del autor o una comunidad.
El coordinador no debe comentar las respuestas durante la evaluación.
Esta muestra explora el procedimiento; no representa Reddit ni su distribución real.

'''+manual
    projects = {}
    with transaction.atomic():
        for name in ["evaluador_a", "evaluador_b"]:
            project, created = TextClassificationProject.objects.get_or_create(
                name="Independiente 50 v1 - "+name,
                defaults=dict(description="50 textos sintéticos nuevos sin respuestas sugeridas. Evaluación independiente.",
                              guideline=guideline, created_by=coordinator, project_type="DocumentClassification",
                              single_class_classification=True, collaborative_annotation=False))
            if created:
                for user, role in [(coordinator,"project_admin"),(User.objects.get(username=name),"annotator")]:
                    Member.objects.create(project=project,user=user,role=Role.objects.get(name=role))
                for label,color in [("Odio","#B71C1C"),("Ofensivo","#E65100"),("Neutro","#1565C0")]:
                    CategoryType.objects.create(project=project,text=label,background_color=color)
                for row in source:
                    Example.objects.create(project=project,text=row["text"],meta={k:v for k,v in row.items() if k!="text"})
            else:
                actual = {e.meta["id_comentario"]: e.text for e in Example.objects.filter(project=project)}
                assert actual == {r["id_comentario"]:r["text"] for r in source}, "El proyecto existente difiere; no se sobrescribe."
            projects[name]=project.id
    (local.DATA.parent / "independiente_muestra.jsonl").write_text(payload,encoding="utf-8")
    manifest = dict(version=VERSION, projects=projects, n=50, source_sha256=digest,
                    manual_sha256=hashlib.sha256(manual.encode()).hexdigest(),
                    purpose="piloto sintetico del procedimiento", gold_labels_provided=False,
                    independent_humans_confirmed=False)
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest))

if __name__ == "__main__":
    main()
