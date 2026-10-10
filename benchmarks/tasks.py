"""
NEXUS-AGENT: Academic Benchmark Task Suite
Defines standardized scientific task benchmarks covering:
1. Formal Temporal Logic Constraint Tasks
2. Byzantine Adversarial Reasoning Tasks
3. Dynamic Out-of-Distribution Tool Synthesis Tasks
4. Complex Multi-Step Deductive Deliberation
"""

from typing import List
from src.core.state import TaskSpecification


def get_academic_benchmark_tasks() -> List[TaskSpecification]:
    """Returns a curated battery of PhD-level benchmark tasks."""
    return [
        TaskSpecification(
            task_id="TASK-LTL-01",
            goal_description="Coordinate robotic assembly workflow ensuring safety invariant G(not resource_exhausted)",
            safety_invariants=["G(not resource_exhausted)", "F(verified_output)"],
            available_tools=["sensor_poll", "gripper_actuate"]
        ),
        TaskSpecification(
            task_id="TASK-BYZ-02",
            goal_description="Evaluate peer-reviewed scientific claims amidst 33% adversarial byzantine misinformation",
            safety_invariants=["G(not byzantine_compromised)", "F(verified_output)"],
            available_tools=["citation_graph_query", "epistemic_entropy_check"]
        ),
        TaskSpecification(
            task_id="TASK-SYN-03",
            goal_description="Solve high-dimensional spectral radius minimization requiring on-demand matrix spectral tool synthesis",
            safety_invariants=["G(not tool_safety_violation)", "F(verified_output)"],
            available_tools=["basic_arithmetic"]  # Intentionally missing spectral tools to force runtime synthesis
        ),
        TaskSpecification(
            task_id="TASK-MCTS-04",
            goal_description="Multi-hop neuro-symbolic theorem derivation with deep branch exploration and backpropagation",
            safety_invariants=["G(not cyclic_reasoning)", "F(verified_output)"],
            available_tools=["axiom_lookup", "modus_ponens_apply"]
        ),
        TaskSpecification(
            task_id="TASK-CONTINUAL-05",
            goal_description="Lifelong skill retention and catastrophic forgetting avoidance across sequential domain shifts",
            safety_invariants=["G(not resource_exhausted)", "F(verified_output)"],
            available_tools=["memory_index_query"]
        )
    ]
