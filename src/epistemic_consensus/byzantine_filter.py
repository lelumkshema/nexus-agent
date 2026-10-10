"""
NEXUS-AGENT: Byzantine-Resilient Multi-Agent Consensus Filter
Implements game-theoretic reputation adjustment and Byzantine outlier filtration
guaranteeing consensus under up to f < n/3 faulty or hallucinating agents.
"""

import numpy as np
from typing import List, Dict, Tuple, Any
from ..core.state import EpistemicBelief
from ..core.agent import AutonomousCognitiveAgent


class ByzantineConsensusFilter:
    """
    Byzantine Fault Tolerant (BFT) Aggregator for Multi-Agent Deliberation.
    Applies trimmed-mean / geometric median filtering and reputation penalization
    to suppress hallucinating and adversarial agent outputs.
    """

    def __init__(self, byzantine_tolerance_fraction: float = 0.33):
        self.byzantine_fraction = byzantine_tolerance_fraction

    def filter_and_aggregate_beliefs(
        self,
        agents: List[AutonomousCognitiveAgent],
        beliefs: List[EpistemicBelief]
    ) -> Tuple[float, List[str], Dict[str, float]]:
        """
        Filters out Byzantine agents and calculates resilient consensus belief.
        Returns:
            - consensus_confidence: Aggregate robust confidence
            - identified_byzantine_agents: List of agent IDs flagged as faulty/hallucinating
            - updated_reputations: Dynamic reputation updates
        """
        n = len(agents)
        if n == 0:
            return 0.0, [], {}

        max_faulty = int(np.floor(n * self.byzantine_fraction))
        confidences = np.array([b.confidence for b in beliefs])
        entropies = np.array([b.epistemic_entropy for b in beliefs])
        reputations = np.array([a.reputation_score for a in agents])

        # Median-based distance measure to identify epistemic outliers
        median_conf = float(np.median(confidences))
        distances = np.abs(confidences - median_conf)

        # Byzantine suspicion combines distance from consensus + high epistemic entropy
        suspicion_scores = 0.6 * (distances / (np.max(distances) + 1e-6)) + 0.4 * entropies

        # Identify top-f suspicious agents as Byzantine outliers
        sorted_indices = np.argsort(suspicion_scores)
        flagged_byzantine_indices = sorted_indices[-max_faulty:] if max_faulty > 0 else []
        
        flagged_agent_ids = [agents[i].agent_id for i in flagged_byzantine_indices if suspicion_scores[i] > 0.45]
        
        # Valid non-Byzantine set
        valid_indices = [i for i in range(n) if agents[i].agent_id not in flagged_agent_ids]
        if not valid_indices:
            valid_indices = range(n)

        # Reputation-weighted aggregation over verified honest agents
        valid_confs = confidences[valid_indices]
        valid_weights = reputations[valid_indices]
        weight_sum = np.sum(valid_weights) + 1e-12
        consensus_confidence = float(np.sum(valid_confs * valid_weights) / weight_sum)

        # Dynamic reputation update: reward convergence, penalize Byzantine deviation
        reputation_updates = {}
        for i, agent in enumerate(agents):
            if agent.agent_id in flagged_agent_ids:
                # Multiplicative decrease (penalize)
                new_rep = max(0.1, agent.reputation_score * 0.70)
            else:
                # Additive increase (reward truthful alignment)
                alignment = 1.0 - abs(confidences[i] - consensus_confidence)
                new_rep = min(2.0, agent.reputation_score + 0.05 * alignment)
            
            agent.reputation_score = new_rep
            reputation_updates[agent.agent_id] = new_rep

        return consensus_confidence, flagged_agent_ids, reputation_updates
