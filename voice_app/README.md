# Voice-Enabled Agentic Learning App

A local, privacy-first conversational learning system that combines AI-powered personalization with systematic curriculum coverage.

## What Makes This Special

This app solves the "customized vs comprehensive" challenge:

- **Customized**: Every conversation adapts to YOUR specific role, challenges, and context
- **Comprehensive**: Systematically covers all 13 modules and key concepts
- **Conversational**: Feels like talking to a thoughtful coach, not a chatbot
- **Local & Private**: Runs entirely on your machine using Ollama
- **Voice-Enabled**: Support for spoken conversation (optional)

## Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Ollama** installed and running

### Installation

```bash
# 1. Install Ollama (if not already installed)
# Visit https://ollama.ai or use:
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull a language model
ollama pull llama3.2  # or mistral, llama2, etc.

# 3. Start Ollama server
ollama serve

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Run the app
python app_gradio.py
```

The app will open at `http://localhost:7860`

## How It Works

### The Customization Engine

Every interaction includes your context:

```python
Learner: Alex
Role: Product Manager at SaaS company
Challenges:
  - Project delays from unclear requirements
  - Cross-team coordination breakdowns
Previous Insights:
  - Module 00: Root cause is lack of early stakeholder alignment
  - Module 01: Pattern across all challenges is coordination
```

The AI uses THIS context in EVERY response, making everything relevant to your situation.

### The Comprehensive Framework

The system tracks:
- Which modules you've completed
- Which concepts you've explored
- Whether you're ready to advance
- What you still need to cover

```python
Module 02: Breaking Down Complexity
Concepts Required: [decomposition, prioritization, simplification, abstraction]
Concepts Covered: [decomposition, prioritization]
Remaining: [simplification, abstraction]
Status: In Progress (50%)
```

### The Balance

**Generic Learning**: "Here's how to do systems thinking..."

**This App**:
- "Alex, remember when you said project delays create team frustration, which leads to more status meetings, which causes more delays? That's a reinforcing feedback loop. Let's map that system..."

Uses YOUR challenges as the vehicle for exploring universal concepts.

## Features

### 1. Persistent Learner State

Your progress is automatically saved:
```
learners/
└── alex_pm/
    └── state.json  # Everything about your learning journey
```

Includes:
- Your role and context
- Challenges and goals
- Insights from each module
- Conversation history
- Progress through modules

### 2. Dynamic Module Loading

Modules adapt to you:
```python
# Generic Module 03 prompt
"Let's talk about systems thinking..."

# Your contextualized prompt
"Alex, in your role coordinating Engineering, Sales, and Customer Success,
let's explore how these teams interact as a system. When Engineering
changes a feature, what ripple effects happen across Sales and CS?"
```

### 3. Smart Progression

The system knows when you're ready to advance based on:
- Concepts explored (not just mentioned, but actually applied)
- Insights captured
- Depth of conversation
- Explicit readiness

### 4. Progress Tracking

See your journey:
- Modules completed
- Current module progress
- Concepts covered vs. remaining
- Key insights you've discovered

## Usage Examples

### Starting Out (Module 00)

```
AI: "Let's start by understanding your current situation. What's your role,
     and what brings you to this learning journey?"

You: "I'm a product manager at a mid-size SaaS company. I'm struggling
      with project delays and team communication."

AI: "Tell me more about these project delays. What typically happens?"

You: [Describes specific situation]

AI: "I hear that unclear requirements lead to delays. Can you walk me
     through a recent example?"

[Conversation continues, building your specific context...]
```

### Mid-Journey (Module 03)

```
AI: "Alex, remember that pattern you identified where all your challenges
     involve cross-team coordination? Let's explore that through a systems
     lens. When Engineering makes a change, what happens next?"

You: "Usually Sales finds out from customers, then gets frustrated..."

AI: "And how does that frustration affect Engineering?"

You: "They get defensive and share less proactively."

AI: "So we have a loop: Change → Poor communication → Frustration →
     Less communication → More surprises. That's a vicious cycle.
     Where in that loop could you intervene?"

[Applying systems thinking to YOUR specific challenge...]
```

### Advancing Modules

When ready:
```
AI: "You've explored decomposition, prioritization, and simplification
     in depth through your project delay challenge. You've identified
     that the real bottleneck is in the alignment phase, not the entire
     process. Want to explore how to make that alignment repeatable
     in Module 04?"

You: "Yes, let's do it."

[System transitions to Module 04, carrying forward your context...]
```

## Architecture

```
┌─────────────────────┐
│   Gradio UI         │  # Clean web interface
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  State Manager      │  # Tracks your progress
│  - Learner context  │  # Customization
│  - Module progress  │  # Comprehensiveness
│  - Conversation     │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Module Loader      │  # Dynamic prompts
│  - Injects context  │  # Your situation
│  - Tracks concepts  │  # Coverage
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Local LLM (Ollama) │  # Privacy-first AI
│  - Llama 3.2        │
│  - Mistral, etc.    │
└─────────────────────┘
```

## File Structure

```
voice_app/
├── app_gradio.py              # Main Gradio application
├── ARCHITECTURE.md            # Detailed design documentation
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── core/
│   ├── state_manager.py      # Learner state persistence
│   ├── module_loader.py      # Dynamic module content
│   └── llm_interface.py      # Ollama integration
│
└── learners/                  # Generated learner data
    └── {learner_id}/
        └── state.json         # Individual learner state
```

## Customization

### Change the LLM Model

Edit `app_gradio.py`:
```python
llm = LocalLLM(model="mistral")  # or llama2, codellama, etc.
```

### Add Multiple Learners

In the UI, change the "Learner ID" field:
- `alex_pm` - for Alex the Product Manager
- `sam_eng` - for Sam the Engineer
- `team_alpha` - for a shared team learning journey

Each gets their own state file.

### Adjust Module Completion Criteria

Edit `core/state_manager.py`:
```python
def check_module_readiness(self, learner_state: Dict, module_id: str) -> bool:
    # Customize what "ready" means
    min_insights = 5  # Require more depth
    # ...
```

## Adding Voice (Optional)

### Speech-to-Text (Whisper)

```bash
pip install faster-whisper

# In app_gradio.py, uncomment voice sections
```

### Text-to-Speech

```bash
pip install pyttsx3

# Add TTS to AI responses
```

### Full Voice Example

```python
from faster_whisper import WhisperModel

whisper = WhisperModel("base")

def transcribe_audio(audio_path):
    segments, _ = whisper.transcribe(audio_path)
    return " ".join([s.text for s in segments])

# Add to Gradio interface
audio_input = gr.Audio(source="microphone", type="filepath")
```

## Troubleshooting

### "Could not connect to Ollama"

```bash
# Make sure Ollama is running
ollama serve

# Check it's accessible
curl http://localhost:11434/api/tags
```

### "No models found"

```bash
# Pull a model
ollama pull llama3.2

# Verify
ollama list
```

### Slow responses

```bash
# Use a smaller model
ollama pull llama3.2:1b  # 1B parameter version

# Or adjust in app
llm = LocalLLM(model="llama3.2:1b")
```

### Conversations feel generic

Check that learner context is populated:
1. Complete Module 00 thoroughly
2. Provide specific challenges and context
3. The more specific you are, the more customized the responses

## Advanced Usage

### Export Your Journey

```python
from core.state_manager import LearnerStateManager

state_mgr = LearnerStateManager()
learner = state_mgr.load_learner("your_id")

# Export insights
for module_id, insights in learner["key_insights"].items():
    print(f"Module {module_id}:")
    for insight in insights:
        print(f"  - {insight['insight']}")
```

### Analyze Progress

```python
# See completion rates
for mod_id in range(13):
    mod = f"{mod_id:02d}"
    progress = learner["module_progress"][mod]
    print(f"Module {mod}: {len(progress['concepts_covered'])}/concepts")
```

### Team Learning

Use a shared learner ID:
```
learner_id = "product_team_q1_2025"
```

Multiple people can contribute to the same learning journey.

## Philosophy

This app embodies the principle:

> **Use each learner's SPECIFIC context as the medium through which UNIVERSAL concepts are explored systematically.**

- **Specific context** = Customization
- **Universal concepts** = Comprehensiveness
- **Explored systematically** = Structured but flexible progression

## Contributing

Want to extend this? Ideas:

1. **Better insight extraction**: Use LLM to identify insights, not keywords
2. **Visual progress**: Add charts and graphs
3. **Voice integration**: Full STT/TTS pipeline
4. **Mobile app**: Package as mobile experience
5. **Collaborative mode**: Multiple learners in one conversation
6. **Analytics**: Track learning patterns across users

## License

This learning framework is part of the Agentic Upskilling curriculum.
See main repository for license details.

## Support

For issues or questions:
1. Check `ARCHITECTURE.md` for design details
2. Review learner state files in `learners/{id}/state.json`
3. Verify Ollama connectivity and model availability
4. Ensure module content files are accessible

## What's Next?

After you've built familiarity with the system:
1. Try the Streamlit version (if available)
2. Experiment with different LLM models
3. Customize module completion criteria
4. Add voice capabilities
5. Build team learning experiences

---

**Remember**: This is YOUR learning journey. The system adapts to YOU. Be specific, be honest, and let the conversation flow naturally.

The more you put into it (real challenges, honest reflection, deep exploration), the more you'll get out of it.

Happy learning! 🎓
