"""
NEXUS-AGENT: Core State and Epistemic Representation
Formal definition of Agent Belief States, Thought Nodes, and Transition Graphs.
Part of the unified Master's to PhD Research Architecture.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
import time
import uuid


class VerificationStatus(Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED_VALID = "VERIFIED_VALID"
    VERIFIED_VIOLATION = "VERIFIED_VIOLATION"
    PRUNED = "PRUNED"


class AgentRole(Enum):
    ORCHESTRATOR = "ORCHESTRATOR"
    HYPOTHESIS_GENERATOR = "HYPOTHESIS_GENERATOR"
    FORMAL_VERIFIER = "FORMAL_VERIFIER"
    TOOL_SYNTHESIZER = "TOOL_SYNTHESIZER"
    ADVERSARIAL_CRITIC = "ADVERSARIAL_CRITIC"


@dataclass
class EpistemicBelief:
    """Represents an agent's quantified belief over an assertion or sub-plan."""
    claim: str
    confidence: float  # [0.0, 1.0]
    epistemic_entropy: float  # Quantified model ignorance / uncertainty
    aleatoric_variance: float  # Stochastic environmental noise
    supporting_evidence: List[str] = field(default_factory=list)
    counter_evidence: List[str] = field(default_factory=list)
    byzantine_suspicion_score: float = 0.0


@dataclass
class ThoughtNode:
    """Node in the Monte Carlo Thought-Tree Search (MCTS-ATG)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_id: Optional[str] = None
    agent_id: str = "agent-0"
    role: AgentRole = AgentRole.HYPOTHESIS_GENERATOR
    content: str = ""
    action_type: str = "THINK"  # THINK, TOOL_CALL, SYNTHESIZE, VERIFY, CONCLUDE
    tool_name: Optional[str] = None
    tool_args: Dict[str, Any] = field(default_factory=dict)
    tool_output: Optional[Any] = None
    
    # MCTS Statistics
    visit_count: int = 0
    total_reward: float = 0.0
    prior_probability: float = 1.0
    
    # Formal Verification Metadata
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    ltl_invariants_checked: List[str] = field(default_factory=list)
    ltl_violation_detail: Optional[str] = None
    
    # Epistemic Metrics
    epistemic_entropy: float = 0.0
    consensus_weight: float = 1.0
    
    children_ids: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    @property
    def mean_q_value(self) -> float:
        return (self.total_reward / self.visit_count) if self.visit_count > 0 else 0.0


@dataclass
class TaskSpecification:
    """Formal definition of a task under the POMDP formulation."""
    task_id: str
    goal_description: str
    safety_invariants: List[str]  # e.g., ["G(not resource_exhausted)", "F(verified_output)"]
    available_tools: List[str]
    max_deliberation_steps: int = 25
    epistemic_threshold: float = 0.35  # Threshold below which belief is accepted
    byzantine_tolerance_ratio: float = 0.33  # f < n/3 tolerance
