# Smart Librarian

Smart Librarian is an AI-powered book assistant that combines semantic retrieval (RAG), multi-agent orchestration, and image generation in a modern Streamlit UI.

The app helps users:
- find books by theme or intent,
- get title-specific summaries,
- ask follow-up questions about the current book,
- generate visual interpretations for stories.

## Core Features

### 1. Retrieval-Augmented Recommendations (RAG)
- Uses ChromaDB as a persistent vector store.
- Embeds book metadata with `text-embedding-3-small`.
- Retrieves top matching books from local data before recommendation.
- Ensures final recommendations stay grounded in retrieved titles.

### 2. Intent-Based Conversation Routing
- A dedicated intent agent classifies each user message into flows like:
- new recommendation,
- exact title summary,
- follow-up on current book,
- image generation,
- other/general.

### 3. Multi-Agent Workflow
- `intent_agent` decides the route.
- `recommendation_agent` selects the best book from retrieved candidates.
- `summary_agent` fetches exact summaries via local tools.
- `follow_up_agent` answers contextual follow-up questions.
- `image_generation_agent` builds a strong visual prompt for image generation.

### 4. AI Image Generation
- Generates images with `gpt-image-1`.
- Saves image files in `generated_images/`.
- Supports two UX paths that converge to the same Image Card component:
- Visualize button from a Book Card,
- direct chat request (for example: "Generate an image inspired by The Hobbit").

### 5. Premium Streamlit UI
- Custom hero, themed chat bubbles, and styled cards.
- Dedicated Book Card and Image Card components.
- Tool-specific loading states:
- `Searching the library...`
- `Imagining "<title>"...`
- Error cards instead of plain error lines.
- Custom sidebar with:
- New Conversation,
- capabilities list,
- status indicator,
- about section.

### 6. Conversation Memory and Reset
- Tracks current book title, summary, and recommendation reason.
- `New Conversation` clears both UI messages and backend conversation state.

## Tech Stack

- Python 3.10+
- Streamlit
- OpenAI Agents SDK
- OpenAI API (chat + embeddings + image)
- ChromaDB
- python-dotenv

## Project Structure

```text
Smart_Librarian/
	app.py                       # CLI entrypoint
	streamlit_app.py             # Streamlit UI entrypoint
	config.py                    # OpenAI/API configuration
	vector_store.py              # ChromaDB setup and retrieval
	state.py                     # Conversation state dataclass
	models.py                    # Typed models for agent outputs

	app_agents/                  # Agent factories (intent, summary, etc.)
	app_tools/                   # Tool functions (book tools, image tools)
	app_guardrails/              # Guardrails (bad words filter)
	repositories/                # Local data access layer
	services/                    # Core orchestration services
	components/                  # UI components (book card, image card)
	styles/                      # Custom CSS
	data/                        # Local JSON data (books, bad words)
	chroma_db/                   # Persistent vector DB files
	generated_images/            # Generated image outputs
```

## Setup

### 1. Clone

```bash
git clone <your-repo-url>
cd Smart_Librarian
```

### 2. Create and activate virtual environment

Windows (PowerShell):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

If you maintain a lock/dependency file, install from that.
Otherwise install required packages directly:

```bash
pip install streamlit openai chromadb python-dotenv
```

If your environment requires a separate Agents SDK package, install it as well.

### 4. Configure environment variables

Create a `.env` file in project root:

```env
ENDAVA_OPENAI_API_KEY=your_openai_api_key_here
```

## Initialize Vector Store

Before first recommendation flow, initialize Chroma with local books:

```bash
py -3 vector_store.py
```

This creates/updates the persistent collection in `chroma_db/`.

## Run the App

### Streamlit UI

```bash
streamlit run streamlit_app.py
```

### CLI Mode

```bash
py -3 main.py
```

## User Flows

### A. Recommendation flow
1. User asks by mood/theme.
2. Retriever fetches top semantic matches.
3. Recommendation agent picks one valid title.
4. Summary is fetched and presented in Book Card.

### B. Exact title flow
1. User asks for a specific title.
2. Repository validates title.
3. Summary agent retrieves exact summary.
4. Current book context is updated.

### C. Follow-up flow
1. User asks a contextual question.
2. Follow-up agent answers only about current book.
3. Avoids recommending unrelated books.

### D. Image generation flow
1. Trigger via Book Card button or direct chat prompt.
2. Image agent builds visual prompt.
3. Image API generates and saves PNG.
4. Streamlit attaches `message["image"]` and renders Image Card.

## Guardrails and Validation

- Input guardrail protects against abusive language.
- Recommendation title is validated against retrieved candidates.
- App handles missing title, empty summary, timeout, and generation failures.
- UI converts known failures into styled error cards.

## Troubleshooting

### API key missing
Symptom: startup/config error about missing key.
Fix: ensure `.env` exists and `ENDAVA_OPENAI_API_KEY` is set.

### Empty retrieval results or Chroma errors
Symptom: recommendation flow fails or says collection is empty.
Fix: run `py -3 vector_store.py` to initialize embeddings.

### Image generated but not displayed as card
Symptom: only text/path appears.
Fix: ensure Streamlit runs latest code and that generated file exists in `generated_images/`.

### Stale conversation context
Symptom: follow-up/image refers to old book.
Fix: click `New Conversation` in sidebar (resets UI + backend state).

## Configuration Notes

In `config.py`:
- `MODEL_NAME` controls language model usage.
- `IMAGE_MODEL_NAME` controls image generation model.

In `vector_store.py`:
- `EMBEDDING_MODEL` controls embeddings model.
- `COLLECTION_NAME` identifies the Chroma collection.

## Security and Privacy

- API keys are read from environment variables.
- Keep `.env` out of version control.
- Generated image files are stored locally in `generated_images/`.

## Roadmap Ideas

- Add export/share for generated image cards.
- Add citations/source snippets from retrieved context.
- Add multilingual UI toggle (RO/EN).
- Add automated tests for message routing and UI payload transforms.

## Author

Ciobanu Robert-Andrei
