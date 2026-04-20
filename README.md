# Strategic Agentic AI Email Assistant

**Author:** DG Rohitha  
**Version:** 2.0  
**Last Updated:** April 2026

## 📋 Project Overview

Strategic Agentic AI Email Assistant is a professional-grade AI system that intelligently generates high-quality business emails using a sophisticated multi-agent architecture. The system can generate multiple email versions simultaneously, provide real-time coaching, suggest key points, and predict recipient reactions—all without vendor lock-in through free local AI support.

### Key Capabilities

✅ **Generate Multiple Versions**: Creates up to 3 professional email versions in parallel  
✅ **One-Line Generation**: Quick email generation using minimal input  
✅ **Draft Improvement**: Refine and enhance existing email drafts  
✅ **Live Coaching**: Real-time feedback while drafting  
✅ **Smart Suggestions**: AI-powered key points and strategy recommendations  
✅ **Outcome Prediction**: Simulates recipient reactions and identifies risks  
✅ **API Key Rotation**: Automatic fallback between multiple OpenAI keys  
✅ **Free Local AI**: Works offline with Ollama or rule-based fallback  

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit (web) + React TypeScript (optional) | User interface |
| **Backend API** | FastAPI with CORS | RESTful endpoints |
| **Request Framework** | LangChain | Multi-agent orchestration |
| **LLM Models** | OpenAI (default) + Ollama (free local) | AI generation |
| **Language** | Python 3.10+ | Core implementation |
| **Concurrency** | ThreadPoolExecutor | Parallel version generation |

---

## 🧠 Agentic Workflow Architecture

```
User Input
    ↓
Intent Detection Agent → Identifies email purpose
    ↓
Situation Analysis Agent → Extracts context & urgency
    ↓
Strategy Selection Agent → Picks communication approach
    ↓
Tone Selection Agent → Determines voice & style
    ↓
[Concurrent Generation - 3 Versions]
├─ Email Generator Agent (v1)
├─ Email Generator Agent (v2)
└─ Email Generator Agent (v3)
    ↓
[Simultaneous]
├─ Email Review Agent → Quality scoring & refinement
└─ Outcome Simulator Agent → Predicts recipient reaction
    ↓
Final Output with Metadata
```

### 9 Specialized Agents

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Intent Agent** | Detects email purpose | Purpose, situation | Intent classification |
| **Situation Analysis Agent** | Analyzes context | Request, situation | Urgency, risks, focus areas |
| **Strategy Selection Agent** | Picks communication method | Intent, situation | Strategy (persuasion/apology/etc) |
| **Tone Selection Agent** | Determines email voice | Preference, strategy | Tone (formal/friendly/etc) |
| **Email Generator Agent** | Drafts email | All above + key points | Subject + email body |
| **Email Review Agent** | Quality assurance | Draft + context | Quality score + refinements |
| **Outcome Simulator Agent** | Predicts reaction | Recipient, email | Reaction % + risk level |
| **Email Coach Agent** | Live feedback | Current draft | Tone check + suggestions |
| **Suggestor Agent** | Recommends points | Purpose, recipient | Key point ideas |

---

## 📁 Project Structure

```
Strategic-ai-email-generator/
│
├─ app.py                          # Streamlit UI (web interface)
├─ main.py                         # FastAPI backend (REST API)
├─ requirements.txt                # Python dependencies
├─ .env.example                    # Environment template
├─ .env                            # Local runtime config (add your keys here)
├─ README.md                       # Project documentation
│
├─ src/
│  ├─ __init__.py
│  ├─ config.py                   # Multi-key API management
│  ├─ models.py                   # Data classes (EmailRequest, etc)
│  ├─ prompts.py                  # Agent prompt templates
│  ├─ utils.py                    # JSON parsing, text normalization
│  ├─ orchestrator.py             # Multi-agent workflow coordinator
│  ├─ model_manager.py            # API key rotation & fallback
│  ├─ fallback_engine.py          # Rule-based generation (free)
│  │
│  └─ agents/
│     ├─ __init__.py
│     ├─ base.py                 # BaseAgent class
│     ├─ intent_agent.py         # Email purpose detection
│     ├─ situation_agent.py      # Context analysis
│     ├─ strategy_agent.py       # Strategy selection
│     ├─ tone_agent.py           # Tone determination
│     ├─ email_generator_agent.py # Email drafting
│     ├─ review_agent.py         # Quality review
│     ├─ outcome_simulator_agent.py # Reaction prediction
│     ├─ coach_agent.py          # Live feedback
│     └─ suggestor_agent.py      # Point suggestions
│
├─ examples/
│  └─ sample_inputs_outputs.md    # Usage examples
│
├─ frontend/                       # Optional React frontend
│  ├─ src/
│  ├─ package.json
│  └─ tsconfig.json
│
└─ .git/                          # Version control
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Virtual environment
- API key (OpenAI) OR local Ollama OR free fallback mode

### Installation

1. **Clone Repository**
   ```powershell
   git clone https://github.com/DG-ROHITHA/Strategic-ai-email-generator.git
   cd Strategic-ai-email-generator
   ```

2. **Setup Virtual Environment**
   ```powershell
   python -m venv .venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```powershell
   cp .env.example .env
   ```

5. **Add API Keys (Optional)**
   
   Edit `.env` with your configuration:
   
   **Option A: Use OpenAI (Paid)**
   ```env
   OPENAI_API_KEY=sk-proj-your-key-here
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_TEMPERATURE=0.3
   OPENAI_BASE_URL=https://api.openai.com/v1
   ```
   
   **Option B: Multiple Keys with Rotation**
   ```env
   OPENAI_API_KEY=sk-proj-key1,sk-proj-key2,sk-proj-key3
   ```
   
   **Option C: Ollama Local (Free)**
   ```env
   OLLAMA_MODEL=llama3.2:3b
   OLLAMA_BASE_URL=http://localhost:11434
   ```

---

## 📱 Running the Application

### Option 1: Streamlit Web UI (Recommended for Beginners)

```powershell
streamlit run app.py
```

Visit: `http://localhost:8501`

**Features in Web UI:**
- Select generation mode (OpenAI/Ollama/Fallback)
- Specify email purpose, recipient, situation
- Choose tone preference
- Set number of versions (1-3)
- Drafting style (concise/balanced/detailed)
- Improve existing drafts option
- View all versions side-by-side
- Copy-to-clipboard functionality

### Option 2: FastAPI REST Backend

```powershell
python main.py
```

API runs on: `http://localhost:8000`

**Available Endpoints:**

#### POST `/generate` - Generate Email Versions
```json
{
  "email_purpose": "Request a timeline extension",
  "recipient": "Project Manager",
  "situation": "Technical issues delayed delivery",
  "tone_preference": "professional",
  "key_points": "2-day extension needed",
  "drafting_style": "balanced",
  "num_versions": 3,
  "improve_existing_email": false,
  "existing_email": ""
}
```

Response includes:
- Subject line
- 3 email versions
- Quality score
- Outcome simulation (recipient reaction %)
- Risk assessment

#### POST `/suggest-points` - Get Key Point Suggestions
```json
{
  "email_purpose": "Request a timeline extension",
  "recipient": "Project Manager"
}
```

#### POST `/coach` - Get Live Feedback
```json
{
  "current_draft": "Dear Manager, I need more time...",
  "recipient": "Project Manager",
  "intent": "request"
}
```

#### GET `/health` - Check API Status
```
http://localhost:8000/health
```

---

## 🎯 Usage Examples

### Example 1: Generate 3 Professional Email Versions

**Input:**
- Purpose: Request a timeline extension
- Recipient: Sarah Ahmed (Project Manager)
- Situation: Technical issues delayed project completion
- Tone: Professional
- Key Points:
  - Ask for 2-day extension
  - Provide risk mitigation plan

**Output:**
```
Version 1: Formal negotiation approach
"Dear Sarah, I am writing to discuss a timeline extension..."

Version 2: Direct request approach
"Sarah, our team encountered technical challenges..."

Version 3: Solution-focused approach
"To better serve project goals, we propose..."
```

### Example 2: One-Line Email Generation

For quick emails, provide minimal context:
- Purpose: "Follow-up on proposal"
- Recipient: "Client contact"
- Situation: (leave blank for auto-detection)
- Key Points: (single line)

System generates a professional email in seconds using rule-based fallback engine.

### Example 3: Improve an Existing Draft

Enable "Improve Existing Draft" and paste your draft:

**Original:**
"hey, we need more time lol"

**Improved Version:**
"Dear [Recipient], thank you for your understanding regarding the project timeline. Due to unforeseen technical challenges, we respectfully request a 2-day extension..."

---

## 🔧 Configuration Guide

### API Key Management

#### Single Key
```env
OPENAI_API_KEY=sk-proj-single-key
```

#### Multiple Keys (Rotation)
```env
OPENAI_API_KEY=sk-proj-key1,sk-proj-key2,sk-proj-key3
```

The system automatically rotates keys when quota is exceeded. On quota error:
1. Tries key 1 → fails
2. Rotates to key 2 → retries
3. Rotates to key 3 → retries
4. Falls back to local AI or rules

#### Model Selection

```env
# OpenAI model
OPENAI_MODEL=gpt-4o-mini

# Temperature (0.0-1.0, default 0.3 for consistency)
OPENAI_TEMPERATURE=0.3

# Custom OpenAI-compatible endpoint
OPENAI_BASE_URL=https://api.openai.com/v1
```

#### Local AI (Ollama)

```env
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434
```

**Install Ollama:**
```powershell
winget install -e --id Ollama.Ollama
```

**Run Local Model:**
```powershell
ollama run llama3.2:3b
```

---

## 📊 Features Deep Dive

### 1. Multi-Version Generation

Generate 1-3 versions concurrently using ThreadPoolExecutor:
- **Version 1:** Formal approach
- **Version 2:** Casual/friendly approach
- **Version 3:** Strategic negotiation approach

Each version considers the same context but with different emphasis.

### 2. Drafting Styles

| Style | Use Case | Example |
|-------|----------|---------|
| **Concise** | Busy recipients, urgent matters | Short, direct sentences |
| **Detailed** | Complex topics, full explanations | Comprehensive context |
| **Balanced** | General professional communication | Mix of brevity and detail |

### 3. Live Coaching Feedback

Real-time suggestions while typing:
- ✓ Tone appropriateness
- ✓ Aggressive language detection
- ✓ Clarity improvements
- ✓ Grammar and punctuation
- ✓ Alternative wording suggestions

### 4. Outcome Simulation

Predicts recipient reaction:
- Positive probability %
- Neutral probability %
- Negative probability %
- Risk level (low/medium/high)
- Potential objections list

### 5. Intelligent Key Point Suggestions

Suggests relevant talking points based on:
- Email purpose
- Recipient role/title
- Industry context (inferred)
- Best practices

---

## 💳 Free Usage (No API Required)

The system includes **three free options:**

### Option 1: Local Fallback Rules (Fastest)
No dependencies. Uses built-in rule engine.
```env
# Leave OPENAI_API_KEY empty
```

### Option 2: Ollama Local AI (Best Quality)
Free, open-source models running locally.
```powershell
ollama run llama3.2:3b
```

### Option 3: OpenAI API (Premium Features)
Full LLM power with unlimited versions and advanced agents.
```env
OPENAI_API_KEY=sk-proj-your-key
```

---

## ⚠️ Troubleshooting

### Error: "No .env file found"
**Solution:** Copy template and add your keys:
```powershell
cp .env.example .env
```

### Error: "insufficient_quota"
OpenAI account has no credits. Options:
- Add credits to OpenAI account
- Use multiple keys (rotation feature)
- Switch to Ollama local mode
- Use free fallback rules

### Error: "Connection refused" (Ollama)
Ollama not running. Start it:
```powershell
ollama run llama3.2:3b
```

### Error: "Module not found"
Reinstall dependencies:
```powershell
pip install -r requirements.txt
```

---

## 🔐 Security Best Practices

1. **Never commit .env file** (already in .gitignore)
2. **Rotate API keys regularly** (supports comma-separated keys)
3. **Use environment variables** for sensitive data
4. **Keep dependencies updated** (run `pip install --upgrade -r requirements.txt`)
5. **Review generated emails** before sending critical communications

---

## 📈 Performance Tips

1. **Use fewer versions** for faster generation (num_versions=1)
2. **Set lower temperature** (0.1-0.3) for consistent results
3. **Use concise style** for faster processing
4. **Run Ollama locally** for offline-first workflows
5. **Batch multiple requests** via FastAPI for efficiency

---

## 🚀 Advanced Features

### Concurrent Generation
The orchestrator uses ThreadPoolExecutor to generate multiple versions in parallel:
- Reduces latency from 3x to ~1.5x of single generation
- Thread-safe LLM interactions
- Automatic fallback if version fails

### API Key Rotation Strategy
ModelManager implements smart rotation:
- Tries current key first
- Rotates on quota errors
- Falls back to local model after all keys exhausted
- Logs all rotation attempts for debugging

### Outcome Prediction
OutcomeSimulatorAgent predicts:
- Recipient's likely emotional response
- Probability distribution across reactions
- Risk factors specific to situation
- Potential objections and how to address them

---

## 📚 Examples

See [examples/sample_inputs_outputs.md](examples/sample_inputs_outputs.md) for:
- Follow-up email example
- Apology email example
- Negotiation email example
- Improvement example

---

## 🛠️ Future Enhancements

Planned features:
- ✓ Gmail integration for direct sending
- ✓ Voice input for hands-free operation
- ✓ Meeting transcript to email generation
- ✓ Email sentiment detection
- ✓ A/B testing for email opens/clicks
- ✓ CRM integration (Salesforce, HubSpot)
- ✓ Multi-language support
- ✓ Email analytics dashboard

---

## 📝 Notes for Developers

### Adding New Agents

1. Create new file: `src/agents/new_agent.py`
2. Inherit from `BaseAgent`
3. Implement `run()` method
4. Add prompt template in `src/prompts.py`
5. Import in orchestrator and use

### Extending Prompts

All agent prompts are in `src/prompts.py` for easy customization. Modify prompts to:
- Change tone
- Adjust output format
- Add new constraints
- Tailor for specific industries

### API Integration

FastAPI backend `main.py` is production-ready and can be deployed to:
- AWS Lambda / ECS
- Google Cloud Run
- Azure App Service
- Docker containers
- Heroku platform

---

## 📞 Support

For issues or questions:
1. Check [troubleshooting section](#-troubleshooting)
2. Review [examples/sample_inputs_outputs.md](examples/sample_inputs_outputs.md)
3. Check `.env` configuration
4. Verify API keys are valid and have credits

---

## 📄 License

Open source project. Feel free to fork, modify, and contribute.

---

## ✨ Acknowledgments

Built with:
- OpenAI API
- LangChain framework
- Streamlit
- FastAPI
- Ollama

---

**Last Updated:** April 2026  
**Author:** DG Rohitha  
**Repository:** https://github.com/DG-ROHITHA/Strategic-ai-email-generator
