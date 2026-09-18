"""
Módulo de Ingesta, Generación y Preprocesamiento de Datos de Reddit
===================================================================

Proyecto: Análisis y Clasificación Automática del Discurso de Odio
          en Comunidades de Reddit (r/Millennials y r/GenZ).

Este módulo proporciona:
1. Generación de un corpus bilingüe sintético (español e inglés) representativo
   de interacciones en Reddit, balanceado por comunidad, idioma y clase de discurso.
2. Funciones de limpieza, normalización Unicode y anonimización de texto
   (sustitución de nombres de usuario y enlaces web preservando emojis y signos clave).
3. Pipeline automatizado para procesar el dataset y exportarlo en formatos CSV y Parquet.

Autor: Senior Data Engineer (NLP & Python)
"""

import logging
import os
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Optional, Union

import pandas as pd

# Configuración básica de logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DataPipeline")

# Rutas estándar del proyecto
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_CSV_PATH = DATA_DIR / "corpus_preprocesado.csv"
DEFAULT_PARQUET_PATH = DATA_DIR / "corpus_preprocesado.parquet"

# Expresiones regulares precompiladas para optimizar el rendimiento en inferencia por lotes
RE_UNICODE_INVISIBLE = re.compile(r"[\u200b\u200c\u200d\u200e\u200f\ufeff]")
RE_NON_BREAKING_SPACES = re.compile(r"[\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000]")
# Detecta URLs (http, https, www) sin absorber signos de puntuación o paréntesis finales
RE_URL = re.compile(r"(?:https?://|www\.)\S+?(?=[.,;!?)]*(?:\s|$))", flags=re.IGNORECASE)
# Detecta menciones de usuario Reddit (/u/usuario, u/usuario) o menciones (@usuario)
# Excluye direcciones de correo electrónico previniendo coincidencias precedidas por caracteres de palabra
RE_USER = re.compile(r"(?<!\w)(?:/?u/|@)[A-Za-z0-9_-]+", flags=re.IGNORECASE)
# Normalización de espacios repetidos
RE_SPACES = re.compile(r"\s+")


def clean_and_anonymize(text: str) -> str:
    """
    Limpia, normaliza y anonimiza un texto proveniente de comentarios de Reddit.

    Operaciones realizadas:
    a) Sustituye nombres de usuario (ej. u/usuario, /u/usuario, @usuario) por '[USER]'.
    b) Sustituye enlaces y URLs (http, https, www) por '[URL]'.
    c) Normaliza la codificación Unicode mediante la forma canónica NFKC, eliminando
       espacios invisibles o de no separación, manteniendo intactos emojis, tildes y
       signos de puntuación clave (¿?, ¡!, ., ,, etc.).
    d) Estandariza múltiples espacios en blanco a un único espacio y recorta extremos.

    Args:
        text (str): Texto crudo original del comentario.

    Returns:
        str: Texto procesado, normalizado y anonimizado.
    """
    if not isinstance(text, str):
        return ""

    # 1. Normalización Unicode canónica (NFKC) para caracteres compuestos y compatibles
    cleaned = unicodedata.normalize("NFKC", text)

    # 2. Eliminación de caracteres invisibles y formato de control de texto
    cleaned = RE_UNICODE_INVISIBLE.sub("", cleaned)
    cleaned = RE_NON_BREAKING_SPACES.sub(" ", cleaned)

    # 3. Anonimización de URLs
    cleaned = RE_URL.sub("[URL]", cleaned)

    # 4. Anonimización de usuarios de Reddit y menciones
    cleaned = RE_USER.sub("[USER]", cleaned)

    # 5. Normalización de espacios y saltos de línea redundantes
    cleaned = RE_SPACES.sub(" ", cleaned).strip()

    return cleaned


def generate_synthetic_data() -> pd.DataFrame:
    """
    Genera un conjunto sintético balanceado de comentarios representativos
    para comunidades de Reddit ('r/Millennials' y 'r/GenZ') en español e inglés.

    El corpus incluye 72 registros distribuidos de manera equilibrada en:
    - Subreddits: 'r/Millennials', 'r/GenZ'
    - Idiomas: 'es', 'en'
    - Categorías de clasificación:
        * 'Odio': Discurso de odio hacia grupos protegidos (nacionalidad, género, raza, orientación).
        * 'Ofensivo': Agresiones personales, toxicidad, insultos directos sin encajar en odio hacia minorías.
        * 'Neutro': Discusiones constructivas, nostalgia, consejos, preguntas informativas.

    Returns:
        pd.DataFrame: DataFrame con columnas ['id_comentario', 'subreddit', 'idioma', 'texto_original', 'etiqueta'].
    """
    records: List[Dict[str, str]] = [
        # =========================================================================
        # 1. r/Millennials - Español
        # =========================================================================
        # Odio (ES - Millennials)
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Todos esos inmigrantes que vienen a quitarnos los empleos deberían ser expulsados a la fuerza. u/carlos_90 tiene razón, arruinan nuestro país.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "La culpa de que no haya viviendas es de esa plaga de extranjeros ilegales. Míralo tú mismo en https://noticias-locales.com/crisis.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Esa comunidad de degenerados LGBT está destruyendo los valores familiares tradicionales con los que crecimos en los 90s. Dan asco.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Las feminazis modernas solo quieren privilegios y destruir a los hombres trabajadores. No sirven para nada. /u/antifem_truth",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Esa etnia siempre ha sido una lacra social y criminal. No es racismo, es la pura realidad biológica https://datos-falsos.org/estudio.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Deberíamos mandar a todos esos refugiados de vuelta a su basurero antes de que nos reemplacen a todos los ciudadanos honestos.",
            "etiqueta": "Odio",
        },
        # Ofensivo (ES - Millennials)
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Eres un tonto no sirves para nada bruto, cállate estúpido y deja de opinar idioteces u/bocazas.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Eres un inútil y un fracasado patético de 35 años que no sirve para nada. Das vergüenza ajena 🤡.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Cállate estúpido lamebotas insoportable, vete al carajo con tus consejos baratos https://linkedin.com/in/fakecoach.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Maldita sea, estoy harto de idiotas y brutos como /u/marcos_rr que defienden a los usureros. Púdrete.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Tu comentario es una completa basura y tú eres un tonto que no sabe nada de la vida. Púdrete.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Deja de llorar por cualquier estupidez, imbécil inútil. Madura de una maldita vez y ponte a trabajar.",
            "etiqueta": "Ofensivo",
        },
        # Neutro (ES - Millennials)
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "¿Alguien más recuerda pasar las tardes jugando con la Nintendo 64 y comiendo cereales? Qué buenos tiempos u/retro_gamer.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "La subida de los tipos de interés hace imposible comprar un piso ahora mismo en las grandes ciudades. Les comparto este informe: https://ine.es/vivienda2024.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "A mis 34 años decidí cambiar de carrera hacia desarrollo de software y fue la mejor decisión 💻🚀.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Me gusta mucho cómo /u/psicologia_millennial explica el síndrome de burnout en su blog: https://saludmental.org/burnout.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "¿Qué podcasts en español recomiendan sobre finanzas personales y ahorro para el retiro?",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "es",
            "texto_original": "Totalmente de acuerdo con tu punto sobre el equilibrio entre la vida laboral y personal. Saludos @ana_maldonado.",
            "etiqueta": "Neutro",
        },
        # =========================================================================
        # 2. r/Millennials - English
        # =========================================================================
        # Odio (EN - Millennials)
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "All these illegal immigrants pouring across the border are ruining our communities. Send them all back where they belong! u/border_patrol.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Trans ideology is a mental illness pushed by sick perverts targeting our children. Look at this madness: https://fake-news-patriot.org/leak.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Women only marry for money and ruin men in family courts. They are selfish parasites /u/mgtow_legacy.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Certain ethnic groups are genetically prone to crime and lower IQ, look at the stats on https://alt-stats.net/crimes.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Muslim refugees will never integrate into Western society, they want to enforce sharia law and replace us all.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Those disgusting degenerates in pride parades shouldn't be allowed around decent people. u/traditional_values_guy.",
            "etiqueta": "Odio",
        },
        # Ofensivo (EN - Millennials)
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Shut your fucking mouth, you clueless corporate bootlicker. Nobody asked for your stupid opinion u/office_drone.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "You're 38 and still broke complaining about landlords? Get off your lazy ass and stop being a pathetic loser 🤡.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Go fuck yourself. Your take on the housing market is literally brain-dead https://reddit.com/r/housing/idiots.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "What a complete piece of shit /u/crypto_bro_99 is for scamming people in this sub.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "You are an insufferable prick and everyone in your office probably hates you behind your back.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Stop crying like a little bitch and take accountability for your awful life choices.",
            "etiqueta": "Ofensivo",
        },
        # Neutro (EN - Millennials)
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Remember coming home from middle school to watch TRL on MTV and log into AIM? The nostalgia hits hard u/90s_kid.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "We finally paid off the last of our student loans today after 11 years! Such a relief 🥑🎉.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Here is a great breakdown of index fund investing for 30-somethings: https://bogleheads.org/wiki/Three-fund_portfolio.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Honestly, cutting out alcohol in my mid-30s completely cured my chronic fatigue and insomnia @healthy_habits.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Did anyone else transition from tech into trades? Wondering if plumbing or electrical is worth learning now.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/Millennials",
            "idioma": "en",
            "texto_original": "Check out /u/cooking_enthusiast's recipe for sourdough bread, made it yesterday and it turned out amazing https://cooking.com/bread.",
            "etiqueta": "Neutro",
        },
        # =========================================================================
        # 3. r/GenZ - Español
        # =========================================================================
        # Odio (ES - GenZ)
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Todos los maricones y raritos de género deberían ser internados en psiquiátricos, dan asco en la escuela u/edgy_teen.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Esa gente marrón que invade nuestros colegios debería largarse de España. Arruinan nuestra cultura https://nacionalismo-extremo.com.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Las feministas modernas son todas unas gordas resentidas que odian a los hombres porque nadie se las coge /u/alfa_redpill.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Los judíos controlan toda la industria musical y los medios para manipular a nuestra generación. Despierten: https://conspiracion.net/agenda.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Ojalá limpien las calles de todos esos mendigos y gitanos, son una escoria que no merece derechos humanos.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Esas personas trans mutilan sus cuerpos y esperan que celebremos su perversión. Son enfermos mentales @vox_fan.",
            "etiqueta": "Odio",
        },
        # Ofensivo (ES - GenZ)
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Cállate la puta boca, eres un tonto no sirves para nada bruto. Cero rizz u/skibidi_clown 💀.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Cállate estúpido, das cringe supremo con tus tiktoks de mierda. Eres un inútil borra la cuenta.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Tu opinión es pura basura, eres un bruto si de verdad crees que la uni vale la pena https://reddit.com/r/GenZ/comments/123.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Maldito tonto ignorante /u/toxic_gamer, aprende a jugar o desinstala el juego pedazo de bruto.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Qué asco de pavo, eres un estúpido inútil, ojalá te atropellen por pesado.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Deja de decir mamadas y ponte a estudiar, payaso tonto y fracasado 🤡.",
            "etiqueta": "Ofensivo",
        },
        # Neutro (ES - GenZ)
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "La verdad la situación laboral para los recién graduados está bastante difícil, pero no hay que rendirse u/estudiante_2004.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Encontré este canal de YouTube que explica cálculo multivariable genial: https://youtube.com/watch?v=calculo_pro.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Siento que nuestra generación tiene mucha conciencia ambiental pero poca esperanza real frente al cambio climático 🌱.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Para los que buscan su primer empleo en tech, les recomiendo armar proyectos en GitHub: https://github.com/recursos-juniors.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "¿Alguien más siente que TikTok arruinó su capacidad de concentración para leer libros enteros? @sofia_lectora",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "es",
            "texto_original": "Tremendo beat el nuevo tema que subió /u/prod_marcos a Soundcloud, tiene muy buena vibra 🔥🎧.",
            "etiqueta": "Neutro",
        },
        # =========================================================================
        # 4. r/GenZ - English
        # =========================================================================
        # Odio (EN - GenZ)
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Get these third-world illegal invaders out of our country before they turn every city into a ghetto u/genz_nationalist.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Trans people are mentally ill groomers and should not be allowed anywhere near children or schools: https://radical-take.org/truth.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Women have zero loyalty and only seek validation on TikTok while destroying real masculinity. Total subhumans /u/based_sigmamale.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Certain races have lower genetic potential for science and tech, it's basic evolutionary biology https://race-facts-fake.com/chart.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Gay pride is degenerate propaganda funded by globalist elites to depopulate the West. Disgusting pigs.",
            "etiqueta": "Odio",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Feminism is a cancer that ruined modern society. Women should be stripped of voting rights @anti_woke_18.",
            "etiqueta": "Odio",
        },
        # Ofensivo (EN - GenZ)
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Shut the fuck up you brainrotted NPC. Your take has zero rizz and maximum cringe u/clown_energy 💀.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Delete your account you absolute dumbass, you have negative IQ and no future https://tiktok.com/@loser/video/1.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Go touch grass you pathetic virgin neckbeard. Nobody cares about your useless crying /u/edgelord420.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "You're a miserable piece of shit for cheating on your exams. Get exposed, bitch.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Stop yapping holy shit, you're annoying as fuck and everyone in the group chat laughs at you.",
            "etiqueta": "Ofensivo",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Bro is actually retarded if he thinks buying crypto memecoins is an investment strategy 🤡.",
            "etiqueta": "Ofensivo",
        },
        # Neutro (EN - GenZ)
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Does anyone else feel like college tuition is just way too overpriced compared to learning online? u/study_grind.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Here is a free curated list of internships for summer 2025: https://github.com/pittcsc/Summer2025-Internships.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Actually no cap, learning how to cook simple meals saved me so much money living in the dorms 🍳.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "Check out this guide by /u/budget_buddy on building credit safely as a college freshman: https://nerdwallet.com/best-credit-cards.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "I really love how our generation prioritizes mental health over hustle culture burnout ✨.",
            "etiqueta": "Neutro",
        },
        {
            "subreddit": "r/GenZ",
            "idioma": "en",
            "texto_original": "What are your favorite indie games released this year? Need recommendations for steam summer sale @gaming_vibes.",
            "etiqueta": "Neutro",
        },
    ]

    # Asignación de ID único estructurado para trazabilidad
    for idx, item in enumerate(records, start=1):
        item["id_comentario"] = f"cmt_{idx:04d}"

    df = pd.DataFrame(records)
    # Reordenar columnas para mantener el esquema contractual solicitado
    df = df[["id_comentario", "subreddit", "idioma", "texto_original", "etiqueta"]]
    logger.info("Generados %d registros sintéticos bilingües exitosamente.", len(df))
    return df


def process_and_save(
    df: Optional[pd.DataFrame] = None,
    output_csv: Union[str, Path] = DEFAULT_CSV_PATH,
    output_parquet: Union[str, Path] = DEFAULT_PARQUET_PATH,
) -> pd.DataFrame:
    """
    Ejecuta el pipeline de preprocesamiento sobre el DataFrame de comentarios,
    aplica la anonimización/limpieza de texto, añade 'texto_limpio' y persiste los
    datos tanto en formato CSV como en Apache Parquet.

    Args:
        df (Optional[pd.DataFrame]): DataFrame de entrada. Si es None, genera el
                                     dataset sintético por defecto.
        output_csv (Union[str, Path]): Ruta de destino para el archivo CSV.
        output_parquet (Union[str, Path]): Ruta de destino para el archivo Parquet.

    Returns:
        pd.DataFrame: DataFrame procesado con la nueva columna 'texto_limpio'.
    """
    if df is None:
        logger.info("No se proporcionó DataFrame. Generando datos sintéticos...")
        df = generate_synthetic_data()

    logger.info("Iniciando fase de limpieza y anonimización de texto...")
    df_processed = df.copy()
    df_processed["texto_limpio"] = df_processed["texto_original"].apply(clean_and_anonymize)

    # Asegurar que el directorio destino exista
    csv_path = Path(output_csv)
    parquet_path = Path(output_parquet)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Guardar en CSV (formato legible para inspección rápida con UTF-8)
    df_processed.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info("Archivo CSV guardado en: %s", csv_path.resolve())

    # 2. Guardar en Parquet (almacenamiento columnar optimizado para pipelines de ML)
    df_processed.to_parquet(parquet_path, index=False, engine="pyarrow")
    logger.info("Archivo Parquet guardado en: %s", parquet_path.resolve())

    return df_processed


def print_corpus_summary(df: pd.DataFrame) -> None:
    """
    Imprime métricas descriptivas y una muestra de verificación de la limpieza.
    """
    print("\n" + "=" * 70)
    print("RESUMEN DEL CORPUS PREPROCESADO")
    print("=" * 70)
    print(f"Total de registros: {len(df)}")
    print("\nDistribución por Etiqueta:")
    print(df["etiqueta"].value_counts().to_string())
    print("\nDistribución por Subreddit:")
    print(df["subreddit"].value_counts().to_string())
    print("\nDistribución por Idioma:")
    print(df["idioma"].value_counts().to_string())
    print("\n" + "-" * 70)
    print("MUESTRA COMPARATIVA (Original vs. Limpio):")
    print("-" * 70)
    sample_df = df.sample(n=min(5, len(df)), random_state=42)
    for _, row in sample_df.iterrows():
        print(f"[{row['id_comentario']}] ({row['subreddit']} | {row['idioma']} | {row['etiqueta']})")
        print(f"  ORIGINAL: {row['texto_original']}")
        print(f"  LIMPIO  : {row['texto_limpio']}\n")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    logger.info("=== Iniciando Pipeline de Datos Capstone Reddit NLP ===")
    df_final = process_and_save()
    print_corpus_summary(df_final)
    logger.info("=== Pipeline ejecutado con éxito ===")
