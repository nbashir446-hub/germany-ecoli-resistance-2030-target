import os
import inspect
import gradio as gr

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    PromptTemplate
)
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. CONFIG & LLM SETUP ---
# Ensure you set your GROQ_API_KEY environment variable before running
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    raise SystemExit("Set the GROQ_API_KEY environment variable first (never put the key in the code).")

Settings.llm = Groq(model="openai/gpt-oss-20b", api_key=GROQ_API_KEY)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# --- 2. LLAMAINDEX VECTOR STORE SETUP ---
# Index only the chatbot text sources (results_sources.md and, if you add it, the ECDC report PDF).
# test_questions.csv and the data CSVs are not indexed.
DATA_DIR = "chatbot"
PERSIST_DIR = "storage_part3"

def build_or_load_index():
    if os.path.exists(PERSIST_DIR):
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        return load_index_from_storage(storage_context)
    docs = SimpleDirectoryReader(DATA_DIR, required_exts=[".md", ".pdf"]).load_data()
    idx = VectorStoreIndex.from_documents(docs)
    idx.storage_context.persist(persist_dir=PERSIST_DIR)
    return idx

index = build_or_load_index()

qa_template = PromptTemplate(
"""You are an assistant for a data science project about third-generation
cephalosporin-resistant E. coli in 8 EU countries (2015-2024).

RULES
- Answer ONLY from the context below. Do not use general knowledge.
- Quote numbers exactly as they appear.
- If the answer is not in the context, reply exactly: "I can't answer that from the project data."
- The project has NO forecast for future years. If asked to predict a future value, say so and
  explain that the regression only shows direction.
- Keep answers short (1-3 sentences). Say whether a number is official ECDC incidence or the
  calculated incidence when it matters.

Context:
{context_str}

Question: {query_str}
Answer:"""
)

def respond(message, history, top_k=3):
    if not message.strip():
        return "Please enter a question.", "No evidence yet."
    eng = index.as_query_engine(similarity_top_k=int(top_k), text_qa_template=qa_template)
    response = eng.query(message)
    evidence = []
    for node in getattr(response, "source_nodes", []):
        name = node.metadata.get("file_name", "unknown")
        score = f"{node.score:.2f}" if node.score is not None else "n/a"
        snippet = node.get_content().replace("\n", " ")[:300]
        evidence.append(f"**{name}** (similarity {score})\n\n> {snippet}...")
    return str(response), "\n\n---\n\n".join(evidence) or "No evidence retrieved."

# --- 3. GRADIO INTERFACE ---
theme = gr.themes.Soft(primary_hue="teal", neutral_hue="slate")

css = """
.gradio-container { background: #f4f9f9 !important; }
.banner { background: linear-gradient(90deg, #0f766e, #14b8a6);
          border-radius: 16px; padding: 24px 28px; margin-bottom: 16px; }
.banner h1, .banner p { color: white !important; }
.banner h1 { margin: 0; font-size: 2rem; }
.banner p  { margin: 6px 0 0; opacity: .95; }
.kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 16px; }
.kpi { background: white; border-left: 6px solid #14b8a6; border-radius: 12px;
       padding: 14px 18px; box-shadow: 0 2px 8px rgba(0,0,0,.06); }
.kpi b { display: block; font-size: 1.5rem; color: #0f766e; }
.kpi span { color: #475569; font-size: .85rem; }
@media (max-width: 800px) { .kpis { grid-template-columns: 1fr; } }
"""

header_html = """
<div class="banner">
  <h1>🧫 AMR Assistant: Germany and the EU</h1>
  <p>Resistant E. coli, 8 EU countries, 2015-2024. Answers come only from the project data and ECDC reports.</p>
</div>
<div class="kpis">
  <div class="kpi"><b>🇩🇪 10.2 vs 10.6</b><span>Germany latest vs 2030 target (per 100,000)</span></div>
  <div class="kpi"><b>🌍 8 countries</b><span>Germany and 7 other EU countries</span></div>
  <div class="kpi"><b>📊 ECDC</b><span>Data source, 2015-2024</span></div>
</div>
"""

if "theme" in inspect.signature(gr.Blocks.__init__).parameters:
    blocks_kwargs, launch_kwargs = dict(theme=theme, css=css), {}
else:
    blocks_kwargs, launch_kwargs = {}, dict(theme=theme, css=css)

example_questions = [
    "Is Germany on track to meet its 2030 target?",
    "Which countries are above their 2030 target?",
    "Which country is moving in the wrong direction?",
    "Why not use only the percentage resistant?",
]

with gr.Blocks(title="AMR Assistant", **blocks_kwargs) as demo:
    gr.HTML(header_html)

    with gr.Row():
        with gr.Column(scale=1, min_width=240):
            gr.Markdown("### ⚙️ Settings")
            top_k = gr.Slider(1, 5, value=3, step=1, label="Top K chunks")
            with gr.Accordion("📚 Retrieved evidence", open=True):
                evidence_box = gr.Markdown("Ask a question to see the sources.")
        with gr.Column(scale=3):
            chat = gr.ChatInterface(
                fn=respond,
                additional_inputs=[top_k],
                additional_outputs=[evidence_box],
                chatbot=gr.Chatbot(height=430, placeholder="🧫 Ask me about resistant E. coli in Germany and the EU."),
            )
            gr.Markdown("### 💡 Example questions")
            with gr.Row():
                for q in example_questions:
                    btn = gr.Button(q, size="sm")
                    btn.click(lambda q=q: q, None, chat.textbox)

if __name__ == "__main__":
    demo.launch(debug=True, **launch_kwargs)
