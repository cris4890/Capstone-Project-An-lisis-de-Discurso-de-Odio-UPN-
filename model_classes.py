"""
Definición de Clases y Estimadores de Modelos NLP
=================================================

Contiene las arquitecturas personalizadas para el proyecto Capstone:
- RuleBasedClassifier: Línea base heurística de reglas y lexicón bilingüe.
- TransformerClassifier: Envoltorio para inferencia y ajuste fino de Hugging Face.
- TextDataset: Dataset compatible con PyTorch DataLoader.
"""

import copy
import logging
import re
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.utils.class_weight import compute_class_weight
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import BertForSequenceClassification, BertTokenizer

logger = logging.getLogger("ModelClasses")

TARGET_CLASSES = ["Odio", "Ofensivo", "Neutro"]
LABEL_TO_ID = {label: i for i, label in enumerate(TARGET_CLASSES)}
ID_TO_LABEL = {i: label for i, label in enumerate(TARGET_CLASSES)}


class RuleBasedClassifier:
    """
    Clasificador Heurístico basado en reglas léxicas y detección de patrones bilingües.
    Permite establecer la línea base de desempeño mínima requerida.
    """

    HATE_PATTERNS = [
        # Patrones discriminatorios / odio (ES)
        r"\binmigrantes?\b", r"\bextranjeros?\b", r"\bdegenerados?\b", r"\bfeminazis?\b",
        r"\blacra\b", r"\brefugiados?\b", r"\bmaric[oó]n(?:es)?\b", r"\bmarr[oó]n(?:es)?\b",
        r"\bjud[ií]os?\b", r"\bmendigos?\b", r"\bgitanos?\b", r"\bmutilan\b",
        r"\bescoria\b", r"\bplaga\b", r"\binvaden?\b", r"\blimpien\b", r"\bbasurero\b",
        r"\bperversi[oó]n\b", r"\btrans\b",
        # Discriminatory / hate patterns (EN)
        r"\billegal immigrants?\b", r"\bborder\b", r"\btrans ideology\b", r"\bperverts?\b",
        r"\bparasites?\b", r"\bethnic(?: groups)?\b", r"\bmuslim(?: refugees)?\b",
        r"\bsharia\b", r"\bpride parades?\b", r"\binvaders?\b", r"\bgroomers?\b",
        r"\bsubhumans?\b", r"\bdepopulate\b", r"\bvoting rights\b", r"\bcancer\b",
        r"\bghetto\b",
    ]

    OFFENSIVE_PATTERNS = [
        # Insultos directos / agresiones personales comunes (ES)
        r"\btont[oa]s?\b",
        r"\bbrut[oa]s?\b",
        r"\best[uú]pid[oa]s?\b",
        r"\bidiotas?\b",
        r"\bno sirves?\b",
        r"\bin[uú]t(?:il|iles)\b",
        r"\bbasuras?\b",
        r"\bimb[eé]cil(?:es)?\b",
        r"\bpayas[oa]s?\b",
        r"\bmierdas?\b",
        r"\bfracasad[oa]s?\b",
        r"\bverg[uü]enza ajena\b",
        r"\blamebotas\b",
        r"\busurer[oa]s?\b",
        r"\bsoplapollez\b",
        r"\bp[uú]drete\b",
        r"\bput[ao]s?\b",
        r"\bnpc\b",
        r"\bcringe\b",
        r"\bretrasad[oa]s?\b",
        r"\bsimi[oa]s?\b",
        r"\bmamadas?\b",
        r"\batropellen\b",
        r"\bbocazas\b",
        r"\bc[aá]llate\b",
        r"\basn[oa]s?\b",
        r"\bdesinstala\b",
        r"\bpendej[oa]s?\b",
        r"\bmalparid[oa]s?\b",
        # Insultos directos / agresión personal común (EN)
        r"\bdumb\b",
        r"\bfool(?:s|ish)?\b",
        r"\buseless\b",
        r"\bjerk(?:s)?\b",
        r"\bstupid(?:s)?\b",
        r"\bidiots?\b",
        r"\bfucking\b",
        r"\bfuck\b",
        r"\bclueless\b",
        r"\bbootlicker(?:s)?\b",
        r"\bbroke\b",
        r"\blazy ass\b",
        r"\bloser(?:s)?\b",
        r"\bbrain-?dead\b",
        r"\bpiece of shit\b",
        r"\bpricks?\b",
        r"\bbitch(?:es)?\b",
        r"\bbrainrotted\b",
        r"\bdumbass(?:es)?\b",
        r"\bvirgin(?:s)?\b",
        r"\bneckbeard(?:s)?\b",
        r"\byapping\b",
        r"\bretarded\b",
        r"\bshut up\b",
        r"\bcrying\b",
        r"\basshole(?:s)?\b",
        r"\bclown(?:s)?\b",
    ]

    def __init__(self) -> None:
        self.hate_regex = re.compile("|".join(self.HATE_PATTERNS), re.IGNORECASE)
        self.offensive_regex = re.compile("|".join(self.OFFENSIVE_PATTERNS), re.IGNORECASE)

    def fit(self, X: Any = None, y: Any = None) -> "RuleBasedClassifier":
        """Compatibilidad con interfaz Scikit-Learn."""
        return self

    def predict_single(self, text: str) -> str:
        """Clasifica un comentario individual según precedencia: Odio > Ofensivo > Neutro."""
        if not isinstance(text, str):
            return "Neutro"
        if self.hate_regex.search(text):
            return "Odio"
        if self.offensive_regex.search(text):
            return "Ofensivo"
        return "Neutro"

    def predict(self, texts: Union[str, pd.Series, List[str], np.ndarray]) -> np.ndarray:
        """Predice un lote o un comentario individual."""
        if isinstance(texts, str):
            texts = [texts]
        return np.array([self.predict_single(t) for t in texts])


class TextDataset(Dataset):
    """Dataset de PyTorch para tokenización bajo demanda."""

    def __init__(self, texts: List[str], labels: Optional[List[int]], tokenizer: BertTokenizer, max_len: int = 128):
        self.texts = list(texts)
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_len,
            padding="max_length",
            return_tensors="pt",
        )
        item = {key: val.squeeze(0) for key, val in encoding.items()}
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


class TransformerClassifier:
    """
    Envoltorio modular para entrenamiento y predicción con Transformers ligeros (bert-tiny).
    Implementa early checkpointing según el desempeño en validación.
    """

    def __init__(
        self,
        model_name: str = "prajjwal1/bert-tiny",
        num_epochs: int = 8,
        batch_size: int = 8,
        lr: float = 1e-4,
    ) -> None:
        self.model_name = model_name
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.lr = lr
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        logger.info("Inicializando Tokenizer y Modelo Transformer (%s) en dispositivo: %s", self.model_name, self.device)
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.model = BertForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=len(TARGET_CLASSES),
            id2label=ID_TO_LABEL,
            label2id=LABEL_TO_ID,
        )
        self.model.to(self.device)

    def fit(
        self,
        X_train: pd.Series,
        y_train: pd.Series,
        X_val: pd.Series,
        y_val: pd.Series,
    ) -> "TransformerClassifier":
        """Entrena el modelo con ajuste fino y retiene el mejor estado evaluado en validación."""
        from sklearn.metrics import f1_score

        y_train_ids = [LABEL_TO_ID[label] for label in y_train]
        y_val_ids = [LABEL_TO_ID[label] for label in y_val]

        train_dataset = TextDataset(X_train.tolist(), y_train_ids, self.tokenizer)
        val_dataset = TextDataset(X_val.tolist(), y_val_ids, self.tokenizer)

        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)

        class_weights = compute_class_weight(
            "balanced",
            classes=np.array([0, 1, 2]),
            y=np.array(y_train_ids),
        )
        class_weights_tensor = torch.tensor(class_weights, dtype=torch.float).to(self.device)
        loss_fn = nn.CrossEntropyLoss(weight=class_weights_tensor)

        optimizer = AdamW(self.model.parameters(), lr=self.lr, weight_decay=0.01)

        best_val_macro_f1 = -1.0
        best_state_dict = copy.deepcopy(self.model.state_dict())

        logger.info("Iniciando ajuste fino del Transformer (%d épocas)...", self.num_epochs)
        for epoch in range(1, self.num_epochs + 1):
            self.model.train()
            total_train_loss = 0.0

            for batch in train_loader:
                optimizer.zero_grad()
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)

                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                loss = loss_fn(outputs.logits, labels)
                loss.backward()
                optimizer.step()
                total_train_loss += loss.item()

            avg_train_loss = total_train_loss / len(train_loader)

            self.model.eval()
            val_preds: List[int] = []
            val_true: List[int] = []

            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch["input_ids"].to(self.device)
                    attention_mask = batch["attention_mask"].to(self.device)
                    outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
                    val_preds.extend(preds)
                    val_true.extend(batch["labels"].numpy())

            val_macro_f1 = f1_score(val_true, val_preds, average="macro", zero_division=0)
            logger.info(
                "Época %d/%d - Pérdida Train: %.4f | Macro-F1 (Val): %.4f",
                epoch,
                self.num_epochs,
                avg_train_loss,
                val_macro_f1,
            )

            if val_macro_f1 > best_val_macro_f1:
                best_val_macro_f1 = val_macro_f1
                best_state_dict = copy.deepcopy(self.model.state_dict())

        self.model.load_state_dict(best_state_dict)
        logger.info("Mejor Macro-F1 en Validación para Transformer: %.4f", best_val_macro_f1)
        return self

    def predict(self, texts: Union[str, pd.Series, List[str], np.ndarray]) -> np.ndarray:
        """Genera predicciones de texto en formato string ('Odio', 'Ofensivo', 'Neutro')."""
        if isinstance(texts, str):
            texts = [texts]
        self.model.eval()
        dataset = TextDataset(list(texts), None, self.tokenizer)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)
        predictions: List[str] = []

        with torch.no_grad():
            for batch in loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
                predictions.extend([ID_TO_LABEL[p] for p in preds])

        return np.array(predictions)
