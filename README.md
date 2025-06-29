# Movie-RAG Demo

A minimal Retrieval‑Augmented Generation (RAG) prototype that answers natural‑language questions against a **SQLite** movie database using **AdalFlow** for pipeline orchestration and a local **qwen3 0.6‑B** model served by **Ollama**.

---

## 1  Project structure

| File              | Purpose                                                                      |
| ----------------- | ---------------------------------------------------------------------------- |
| `schema.sql`      | DDL for the relational schema (movies, genres, actors, and junction tables). |
| `create_db.py`    | Creates `movies.db` from `schema.sql`.                                       |
| `populate_db.py`  | Inserts \~20 sample rows per table for demo queries.                         |
| `data_classes.py` | `@dataclass` containers used to pass objects between AdalFlow components.    |
| `main.py`         | End‑to‑end RAG pipeline: NL → SQL → SQLite → Answer.                         |
| `movies.db`       | SQLite database generated by the two scripts above.                          |
| `README.md`       | This guide.                                                                  |

---

## 2  Prerequisites

* **Python 3.9 +**  (recommend `python -m venv rag-env`)
* **Ollama ≥ 0.6.6**  (`ollama version`)
* **qwen3:0.6b** model pulled locally (`ollama pull qwen3:0.6b`)
* Internet access is **not** required once the model and packages are installed.

Install Python dependencies:

```bash
pip install adalflow jinja2 ollama
```

---

## 3  Quick start

```bash
# 1. Build the database
python create_db.py
python populate_db.py

# 2. Run the RAG demo
python main.py
```

Example interaction (stdin/stdout):

```text
User  : Who acted in Interstellar?
Assistant:
The actors who starred in *Interstellar* are Matthew McConaughey and Sean Astin.
```

---

## 4  How it works

1. **`SQLGenerator`** (AdalFlow component) turns the user question into SQLite‑flavoured SQL.
2. **`SQLExecutor`** runs the query against `movies.db`.
3. **`AnswerGenerator`** converts raw rows into a short natural‑language reply.
4. The three components are wrapped in `RagPipeline` for a single‑call interface.

All components live inside `main.py` and inherit from `adalflow.Component` using the `call()` method.

---

## 5  Prompt engineering guidelines

* A compact **data dictionary** is added to the LLM prompt to reduce hallucinations.
* Triple‑back‑tick blocks are stripped with `extract_sql()` to obtain clean SQL before execution.

---

## 6  Extending the demo

| Idea                | Hint                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------ |
| **REST API**        | Wrap `rag_pipeline` in FastAPI (`POST /ask`).                                        |
| **Larger database** | Swap the sample data or connect to PostgreSQL; only `SQLExecutor` needs changes.      |
| **Prompt tuning**   | Replace fixed prompt strings with `adalflow.Parameter` and call `Component.train()`. |
| **Guard‑rails**     | Add schema‑aware validation (e.g. `sqlparse`, `PRAGMA explain`).                     |

---

## 7  Known limitations

* No pagination or `LIMIT` safeguard—large result sets may overflow context.
* The LLM is not sandboxed; malicious questions could inject DDL unless filtered.
* Sample data is tiny; statistics‑based prompts may under‑represent edge cases.
