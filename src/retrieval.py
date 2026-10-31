
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class EvidenceRetriever:
    """Retrieve relevant document chunks using semantic similarity."""

    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []

    def index_chunks(self, chunks: list[dict]) -> None:
        """Convert chunks into embeddings and build a searchable index."""

        if not chunks:
            raise ValueError("Cannot index an empty list of chunks.")

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        embeddings = np.asarray(embeddings, dtype=np.float32)

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)

        # Keep each embedding linked to its source and page metadata.
        self.chunks = chunks

    def retrieve(self, question: str, top_k: int = 5) -> list[dict]:
        """Return the most relevant chunks for a question."""

        if self.index is None:
            raise RuntimeError("Index chunks before retrieving evidence.")

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        question_embedding = self.model.encode(
            [question],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        question_embedding = np.asarray(
            question_embedding,
            dtype=np.float32,
        )

        number_to_retrieve = min(top_k, len(self.chunks))

        scores, indices = self.index.search(
            question_embedding,
            number_to_retrieve,
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            result = self.chunks[int(index)].copy()
            result["similarity_score"] = float(score)
            results.append(result)

        return results
