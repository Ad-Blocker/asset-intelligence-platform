"""
Main Execution & Interactive Demonstration Module for Asset Intelligence Platform.

Demonstrates the refactored LLM Orchestrator executing deterministic ExecutionPlans
uniting:
1. Knowledge Graph (Neo4j)
2. Telemetry Engine (CSV / Pandas)
3. Document Intelligence Layer (PDF / RAG Vector Store)
"""

import sys
from typing import List

from llm.orchestrator import LLMOrchestrator
from llm.models import OrchestratorResponse
from utils.logger import setup_logger
from config import config

logger = setup_logger("main", config.log_level)


def format_orchestrator_output(response: OrchestratorResponse) -> None:
    """
    Format and print structured OrchestratorResponse and ExecutionPlan details for demonstration.

    Args:
        response (OrchestratorResponse): Complete response bundle from orchestrator.
    """
    print("\n" + "=" * 76)
    print(f" QUESTION: \"{response.user_question}\"")
    print("=" * 76)

    # 1. Execution Plan Section
    if response.execution_plan:
        plan = response.execution_plan
        print("\nExecution Plan")
        print("-" * 76)
        print(f"Goal: {plan.goal}")
        print("\nPlanned Execution Steps:")
        print(f"  {'Step ID':<18} | {'Service':<18} | {'Status':<6} | {'Latency':<9} | Action")
        print("  " + "-" * 72)

        # Map step execution call latency
        sc_map = {sc.service: sc for sc in response.service_calls}

        for step in plan.steps:
            sc = sc_map.get(step.service_name)
            status_str = "OK" if (sc and sc.success) else "PEND"
            lat_str = f"{sc.execution_time_ms:>5.1f} ms" if sc else "   N/A   "
            action_snippet = step.action if len(step.action) <= 35 else step.action[:32] + "..."
            print(f"  {step.step_id:<18} | {step.service_name:<18} | {status_str:<6} | {lat_str:<9} | {action_snippet}")

    # 2. Intent Breakdown
    g_check = "[YES]" if response.intent.graph else "[ NO]"
    t_check = "[YES]" if response.intent.telemetry else "[ NO]"
    d_check = "[YES]" if response.intent.documents else "[ NO]"

    print("\nDetected Intent")
    print("-" * 35)
    print(f"  Knowledge Graph:   {g_check}")
    print(f"  Telemetry Engine:  {t_check}")
    print(f"  Document RAG:      {d_check}")

    # 3. Execution Timing & Records Returned Breakdown
    print("\nService Execution Summary")
    print("-" * 50)
    print(f"  {'Service':<22} | {'Status':<8} | {'Latency':<10} | {'Records'}")
    print("-" * 50)
    for sc in response.service_calls:
        status_str = "OK" if sc.success else "FAIL"
        print(f"  {sc.service:<22} | {status_str:<8} | {sc.execution_time_ms:>6.1f} ms  | {sc.records_returned:>4}")
    print(f"  {'Total Pipeline':<22} | {'OK':<8} | {response.total_execution_time_ms:>6.1f} ms  |")

    # 4. Final Synthesized AI Response
    print("\nFINAL AI ASSISTANT RESPONSE")
    print("=" * 76)
    print(response.final_answer)
    print("=" * 76)


def run_platform_demonstration() -> None:
    """Run end-to-end platform demonstration over representative user questions."""
    logger.info("Initializing Asset Intelligence Platform Orchestrator & Execution Planner...")
    orchestrator = LLMOrchestrator()

    representative_questions = [
        "What components belong to AHU-01?",
        "What is the latest supply air temperature?",
        "What maintenance should be performed on the cooling coil?",
        "Why is Conference Room A warmer than usual?"
    ]

    print("\n" + "#" * 76)
    print("  ASSET INTELLIGENCE PLATFORM — DETERMINISTIC EXECUTION PLANNER DEMO")
    print("#" * 76)

    for question in representative_questions:
        try:
            response: OrchestratorResponse = orchestrator.process_query(question)
            format_orchestrator_output(response)
        except Exception as e:
            logger.error("Error processing question '%s': %s", question, e)

    # Clean up connections
    try:
        orchestrator.graph_client.close()
        orchestrator.telemetry_service.clear_cache()
        orchestrator.document_service.clear_cache()
    except Exception as e:
        logger.warning("Error closing services: %s", e)


def main() -> None:
    """Main execution function."""
    run_platform_demonstration()


if __name__ == "__main__":
    main()
