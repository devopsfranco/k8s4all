"""
Agentic Upskilling - Voice-Enabled Learning App (Gradio)
Customized yet comprehensive learning through conversational AI
"""

import gradio as gr
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.state_manager import LearnerStateManager
from core.module_loader import ModuleLoader
from core.llm_interface import LocalLLM

# Initialize components
state_manager = LearnerStateManager()
module_loader = ModuleLoader()
llm = LocalLLM(model="llama3.2")  # or "mistral", "llama2", etc.

# Global state for the session
current_learner_id = "default_learner"


def initialize_learner(learner_id: str):
    """Initialize or load learner state"""
    global current_learner_id
    current_learner_id = learner_id
    learner_state = state_manager.load_learner(learner_id)

    # If new learner, start with Module 00
    if not learner_state["module_progress"]["00"]["started"]:
        state_manager.start_module(learner_state, "00")

    return learner_state


def process_message(message: str, history: list):
    """
    Process user message and generate AI response
    This is where customization meets comprehensiveness
    """
    # Load learner state
    learner_state = state_manager.load_learner(current_learner_id)
    current_module = learner_state["current_module"]

    # Get learner context for customization
    learner_context = state_manager.get_context_summary(learner_state)

    # Get conversation history for continuity
    recent_conversation = state_manager.get_conversation_context(learner_state, last_n=5)

    # Build contextualized prompt for comprehensive coverage
    full_prompt = module_loader.build_contextualized_prompt(
        module_id=current_module,
        learner_context=learner_context,
        conversation_history=recent_conversation + f"\n\nUser: {message}\n\nAI:"
    )

    # Get AI response
    ai_response = llm.chat(full_prompt)

    # Update state
    state_manager.update_conversation(learner_state, message, ai_response)

    # Extract and save insights (simple keyword-based for now)
    if any(word in message.lower() for word in ["realize", "understand", "insight", "because", "now i see"]):
        state_manager.add_insight(learner_state, current_module, message)

    # Check for concept coverage (simple pattern matching - could be enhanced)
    module_info = module_loader.get_module_info(current_module)
    for concept in module_info["key_concepts"]:
        if concept.replace("_", " ") in message.lower() or concept.replace("_", " ") in ai_response.lower():
            state_manager.mark_concept_covered(learner_state, current_module, concept)

    # Update history for display
    history.append((message, ai_response))

    return "", history


def check_progress():
    """Display learner progress"""
    learner_state = state_manager.load_learner(current_learner_id)

    progress_text = f"## Learning Progress for {learner_state.get('name', 'Learner')}\n\n"
    progress_text += f"**Current Module**: {learner_state['current_module']} - {module_loader.modules[learner_state['current_module']]['name']}\n\n"

    progress_text += "### Modules Completed:\n"
    for mod_id in sorted(learner_state["modules_completed"]):
        progress_text += f"- Module {mod_id}: {module_loader.modules[mod_id]['name']}\n"

    progress_text += "\n### Current Module Progress:\n"
    current = learner_state["current_module"]
    coverage = module_loader.check_concept_coverage(learner_state, current)
    progress_text += f"- Concepts covered: {len(coverage['covered'])}/{len(coverage['required'])}\n"
    progress_text += f"- Covered: {', '.join(coverage['covered']) if coverage['covered'] else 'None yet'}\n"
    progress_text += f"- Remaining: {', '.join(coverage['remaining']) if coverage['remaining'] else 'All covered!'}\n"

    progress_text += "\n### Key Insights:\n"
    if learner_state["key_insights"]:
        for mod_id in sorted(learner_state["key_insights"].keys()):
            if learner_state["key_insights"][mod_id]:
                progress_text += f"\n**Module {mod_id}:**\n"
                for insight in learner_state["key_insights"][mod_id][-3:]:  # Last 3 insights
                    progress_text += f"- {insight['insight']}\n"
    else:
        progress_text += "No insights captured yet.\n"

    return progress_text


def advance_module():
    """Move to next module"""
    learner_state = state_manager.load_learner(current_learner_id)
    current = learner_state["current_module"]

    # Check readiness
    if state_manager.check_module_readiness(learner_state, current):
        # Complete current
        state_manager.complete_module(learner_state, current)

        # Move to next
        next_module = state_manager.suggest_next_module(learner_state)
        if next_module:
            state_manager.start_module(learner_state, next_module)
            return f"Great work! Moving to Module {next_module}: {module_loader.modules[next_module]['name']}"
        else:
            return "Congratulations! You've completed all modules!"
    else:
        coverage = module_loader.check_concept_coverage(learner_state, current)
        return f"Not quite ready to advance. Still need to explore: {', '.join(coverage['remaining'])}"


def reset_conversation():
    """Start fresh conversation (keeps learner state)"""
    return [], "Conversation reset. Your progress is saved."


# Build Gradio Interface
with gr.Blocks(title="Agentic Upskilling - Voice Learning", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🎓 Agentic Upskilling: Your Personal Learning Coach

    This is a **conversational learning system** that adapts to YOU. It uses a local AI to guide you through
    personalized learning based on your specific challenges and goals.

    ## How It Works:
    1. **Speak or type** your responses
    2. The AI asks thoughtful questions about YOUR situation
    3. You explore concepts through YOUR real challenges
    4. Progress is tracked automatically
    5. All learning happens locally and privately

    **Current Model**: {model} via Ollama
    """.format(model=llm.model))

    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=500, label="Learning Conversation")

            with gr.Row():
                with gr.Column(scale=4):
                    msg = gr.Textbox(
                        label="Your Message",
                        placeholder="Type here or use voice...",
                        lines=2
                    )
                with gr.Column(scale=1):
                    # Voice input (optional - requires audio setup)
                    # audio_input = gr.Audio(source="microphone", type="filepath", label="Voice Input")
                    pass

            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear Conversation")

        with gr.Column(scale=1):
            gr.Markdown("## Your Progress")
            progress_display = gr.Markdown("Click 'Check Progress' to see your journey")

            check_progress_btn = gr.Button("Check Progress")
            advance_btn = gr.Button("Ready for Next Module?")

            status_display = gr.Textbox(label="Status", lines=2)

            gr.Markdown("### Learner ID")
            learner_id_input = gr.Textbox(
                value="default_learner",
                label="Your ID (to save progress)",
                info="Change this to have multiple learners"
            )
            init_btn = gr.Button("Initialize/Load Learner")

    # Event handlers
    send_btn.click(
        fn=process_message,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )

    msg.submit(
        fn=process_message,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )

    clear_btn.click(
        fn=reset_conversation,
        outputs=[chatbot, status_display]
    )

    check_progress_btn.click(
        fn=check_progress,
        outputs=progress_display
    )

    advance_btn.click(
        fn=advance_module,
        outputs=status_display
    )

    init_btn.click(
        fn=lambda lid: initialize_learner(lid) and "Learner loaded!",
        inputs=learner_id_input,
        outputs=status_display
    )

    # Check Ollama on startup
    gr.Markdown(f"""
    ---
    ### System Status
    - **Ollama Status**: {"✅ Connected" if llm.is_available() else "❌ Not connected - Please run 'ollama serve'"}
    - **Available Models**: {', '.join(llm.list_models()) if llm.list_models() else "None found"}

    To get started:
    1. Make sure Ollama is running: `ollama serve`
    2. Pull a model if needed: `ollama pull llama3.2`
    3. Initialize your learner ID above
    4. Start chatting!
    """)


if __name__ == "__main__":
    # Initialize default learner
    initialize_learner(current_learner_id)

    # Launch app
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # Set to True to create a public link
    )
