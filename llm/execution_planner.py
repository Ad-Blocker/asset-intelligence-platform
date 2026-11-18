"""
Execution Planner Module.

Provides the ExecutionPlanner class responsible for generating a deterministic,
ordered ExecutionPlan prior to context retrieval and LLM orchestration.
"""

from typing import List
from .models import Intent
from .execution_models import ExecutionPlan, PlanStep
from utils.logger import setup_logger
from config import config

logger = setup_logger("llm.planner", config.log_level)


class ExecutionPlanner:
    """Deterministic planner constructing service execution step workflows from detected intent."""

    def create_plan(self, question: str, intent: Intent) -> ExecutionPlan:
        """
        Construct an ordered ExecutionPlan based on detected user intent.

        Args:
            question (str): User question string.
            intent (Intent): Detected intent classification bundle.

        Returns:
            ExecutionPlan: Ordered plan containing goal description and service steps.
        """
        steps: List[PlanStep] = []
        active_services: List[str] = []
        asset_id = intent.target_asset or "AHU-01"

        # 1. Knowledge Graph Step
        if intent.graph:
            active_services.append("Knowledge Graph")
            steps.append(PlanStep(
                step_id="step_1_graph",
                service_name="GraphService",
                action=f"Retrieve equipment topology, component hierarchy, and served spaces for asset '{asset_id}'",
                params={"asset_id": asset_id},
                depends_on=[]
            ))

        # 2. Telemetry Step
        if intent.telemetry:
            active_services.append("Telemetry Engine")
            depends = ["step_1_graph"] if intent.graph else []
            steps.append(PlanStep(
                step_id="step_2_telemetry",
                service_name="TelemetryService",
                action="Analyze 24-hour time-series readings and detect Z-score statistical anomalies",
                params={"asset_id": asset_id},
                depends_on=depends
            ))

        # 3. Document RAG Step
        if intent.documents:
            active_services.append("Document RAG")
            depends = ["step_1_graph"] if intent.graph else []
            steps.append(PlanStep(
                step_id="step_3_documents",
                service_name="DocumentService",
                action="Execute vector similarity search over OEM Carrier technical manuals",
                params={"query": question, "top_k": 3},
                depends_on=depends
            ))

        # Construct goal description
        if len(active_services) > 1:
            goal = f"Multi-source synthesis ({', '.join(active_services)}) to answer: '{question}'"
        elif active_services:
            goal = f"Single-source retrieval ({active_services[0]}) for query: '{question}'"
        else:
            goal = f"Default topological lookup for query: '{question}'"

        plan = ExecutionPlan(goal=goal, steps=steps)
        logger.info("Generated ExecutionPlan (%d steps) for query: '%s'", len(steps), question)
        return plan
