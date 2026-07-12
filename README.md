# thnkbyd-ai-agent

Production-ready AI agent scaffold for video content creation workflows.

## Requirements

- Python 3.12
- [Ollama](https://ollama.com/) (for local LLM inference)

## Project Structure

```
thnkbyd-ai-agent/
├── app/
│   ├── agents/       # Agent definitions and orchestration
│   ├── prompts/      # Prompt templates
│   ├── tools/        # Tool integrations
│   ├── workflows/    # Multi-step workflow pipelines
│   ├── memory/       # Conversation and state memory
│   ├── config/       # Application configuration
│   ├── models/       # Pydantic data models
│   └── main.py       # Application entry point
├── outputs/          # Generated artifacts
│   ├── scripts/
│   ├── storyboards/
│   ├── images/
│   ├── audio/
│   ├── videos/
│   └── thumbnails/
└── tests/            # Test suite
```

## Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd thnkbyd-ai-agent
   ```

2. **Create a virtual environment (Python 3.12)**

   ```bash
   py -3.12 -m venv .venv
   ```

3. **Activate the virtual environment**

   Windows (PowerShell):

   ```bash
   .\.venv\Scripts\Activate.ps1
   ```

   macOS / Linux:

   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**

   ```bash
   copy .env.example .env
   ```

   Edit `.env` with your local settings.

## Usage

```bash
python -m app.main
```

## Development

Project modules are organized under `app/` following clean architecture principles. Add agents, tools, and workflows in their respective packages as features are implemented.

## License

Proprietary — THNKBYD
