"""
NEXUS-AGENT: Monte Carlo Tree Search over Agent Thought Graphs (MCTS-ATG)
Explores agent reasoning trajectories using Upper Confidence Bounds (UCB1)
and prunes paths that violate formal temporal logic invariants.
"""

import math
import random
from typing import Dict, List, Optional, Tuple, Any
from ..core.state import ThoughtNode, VerificationStatus, AgentRole
from .ltl_verifier import LTLFormalVerifier


class MonteCarloThoughtTreeSearch:
    """MCTS planner that reasons over cognitive paths with formal safety pruning."""

    def __init__(
        self,
        exploration_constant: float = 1.414,
        max_rollout_depth: int = 5,
        formal_verifier: Optional[LTLFormalVerifier] = None
    ):
        self.c = exploration_constant
        self.max_depth = max_rollout_depth
        self.verifier = formal_verifier or LTLFormalVerifier()
        self.nodes: Dict[str, ThoughtNode] = {}
        self.root_id: Optional[str] = None

    def initialize_root(self, goal_description: str) -> ThoughtNode:
        """Initializes the search tree root node."""
        root = ThoughtNode(
            content=f"Root Goal: {goal_description}",
            action_type="INIT",
            role=AgentRole.ORCHESTRATOR
        )
        self.nodes[root.id] = root
        self.root_id = root.id
        return root

    def select_best_child(self, node_id: str) -> Optional[ThoughtNode]:
        """Selects child maximizing UCB1 with epistemic exploration bonus."""
        parent = self.nodes[node_id]
        if not parent.children_ids:
            return None

        best_score = -float('inf')
        best_child = None

        for child_id in parent.children_ids:
            child = self.nodes[child_id]
            # Pruned / invalid nodes are ignored
            if child.verification_status == VerificationStatus.PRUNED:
                continue

            if child.visit_count == 0:
                # Unvisited nodes prioritized
                return child

            # UCB1 Formula: Q(s, a) + c * sqrt(ln(N(s)) / N(s, a)) - EpistemicPenalty
            exploitation = child.mean_q_value
            exploration = self.c * math.sqrt(math.log(parent.visit_count + 1) / (child.visit_count + 1e-6))
            epistemic_adjustment = (1.0 - child.epistemic_entropy) * 0.2

            score = exploitation + exploration + epistemic_adjustment
            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def expand(self, parent_id: str, candidate_thoughts: List[ThoughtNode]) -> List[ThoughtNode]:
        """Expands node by adding valid candidate thoughts and pruning formal violations."""
        parent = self.nodes[parent_id]
        added_children = []

        for candidate in candidate_thoughts:
            candidate.parent_id = parent_id
            # Formal verification check
            is_valid, reason = self.verifier.verify_thought_node(candidate, [])
            if is_valid:
                candidate.verification_status = VerificationStatus.VERIFIED_VALID
                self.nodes[candidate.id] = candidate
                parent.children_ids.append(candidate.id)
                added_children.append(candidate)
            else:
                candidate.verification_status = VerificationStatus.PRUNED
                self.nodes[candidate.id] = candidate

        return added_children

    def backpropagate(self, path: List[str], reward: float):
        """Propagates evaluation reward back up the tree to the root."""
        for node_id in reversed(path):
            node = self.nodes[node_id]
            node.visit_count += 1
            node.total_reward += reward

    def run_search_iteration(self, candidate_generator_fn) -> Tuple[List[str], float]:
        """Runs a full MCTS cycle: Selection -> Expansion -> Rollout / Simulation -> Backpropagation."""
        if not self.root_id:
            raise ValueError("Root node not initialized.")

        current = self.nodes[self.root_id]
        path = [current.id]

        # 1. Selection
        while current.children_ids:
            next_child = self.select_best_child(current.id)
            if not next_child:
                break
            current = next_child
            path.append(current.id)

        # 2. Expansion (if unvisited or leaf)
        if current.visit_count > 0 and len(path) < self.max_depth:
            candidates = candidate_generator_fn(current)
            new_children = self.expand(current.id, candidates)
            if new_children:
                current = new_children[0]
                path.append(current.id)

        # 3. Rollout / Reward Evaluation
        reward = self.evaluate_node_reward(current)

        # 4. Backpropagation
        self.backpropagate(path, reward)

        return path, reward

    def evaluate_node_reward(self, node: ThoughtNode) -> float:
        """Computes empirical task reward combining formal correctness and epistemic confidence."""
        if node.verification_status == VerificationStatus.PRUNED:
            return -1.0
        # Reward function: R = Correctness(1.0) - Entropy(0.3) + ActionBonus
        action_bonus = 0.2 if node.action_type in ("VERIFY", "CONCLUDE") else 0.05
        reward = 0.70 * (1.0 - node.epistemic_entropy) + action_bonus
        return float(min(1.0, max(0.0, reward)))
