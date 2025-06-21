import adalflow as adal
from data_classes import *
from jinja2 import Template
import sqlite3
import re
from typing import Optional

# Accepts ```sql … ```, ```sqlite … ```, or plain ``` … ```
_SQL_FENCE_RE = re.compile(
    r"```"                       # opening fence
    r"(?:\s*(?:sqlite|sql))?"    # optional tag (sql / sqlite), case-insensitive
    r"\s*([\s\S]*?)\s*"          # captured SQL (non-greedy)
    r"```",                      # closing fence
    flags=re.IGNORECASE,
)

ollama_llm = adal.Generator(
   model_client=adal.OllamaClient(), model_kwargs={"model": "qwen3:0.6b"}
)
# response = ollama_llm(prompt_kwargs={"input_str": "What is LLM?"})

# print(response)

schema_prompt = adal.Parameter()            # ← no positional args!
schema_prompt.value = """
You are a data assistant. Convert the user question into a valid SQLite
SQL statement using the following schema:

Schema:
{{schema}}

Data descriptions:
TABLE movies
• id – a unique number for each movie
• title – the movie’s name
• year – the year it was released
• runtime_min – running time in minutes
• rating – average viewer rating (0–10 scale)
• overview – a short plot summary

TABLE genres
• id – a unique number for each genre
• name – the genre label (e.g. Drama, Action)

TABLE movie_genres  (link table)
• movie_id – points to a movie
• genre_id – points to a genre
  → one movie can have many genres

TABLE actors
• id – a unique number for each actor
• name – the actor’s full name

TABLE movie_actors  (link table)
• movie_id – points to a movie
• actor_id – points to an actor
• role – the character or part played
  → one movie can list several actors

Return ONLY the SQL. No ``` fences, codeblocks, comments, or explanations. Remember that you may have to join 3 or more tables to arrive at the query because of normalization.
"""

class SQLGenerator(adal.Component):
    def __init__(self, llm, ddl):
        super().__init__()
        self.llm  = llm
        self.ddl  = ddl
        self.template = Template(schema_prompt.value)
    def call(self, query: NLQuery) -> SQLText:
        prompt_txt = self.template.render(schema=self.ddl) + \
                    "\nQuestion: " + query.question

        # ↓ **pass prompt as a keyword argument**
        sql_raw = self.llm(prompt_kwargs={"input_str":prompt_txt})

        sql_text = _extract_text(sql_raw)
        print(f"{sql_text=}")

        return SQLText(sql=extract_sql(sql_text.strip()))


class SQLExecutor(adal.Component):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
    def call(self, sqltxt: SQLText) -> SQLResult:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(sqltxt.sql).fetchall()
        return SQLResult(rows=rows)

class AnswerGenerator(adal.Component):
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
    def call(self, inp: tuple[NLQuery, SQLResult]) -> FinalAnswer:
        q, res = inp
        prompt_txt = f"""You are a movie domain expert.
    Question: {q.question}
    SQLite returned these rows: {res.rows}

    Compose a concise answer for the user."""
        
        answer_raw = self.llm(prompt_kwargs={"input_str": prompt_txt})

        answer = _extract_text(answer_raw)
        return FinalAnswer(answer=answer.strip())

class RagPipeline(adal.Component):
    """End-to-end NL→SQL→rows→answer."""
    def __init__(self, llm, ddl: str, db_path: str):
        super().__init__()
        # Sub-components (reuse your earlier definitions)
        self.sql_gen = SQLGenerator(llm, ddl)
        self.sql_exec = SQLExecutor(db_path)
        self.ans_gen = AnswerGenerator(llm)

    def call(self, query: NLQuery) -> FinalAnswer:
        sql: SQLText       = self.sql_gen(query)
        print(f"{sql=}")
        rows: SQLResult    = self.sql_exec(sql)
        print(f"{rows=}")
        answer: FinalAnswer = self.ans_gen((query, rows))
        return answer


def _extract_text(gen_out) -> str:
    """
    Robustly pull the text from an AdalFlow GeneratorOutput or a bare string.
    Raises RuntimeError if the call failed.
    """
    # Case 1 – you got back a plain str (possible when stream=True or
    #          when the wrapper is configured to return raw strings)
    if isinstance(gen_out, str):
        return gen_out.split("</think>")[1]

    # Case 2 – normal GeneratorOutput
    if gen_out.error:
        raise RuntimeError(f"LLM call failed: {gen_out.error}")

    if gen_out.data:          # preferred
        return gen_out.data.split("</think>")[1]
    if gen_out.raw_response:  # fallback
        return gen_out.raw_response.split("</think>")[1]

    raise RuntimeError("Empty GeneratorOutput: no data or raw_response")

def extract_sql(text: str) -> Optional[str]:
    """
    Return the first SQL statement found in triple-back-tick fences.  
    If no fenced block is present but the text *looks* like SQL
    (starts with SELECT/INSERT/UPDATE/DELETE/WITH), return the whole text.
    Otherwise return None.
    """
    m = _SQL_FENCE_RE.search(text)
    if m:
        return m.group(1).strip()

    # Heuristic fallback: treat entire text as SQL if it starts with a verb.
    stripped = text.lstrip()
    if re.match(r"(?i)^(select|insert|update|delete|with)\b", stripped):
        return stripped

    return None


if __name__ == "__main__":
    with open("schema.sql") as f:
      rag_pipeline = RagPipeline(
          llm=ollama_llm,
          ddl=f.read(),
          db_path="movies.db"
      )
    q = NLQuery(question="Who acted in Interstellar?")
    reply = rag_pipeline(q)
    print(reply.answer)
