"""
NEXUS-AGENT: Deliberative Multi-Agent Debate Protocol
Orchestrates multi-round epistemic cross-examination between hypothesis generators,
adversarial critics, and formal verifiers until convergence or maximum rounds.
"""

from typing import List, Dict, Any, Tuple
from ..core.agent import AutonomousCognitiveAgent
from ..core.state import EpistemicBelief, ThoughtNode
from .byzantine_filter import ByzantineConsensusFilter
from .uncertainty import EpistemicUncertaintyQuantifier


class DeliberativeDebateOrchestrator:
    """Manages iterative epistemic cross-examination rounds."""

    def __init__(
        self,
        agents: List[AutonomousCognitiveAgent],
        max_rounds: int = 4,
        convergence_threshold: float = 0.05
    ):
        self.agents = agents
        self.max_rounds = max_rounds
        self.convergence_threshold = convergence_threshold
        self.bft_filter = ByzantineConsensusFilter()
        self.uncertainty_quantifier = EpistemicUncertaintyQuantifier()

    def conduct_debate(
        self,
        initial_hypothesis: str,
        context: str
    ) -> Dict[str, Any]:
        """Runs iterative deliberation rounds with BFT filtering and convergence checks."""
        rounds_data = []
        current_hypothesis = initial_hypothesis
        converged = False
        previous_consensus = 0.0

        for round_idx in range(self.max_rounds):
            thoughts: List[ThoughtNode] = []
            beliefs: List[EpistemicBelief] = []

            for agent in self.agents:
                thought = agent.deliberate(context=context, current_hypothesis=current_hypothesis)
                belief = agent.assess_epistemic_confidence(current_hypothesis)
                thoughts.append(thought)
                beliefs.append(belief)

            # Apply Byzantine filtering
            consensus_conf, byzantine_ids, rep_updates = self.bft_filter.filter_and_aggregate_beliefs(
                self.agents, beliefs
            )

            # Record round telemetry
            round_info = {
                "round_index": round_idx + 1,
                "consensus_confidence": consensus_conf,
                "flagged_byzantine_agents": byzantine_ids,
                "reputation_updates": rep_updates,
                "mean_entropy": float(np.mean([b.epistemic_entropy for b in beliefs])),
                "agent_thoughts": [
                    {
                        "agent_id": t.agent_id,
                        "role": t.role.value,
                        "content": t.content,
                        "entropy": t.epistemic_entropy
                    }
                    for t in thoughts
                ]
            }
            rounds_data.append(round_info)

            # Check delta convergence
            if round_idx > 0 and abs(consensus_conf - previous_consensus) < self.convergence_threshold:
                converged = True
                break
                
            previous_consensus = consensus_conf

        return {
            "converged": converged,
            "total_rounds": len(rounds_data),
            "final_consensus_confidence": previous_consensus,
            "rounds_telemetry": rounds_data
        }


import numpy as np
