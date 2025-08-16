# app/rag/build_faiss_index.py
"""
Usage:
  python -m app.rag.build_faiss_index \
      --input data/corpus.jsonl \
      --out_dir data

Input JSONL schema per line:
  {"id": "doc123", "title": "Oliver Reed", "url": "https://...", "text": "document text ..."}
"""
from __future__ import annotations
import argparse, json, os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="JSONL file path")
    p.add_argument("--out_dir", default="data", help="Directory to write index + arrays")
    p.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    meta, texts = [], []

    with open(args.input, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            assert {"id","title","url","text"}.issubset(d.keys()), \
                "Each JSONL line must have id,title,url,text"
            meta.append({"id": d["id"], "title": d["title"], "url": d["url"]})
            texts.append(d["text"])

    model = SentenceTransformer(args.model)
    emb = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    dim = emb.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(emb)

    faiss.write_index(index, os.path.join(args.out_dir, "faiss.index"))
    np.save(os.path.join(args.out_dir, "meta.npy"), np.array(meta, dtype=object))
    np.save(os.path.join(args.out_dir, "texts.npy"), np.array(texts, dtype=object))
    print(f"Built FAISS index with {len(texts)} docs into {args.out_dir}")

if __name__ == "__main__":
    main()
