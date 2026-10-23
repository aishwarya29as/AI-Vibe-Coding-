# AI Question & Answering System

A Streamlit chat application that answers questions using Google's Gemini
models. Conversation history is maintained for the current Streamlit session,
so follow-up questions can refer to earlier messages.

## Features

- Chat-style Streamlit interface with separate user and assistant messages.
- Multi-turn conversation history stored in `st.session_state`.
- Gemini model and response temperature configurable through `.env`.
- Loading indicator while Gemini generates a response.
- Empty-question validation and a sidebar button to clear the conversation.
- Friendly configuration and request errors that do not show API credentials
  or raw SDK exception details.
- Unit tests use mocked Gemini clients; they do not call the live API.

## Architecture

- **`app/main.py`** — Streamlit UI, session conversation state, input
  validation, and user-facing errors.
- **`app/config/settings.py`** — loads `.env` with `python-dotenv`, validates
  settings, and keeps the API key out of the settings representation.
- **`app/prompts/qa_prompt.py`** — standalone Gemini system instruction.
- **`app/services/gemini_service.py`** — Google Gen AI client setup,
  conversation-format conversion, generation configuration, and sanitized
  Gemini errors. The UI does not make API calls directly.
- **`app/utils/logging_config.py`** — standard Python logging configuration.
- **`tests/`** — configuration and service unit tests, with mocked API calls.

## Project structure

```text
question_answering_app/
├── app/
│   ├── config/
│   │   └── settings.py
│   ├── prompts/
│   │   └── qa_prompt.py
│   ├── services/
│   │   └── gemini_service.py
│   ├── utils/
│   │   └── logging_config.py
│   └── main.py
├── tests/
│   ├── test_config.py
│   └── test_gemini_service.py
├── .env.example
├── .gitignore
├── requirements.txt
└── run.sh
```

## Prerequisites

- Python 3.10 or newer.
- Internet access to reach the Gemini API.
- A Google Gemini API key.

The default model, `gemini-3.8-flash`, is suitable for general-purpose tasks.
Confirm the model is available to your
account in the [Gemini models list](https://ai.google.dev/gemini-api/docs/models).

## Get a Google Gemini API key

Create or manage a key in [Google AI Studio](https://aistudio.google.com/apikey).
Treat it as a password: do not share it, include it in source files, or commit
it to version control.

## Install and configure

Run commands from the repository root directory.

### 1. Create a virtual environment

```sh
python -m venv .venv
```

Activate it on macOS/Linux:

```sh
source .venv/bin/activate
```

Activate it on Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation due to its execution policy, use Command Prompt
or consult your organization's policy rather than weakening security settings.

### 2. Install dependencies

```sh
python -m pip install -r requirements.txt
```

`requirements.txt` includes the Google Gen AI SDK, Streamlit, `python-dotenv`,
and pytest.

### 3. Create `.env`

Copy the example file to `.env`.

macOS/Linux:

```sh
cp .env.example .env
```

Windows Command Prompt:

```bat
copy .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace `your_gemini_api_key_here` with your own key. The
example contains:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
TEMPERATURE=0.2
```

Do not commit `.env`. The project `.gitignore` ignores `.env` files while
keeping `.env.example` trackable.

## Run the Streamlit application

From the project directory, run:

```sh
streamlit run app/main.py
```

You can also use `./run.sh` on macOS/Linux. Streamlit prints a local URL in the
terminal; open it in a browser. Stop the running application by pressing
**Ctrl+C** in the terminal where it is running.

## Run tests

With the virtual environment activated, run:

```sh
pytest
```

Or use:

```sh
python -m pytest
```

Tests mock the Google Gen AI client and use temporary or isolated environment
configuration. They require no real Gemini API key and do not make live API
requests.

## Example questions

- What is the difference between machine learning and deep learning?
- Explain how photosynthesis works in a few steps.
- Give me a concise checklist for planning a weekend trip.
- Can you explain that last point with a simple example?

The final example demonstrates a follow-up that uses prior conversation
messages.

## Change the Gemini model and generation settings

Edit `.env`:

```dotenv
GEMINI_MODEL=gemini-3.8-flash
TEMPERATURE=0.2
```

Set `GEMINI_MODEL` to a model code currently available to your Gemini API
account. Refer to Google's [supported models documentation](https://ai.google.dev/gemini-api/docs/models)
before changing it. `TEMPERATURE` controls response variation and must be a
number from `0` through `2`; lower values are generally more deterministic.
The default model is `gemini-3.8-flash` and the default temperature is `0.2`.
Restart Streamlit after changing `.env`.

## Troubleshooting

- **Missing API key:** Ensure `.env` is in the project directory and contains a
  non-empty `GEMINI_API_KEY`. Create it by copying `.env.example`.
- **Authentication or permission error:** Check that the key is valid, enabled
  for the Gemini API, and has not been revoked. Do not paste the key into an
  issue or log.
- **Model unavailable:** Verify the exact `GEMINI_MODEL` code against Google's
  model list and confirm access for your account.
- **Invalid temperature:** Set `TEMPERATURE` to a numeric value between `0`
  and `2`, such as `0.2`.
- **Package import errors:** Activate the project's `.venv`, then reinstall
  dependencies with `python -m pip install -r requirements.txt`.
- **Port already in use:** Start Streamlit on a different port, for example:
  `streamlit run app/main.py --server.port 8502`.
- **PowerShell activation is blocked:** Activate the environment from Command
  Prompt with `.venv\Scripts\activate.bat`, or follow your administrator's
  approved Python environment setup.

## Security considerations

- Keep the real API key in `.env`; never hard-code or commit it.
- `.env` is ignored by Git. Check `git status` before committing sensitive
  configuration.
- Do not log API keys, request headers, or complete user conversations.
- The application shows friendly errors rather than raw SDK exception details.
- Tests use fake credentials and mocked API responses; no live credentials are
  needed for testing.

## Deactivate the virtual environment

When finished, run:

```sh
deactivate
```

## Code quality and future enhancements

Keep changes aligned with PEP 8, add type hints where useful, and favor small
focused functions with clear responsibilities. Keep UI, settings, prompts,
service/API communication, and logging separated. Handle exceptions explicitly,
avoid wildcard imports and global mutable state, and never hard-code secrets or
configuration that belongs in environment variables. Add tests using mocks for
external services.

Possible future enhancements include streaming responses, configurable system
prompts, conversation export, usage metrics that exclude prompt contents, and
additional automated UI tests.
