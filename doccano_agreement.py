"""Class agreement on original submissions, separate from assisted revisions."""
from collections import Counter
CLASSES = ['Odio', 'Ofensivo', 'Neutro']

def compare(a_rows, b_rows):
    def index(rows):
        result = {}
        for row in rows:
            key = row['id_comentario']
            if key in result:
                raise ValueError('Identificador duplicado')
            result[key] = row
        return result
    a, b = index(a_rows), index(b_rows)
    if set(a) != set(b):
        raise ValueError('Las muestras no contienen las mismas unidades')
    matrix = [[0]*3 for _ in CLASSES]
    differences, excluded = [], []
    for uid, left in a.items():
        right = b[uid]
        if left['texto'] != right['texto']:
            raise ValueError('El texto de una unidad no coincide')
        x, y = left['etiqueta_normalizada'], right['categoria']
        detail = dict(id_comentario=uid,numero=left['numero_archivo'],texto=left['texto'],
                      categoria_a=x,categoria_b=y,motivo_a=left['justificacion_original'],
                      motivo_b=right['justificacion'])
        if x not in CLASSES or y not in CLASSES:
            excluded.append(dict(**detail,motivo_exclusion='Sin categoría única válida en la respuesta original'))
            continue
        matrix[CLASSES.index(x)][CLASSES.index(y)] += 1
        if x != y:
            differences.append(detail)
    n = sum(map(sum,matrix))
    matches = sum(matrix[i][i] for i in range(3))
    observed = matches/n if n else None
    expected = sum(sum(matrix[i])*sum(row[i] for row in matrix) for i in range(3))/(n*n) if n else None
    kappa = (observed-expected)/(1-expected) if n and expected < 1 else None
    return dict(total=len(a),pares=n,coincidencias=matches,acuerdo_observado=observed,
                acuerdo_esperado=expected,kappa=kappa,clases=CLASSES,matriz_filas_a_columnas_b=matrix,
                distribucion_a=dict(zip(CLASSES,map(sum,matrix))),
                distribucion_b={c:sum(r[i] for r in matrix) for i,c in enumerate(CLASSES)},
                desacuerdos=differences,excluidos=excluded,
                alcance='Categorías originales; no evalúa objetivos o justificaciones ni acredita independencia humana.',
                habilitado_para_entrenamiento=False)
