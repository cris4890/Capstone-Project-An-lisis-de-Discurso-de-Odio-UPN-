"""Consolida paquetes A+B en una base SQLite nueva para el flujo E3."""
import argparse
import json
from pathlib import Path

import pandas as pd

from annotations import AnnotationStore


def consolidate(corpus_path, package_paths, destination):
    corpus_path = Path(corpus_path)
    destination = Path(destination)
    content = corpus_path.read_bytes()
    frame = pd.read_csv(corpus_path, dtype={"id_comentario": str})
    packages = [json.loads(Path(path).read_text(encoding="utf-8")) for path in package_paths]
    store = AnnotationStore.consolidate_packages(destination, packages, content, frame)
    corpus_hash = __import__("hashlib").sha256(content).hexdigest()
    completion = store.review_completion(corpus_hash, frame.id_comentario.astype(str).tolist())
    return {
        "database": str(destination.resolve()),
        "corpus_sha256": corpus_hash,
        "rows": len(frame),
        "roles": sorted(store.reviewers(corpus_hash)),
        "complete": completion["complete"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True, help="CSV exacto usado por A y B")
    parser.add_argument("--package-a", required=True, help="Paquete JSON del rol A")
    parser.add_argument("--package-b", required=True, help="Paquete JSON del rol B")
    parser.add_argument("--output", required=True, help="Ruta nueva para la base central")
    args = parser.parse_args()
    result = consolidate(args.corpus, [args.package_a, args.package_b], args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
