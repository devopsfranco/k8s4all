"""
Module Content Loader
Dynamically loads module prompts and injects learner context for customization
"""

from pathlib import Path
from typing import Dict

class ModuleLoader:
    def __init__(self, modules_dir: str = "../"):
        self.modules_dir = Path(modules_dir)

        # Module metadata for comprehensive coverage
        self.modules = {
            "00": {
                "name": "Starting Point",
                "required": True,
                "key_concepts": ["context", "challenges", "goals"],
                "completion_criteria": ["role_identified", "challenges_listed", "goals_stated"]
            },
            "01": {
                "name": "Understanding Challenges",
                "required": True,
                "depends_on": ["00"],
                "key_concepts": ["root_causes", "patterns", "control_vs_influence"],
                "completion_criteria": ["root_cause_analysis", "pattern_recognition", "prioritization"]
            },
            "02": {
                "name": "Breaking Down Complexity",
                "required": True,
                "depends_on": ["01"],
                "key_concepts": ["decomposition", "abstraction", "prioritization", "simplification"],
                "completion_criteria": ["applied_decomposition", "identified_priorities", "simplified_challenge"]
            },
            "03": {
                "name": "Systems Thinking",
                "required": True,
                "depends_on": ["02"],
                "key_concepts": ["connections", "feedback_loops", "leverage_points", "unintended_consequences"],
                "completion_criteria": ["mapped_system", "identified_loops", "found_leverage"]
            },
            "04": {
                "name": "Making Things Repeatable",
                "required": True,
                "depends_on": ["03"],
                "key_concepts": ["patterns", "processes", "documentation", "consistency"],
                "completion_criteria": ["extracted_pattern", "designed_process"]
            },
            "05": {
                "name": "Scaling What Works",
                "required": True,
                "depends_on": ["04"],
                "key_concepts": ["scalability", "growth_challenges", "quality_maintenance"],
                "completion_criteria": ["identified_scalable_elements", "planned_scaling"]
            },
            "06": {
                "name": "Managing Change",
                "required": True,
                "depends_on": ["05"],
                "key_concepts": ["resistance", "transitions", "communication", "momentum"],
                "completion_criteria": ["understood_resistance", "planned_change"]
            },
            "07": {
                "name": "Collaboration and Communication",
                "required": True,
                "depends_on": ["06"],
                "key_concepts": ["clarity", "listening", "coordination", "conflict"],
                "completion_criteria": ["improved_communication", "addressed_breakdown"]
            },
            "08": {
                "name": "Decision Making",
                "required": True,
                "depends_on": ["07"],
                "key_concepts": ["uncertainty", "tradeoffs", "frameworks", "bias_awareness"],
                "completion_criteria": ["made_decision", "evaluated_tradeoffs"]
            },
            "09": {
                "name": "Measuring What Matters",
                "required": True,
                "depends_on": ["08"],
                "key_concepts": ["outcomes_vs_outputs", "leading_indicators", "metric_design"],
                "completion_criteria": ["designed_metrics", "avoided_gaming"]
            },
            "10": {
                "name": "Leading and Influencing",
                "required": True,
                "depends_on": ["09"],
                "key_concepts": ["influence_without_authority", "development", "trust", "difficult_conversations"],
                "completion_criteria": ["influenced_others", "developed_someone"]
            },
            "11": {
                "name": "Continuous Learning",
                "required": True,
                "depends_on": ["10"],
                "key_concepts": ["learning_from_experience", "adaptation", "unlearning"],
                "completion_criteria": ["built_learning_practice", "adapted_to_change"]
            },
            "12": {
                "name": "Designing Solutions",
                "required": True,
                "depends_on": ["11"],
                "key_concepts": ["synthesis", "integration", "custom_design", "implementation"],
                "completion_criteria": ["synthesized_learning", "designed_solution", "planned_implementation"]
            }
        }

    def get_module_info(self, module_id: str) -> Dict:
        """Get module metadata"""
        return self.modules.get(module_id, {})

    def load_module_prompt(self, module_id: str) -> str:
        """Load the conversation starter prompt for a module"""
        module_path = self.modules_dir / f"Module_{module_id}_{self.modules[module_id]['name'].replace(' ', '_')}" / "conversation_starter.md"

        try:
            with open(module_path, 'r') as f:
                content = f.read()

            # Extract the prompt between [BEGIN PROMPT] and [END PROMPT]
            start_marker = "[BEGIN PROMPT]"
            end_marker = "[END PROMPT]"

            if start_marker in content and end_marker in content:
                start_idx = content.find(start_marker) + len(start_marker)
                end_idx = content.find(end_marker)
                return content[start_idx:end_idx].strip()
            else:
                return content

        except FileNotFoundError:
            return f"Module {module_id} - {self.modules[module_id]['name']} prompt not found."

    def build_contextualized_prompt(self, module_id: str, learner_context: str, conversation_history: str = "") -> str:
        """
        Build a prompt that combines:
        1. Learner's specific context
        2. Module's learning objectives
        3. Recent conversation history
        4. Guidance for the AI on how to proceed
        """

        module_info = self.modules[module_id]
        module_prompt = self.load_module_prompt(module_id)

        # System instruction for the AI
        system_instruction = f"""You are a thoughtful learning coach helping someone develop professional skills through conversation.

You are currently guiding them through Module {module_id}: {module_info['name']}.

Key concepts to explore in this module:
{', '.join(module_info['key_concepts'])}

IMPORTANT GUIDELINES:
1. Use the learner's SPECIFIC context and challenges - never generic examples
2. Ask thoughtful questions that make them think deeply
3. Help them discover insights rather than telling them
4. Connect new concepts to what they've already learned
5. Keep the conversation natural and conversational
6. When they've explored a concept, mark it covered by summarizing their insight
7. Don't rush - depth matters more than speed

The learner's context is below. Use this to personalize everything you say."""

        # Combine everything
        full_prompt = f"""{system_instruction}

=== LEARNER CONTEXT ===
{learner_context}

=== MODULE GUIDANCE ===
{module_prompt}

=== RECENT CONVERSATION ===
{conversation_history if conversation_history else "(Starting fresh conversation)"}

=== YOUR RESPONSE ===
Based on the learner's context and our conversation, continue the dialogue naturally. Ask a thoughtful question or explore a concept from this module using their specific situation."""

        return full_prompt

    def get_transition_prompt(self, from_module: str, to_module: str, learner_context: str) -> str:
        """Generate a prompt for transitioning between modules"""

        from_name = self.modules[from_module]['name']
        to_name = self.modules[to_module]['name']
        to_concepts = self.modules[to_module]['key_concepts']

        return f"""The learner has just completed Module {from_module}: {from_name}.

Now transitioning to Module {to_module}: {to_name}.

=== LEARNER CONTEXT ===
{learner_context}

=== TRANSITION GUIDANCE ===
1. Briefly acknowledge their progress on {from_name}
2. Connect what they learned to what comes next in {to_name}
3. Use their specific context to introduce the new module naturally
4. Don't make it feel like a "lesson change" - make it feel like a natural conversation progression

Key concepts in {to_name}: {', '.join(to_concepts)}

Generate a natural transition that:
- Acknowledges their work
- Connects to their context
- Introduces the next topic organically
- Asks an opening question for Module {to_module}"""

    def check_concept_coverage(self, learner_state: Dict, module_id: str) -> Dict:
        """Check which concepts from this module have been covered"""
        module_info = self.modules[module_id]
        required_concepts = set(module_info['key_concepts'])
        covered_concepts = set(learner_state["module_progress"][module_id]["concepts_covered"])

        return {
            "required": required_concepts,
            "covered": covered_concepts,
            "remaining": required_concepts - covered_concepts,
            "completion_rate": len(covered_concepts) / len(required_concepts) if required_concepts else 0
        }

    def get_next_concept_prompt(self, learner_state: Dict, module_id: str, learner_context: str) -> str:
        """Generate prompt to explore remaining concepts in current module"""

        coverage = self.check_concept_coverage(learner_state, module_id)

        if not coverage["remaining"]:
            return "All concepts covered. Ready to transition."

        next_concept = list(coverage["remaining"])[0]
        module_name = self.modules[module_id]['name']

        return f"""The learner is working through Module {module_id}: {module_name}.

They have covered: {', '.join(coverage['covered']) if coverage['covered'] else 'just started'}
Still need to explore: {', '.join(coverage['remaining'])}

=== LEARNER CONTEXT ===
{learner_context}

=== GUIDANCE ===
Help them explore the concept of "{next_concept}" using their specific context and challenges.
Don't mention "we need to cover this concept" - just naturally steer the conversation to explore it through their real situations.

Ask a question or make an observation that leads them to think about {next_concept} in relation to their challenges."""

        return next_concept_prompt
