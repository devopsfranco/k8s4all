"""
Learner State Management
Handles customization through persistent learner context
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class LearnerStateManager:
    def __init__(self, data_dir: str = "learners"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def create_new_learner(self, learner_id: str) -> Dict:
        """Initialize a new learner with empty state"""
        return {
            "id": learner_id,
            "created_at": datetime.now().isoformat(),
            "name": "",
            "role": "",
            "organization_context": "",
            "current_module": "00",
            "modules_completed": [],
            "challenges": [],
            "goals": [],
            "key_insights": {},
            "custom_context": {},
            "conversation_history": [],
            "module_progress": {
                f"{i:02d}": {
                    "started": False,
                    "completed": False,
                    "insights": [],
                    "concepts_covered": []
                }
                for i in range(13)
            }
        }

    def load_learner(self, learner_id: str) -> Dict:
        """Load existing learner or create new"""
        learner_file = self.data_dir / learner_id / "state.json"

        if learner_file.exists():
            with open(learner_file, 'r') as f:
                return json.load(f)
        else:
            return self.create_new_learner(learner_id)

    def save_learner(self, learner_state: Dict):
        """Persist learner state"""
        learner_id = learner_state["id"]
        learner_dir = self.data_dir / learner_id
        learner_dir.mkdir(exist_ok=True)

        with open(learner_dir / "state.json", 'w') as f:
            json.dump(learner_state, f, indent=2)

    def update_conversation(self, learner_state: Dict, user_msg: str, ai_msg: str):
        """Add to conversation history"""
        learner_state["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_msg,
            "ai": ai_msg
        })

        # Keep last 50 exchanges to manage size
        if len(learner_state["conversation_history"]) > 50:
            learner_state["conversation_history"] = learner_state["conversation_history"][-50:]

        self.save_learner(learner_state)

    def add_insight(self, learner_state: Dict, module_id: str, insight: str):
        """Capture a key insight from the conversation"""
        if module_id not in learner_state["key_insights"]:
            learner_state["key_insights"][module_id] = []

        learner_state["key_insights"][module_id].append({
            "timestamp": datetime.now().isoformat(),
            "insight": insight
        })

        learner_state["module_progress"][module_id]["insights"].append(insight)
        self.save_learner(learner_state)

    def mark_concept_covered(self, learner_state: Dict, module_id: str, concept: str):
        """Track that a concept has been explored"""
        if concept not in learner_state["module_progress"][module_id]["concepts_covered"]:
            learner_state["module_progress"][module_id]["concepts_covered"].append(concept)
            self.save_learner(learner_state)

    def start_module(self, learner_state: Dict, module_id: str):
        """Mark module as started"""
        learner_state["module_progress"][module_id]["started"] = True
        learner_state["current_module"] = module_id
        self.save_learner(learner_state)

    def complete_module(self, learner_state: Dict, module_id: str):
        """Mark module as completed"""
        learner_state["module_progress"][module_id]["completed"] = True
        if module_id not in learner_state["modules_completed"]:
            learner_state["modules_completed"].append(module_id)
        self.save_learner(learner_state)

    def check_module_readiness(self, learner_state: Dict, module_id: str) -> bool:
        """
        Check if learner has sufficiently engaged with module
        Based on insights captured and concepts covered
        """
        progress = learner_state["module_progress"][module_id]

        # Module 00 needs basic context
        if module_id == "00":
            return (
                len(learner_state["challenges"]) >= 1 and
                len(learner_state["goals"]) >= 1 and
                learner_state["role"] != ""
            )

        # Other modules need insights and concept coverage
        min_insights = 3 if module_id in ["00", "01"] else 2
        min_concepts = {
            "02": 3,  # Decomposition, prioritization, simplification
            "03": 3,  # Connections, feedback loops, leverage points
            "04": 2,  # Repeatability, process design
            # etc.
        }.get(module_id, 2)

        has_insights = len(progress["insights"]) >= min_insights
        has_concepts = len(progress["concepts_covered"]) >= min_concepts

        return has_insights and has_concepts

    def get_context_summary(self, learner_state: Dict) -> str:
        """Generate a summary of learner context for prompt injection"""
        context_parts = []

        if learner_state["name"]:
            context_parts.append(f"Learner: {learner_state['name']}")

        if learner_state["role"]:
            context_parts.append(f"Role: {learner_state['role']}")

        if learner_state["organization_context"]:
            context_parts.append(f"Context: {learner_state['organization_context']}")

        if learner_state["challenges"]:
            challenges_str = "\n- ".join(learner_state["challenges"])
            context_parts.append(f"Key Challenges:\n- {challenges_str}")

        if learner_state["goals"]:
            goals_str = "\n- ".join(learner_state["goals"])
            context_parts.append(f"Goals:\n- {goals_str}")

        # Include recent insights from previous modules
        if learner_state["key_insights"]:
            insights_str = ""
            for mod_id in sorted(learner_state["key_insights"].keys()):
                if learner_state["key_insights"][mod_id]:
                    last_insight = learner_state["key_insights"][mod_id][-1]["insight"]
                    insights_str += f"\n- Module {mod_id}: {last_insight}"

            if insights_str:
                context_parts.append(f"Previous Insights:{insights_str}")

        return "\n\n".join(context_parts)

    def get_conversation_context(self, learner_state: Dict, last_n: int = 5) -> str:
        """Get recent conversation history"""
        recent = learner_state["conversation_history"][-last_n:]
        context = []

        for exchange in recent:
            context.append(f"User: {exchange['user']}")
            context.append(f"AI: {exchange['ai']}")

        return "\n".join(context)

    def suggest_next_module(self, learner_state: Dict) -> Optional[str]:
        """Suggest next module based on completion"""
        current = learner_state["current_module"]
        current_num = int(current)

        # Check if current module is complete
        if self.check_module_readiness(learner_state, current):
            # Suggest next module
            next_num = current_num + 1
            if next_num <= 12:
                return f"{next_num:02d}"

        return None
