# app/core/sparse_encoder.py
import torch
from typing import List, Dict
from transformers import AutoModelForMaskedLM, AutoTokenizer
from langchain_core.embeddings import Embeddings
from qdrant_client.http import models as rest


class SparseEncoder(Embeddings):
    def __init__(self, model_name: str = "yjoonjang/splade-ko-v1"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(
            model_name, cache_dir="../cache"
        ).to(self.device)
        self.model.eval()

    def _compute_splade(self, text: str) -> Dict[int, float]:
        inputs = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        ).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        splade_values = torch.log(1 + torch.relu(logits))
        pooled_values, _ = torch.max(splade_values, dim=1)
        vector = pooled_values[0]

        indices = torch.nonzero(vector).squeeze().cpu().tolist()
        values = vector[indices].cpu().tolist()

        if isinstance(indices, int):
            indices = [indices]
        if isinstance(values, float):
            values = [values]

        return rest.SparseVector(indices=indices, values=values)

    def embed_documents(self, texts: List[str]) -> List[Dict[int, float]]:
        return [self._compute_splade(text) for text in texts]

    def embed_query(self, text: str) -> Dict[int, float]:
        return self._compute_splade(text)
