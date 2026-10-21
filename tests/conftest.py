"""Clasificación técnica de las pruebas; aceptación formal no se automatiza."""
import pytest


def pytest_configure(config):
    for marker, description in {
        "unitaria": "Función o componente acotado con entradas controladas",
        "integracion": "Colaboración de componentes, persistencia o artefactos",
        "sistema": "Recorrido de aplicación con Streamlit AppTest; no navegador real",
        "aceptacion": "Criterio de usuario; requiere registro humano de aceptación",
    }.items():
        config.addinivalue_line("markers", f"{marker}: {description}")


def pytest_collection_modifyitems(items):
    system_names = {"test_three_subsystems_and_optional_history", "test_internal_annotation_separate",
                    "test_corrupt_history_is_reported_without_overwrite", "test_invalid_run_can_return_to_demo",
                    "test_streamlit_default_and_sections"}
    unit_workflow = {"test_minimization_and_context", "test_selection_uses_validation_only",
                     "test_metrics_counts_and_missing_class", "test_bootstrap_deterministic"}
    for item in items:
        file = item.path.name
        name = item.originalname or item.name
        explicit = [kind for kind in ["unitaria", "integracion", "sistema", "aceptacion"] if item.get_closest_marker(kind)]
        if explicit:
            kind = explicit[0]
        elif file == "test_functional_journey.py" or name in system_names:
            kind = "sistema"
        elif file in {"test_annotation_report.py", "test_pilot_corpus.py"}:
            kind = "integracion"
        elif file == "test_security.py":
            kind = "unitaria" if name == "test_local_server_defaults" else "integracion"
        elif file == "test_workflow.py":
            kind = "unitaria" if name in unit_workflow else "integracion"
        elif name == "test_legacy_and_v2_artifacts_remain_distinct":
            kind = "integracion"
        else:
            kind = "unitaria"
        item.add_marker(getattr(pytest.mark, kind))
        item.user_properties.append(("tipo_prueba", kind))
