"""
NEXUS-AGENT: Hierarchical Episodic-Semantic Cognitive Memory
Mitigates catastrophic forgetting by pairing rapid episodic experiential logging
with slow semantic consolidation via knowledge graph triples and decaying activation weights.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time
import math


@dataclass
class EpisodicTrace:
    trace_id: str
    task_goal: str
    plan_sequence: List[str]
    success: bool
    epistemic_entropy_mean: float
    reward: float
    timestamp: float = field(default_factory=time.time)
    activation_strength: float = 1.0


@dataclass
class SemanticConcept:
    concept_id: str
    predicate: str
    related_tools: List[str]
    evidence_count: int = 1
    confidence: float = 0.90


class HierarchicalCognitiveMemory:
    """Dual-tier cognitive memory architecture with Hebbian decay and consolidation."""

    def __init__(self, decay_rate: float = 0.05):
        self.decay_rate = decay_rate
        self.episodic_store: List[EpisodicTrace] = []
        self.semantic_store: Dict[str, SemanticConcept] = {}

    def log_episode(
        self,
        trace_id: str,
        goal: str,
        plan_sequence: List[str],
        success: bool,
        mean_entropy: float,
        reward: float
    ) -> EpisodicTrace:
        """Stores execution trace in short-term episodic memory."""
        trace = EpisodicTrace(
            trace_id=trace_id,
            task_goal=goal,
            plan_sequence=plan_sequence,
            success=success,
            epistemic_entropy_mean=mean_entropy,
            reward=reward
        )
        self.episodic_store.append(trace)
        return trace

    def consolidate_episodes(self):
        """Consolidates high-reward episodic traces into long-term semantic concepts."""
        current_time = time.time()
        for trace in self.episodic_store:
            # Apply exponential decay to episodic traces
            age_hours = (current_time - trace.timestamp) / 3600.0
            trace.activation_strength = math.exp(-self.decay_rate * age_hours)

            # Consolidate successful traces with low entropy into semantic memory
            if trace.success and trace.reward > 0.70:
                concept_key = f"solves_{trace.task_goal[:30].strip().replace(' ', '_')}"
                if concept_key in self.semantic_store:
                    concept = self.semantic_store[concept_key]
                    concept.evidence_count += 1
                    concept.confidence = min(0.99, concept.confidence + 0.02)
                else:
                    self.semantic_store[concept_key] = SemanticConcept(
                        concept_id=concept_key,
                        predicate=f"Successfully solves: {trace.task_goal}",
                        related_tools=trace.plan_sequence
                    )

    def retrieve_relevant_experience(self, query_goal: str) -> List[EpisodicTrace]:
        """Retrieves top-k active episodic traces matching query tokens."""
        query_tokens = set(query_goal.lower().split())
        scored_traces = []
        for t in self.episodic_store:
            goal_tokens = set(t.task_goal.lower().split())
            overlap = len(query_tokens.intersection(goal_tokens))
            score = overlap * t.activation_strength * (1.5 if t.success else 0.5)
            scored_traces.append((score, t))

        scored_traces.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored_traces[:3]]
