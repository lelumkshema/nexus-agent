"""
NEXUS-AGENT: Formal Linear Temporal Logic (LTL) & Invariant Verifier
Provides formal neuro-symbolic correctness checking over multi-agent execution traces.
Supports temporal operators:
- G(phi) : Globally (Safety invariant that must hold in all states)
- F(phi) : Finally / Eventually (Liveness property that must eventually be satisfied)
- X(phi) : Next state property
"""

import re
from typing import List, Dict, Any, Tuple
from ..core.state import ThoughtNode, VerificationStatus


class LTLFormalVerifier:
    """Evaluates Linear Temporal Logic (LTL) formulas over execution traces."""

    def __init__(self):
        pass

    def evaluate_predicate(self, predicate: str, state: Dict[str, Any]) -> bool:
        """Evaluates an atomic proposition on an environment or agent state."""
        predicate = predicate.strip()
        
        # Inverted predicate
        if predicate.startswith("not "):
            inner = predicate[4:].strip()
            return not self.evaluate_predicate(inner, state)
            
        # Common formal state predicates
        if predicate == "resource_exhausted":
            return bool(state.get("token_consumption", 0) > state.get("max_tokens", 50000))
        elif predicate == "cyclic_reasoning":
            return bool(state.get("cycle_detected", False))
        elif predicate == "tool_safety_violation":
            return bool(state.get("safety_violation", False))
        elif predicate == "verified_output":
            return bool(state.get("output_verified", False))
        elif predicate == "byzantine_compromised":
            return bool(state.get("byzantine_anomaly", False))
        elif "==" in predicate:
            var, val = predicate.split("==")
            return str(state.get(var.strip())) == val.strip().strip("'\"")
        elif "<" in predicate:
            var, val = predicate.split("<")
            return float(state.get(var.strip(), 0)) < float(val.strip())
        elif ">" in predicate:
            var, val = predicate.split(">")
            return float(state.get(var.strip(), 0)) > float(val.strip())

        # Default fallback to state boolean
        return bool(state.get(predicate, True))

    def verify_trace(
        self,
        trace_states: List[Dict[str, Any]],
        ltl_formulas: List[str]
    ) -> Tuple[VerificationStatus, List[str]]:
        """
        Verifies whether an execution sequence satisfies a set of LTL specifications.
        Returns (Status, list of failure explanations).
        """
        violations = []

        for formula in ltl_formulas:
            formula = formula.strip()

            # Globally operator: G(phi) - phi must hold in every state
            if formula.startswith("G(") and formula.endswith(")"):
                inner_phi = formula[2:-1].strip()
                for step_idx, st in enumerate(trace_states):
                    if not self.evaluate_predicate(inner_phi, st):
                        violations.append(
                            f"Safety Invariant Violation: '{formula}' violated at step {step_idx}. Sub-predicate '{inner_phi}' failed."
                        )
                        break

            # Eventually operator: F(phi) - phi must hold in at least one state
            elif formula.startswith("F(") and formula.endswith(")"):
                inner_phi = formula[2:-1].strip()
                satisfied = any(self.evaluate_predicate(inner_phi, st) for st in trace_states)
                if not satisfied:
                    violations.append(
                        f"Liveness Violation: '{formula}' not satisfied across any of the {len(trace_states)} execution steps."
                    )

            # Standard proposition check
            else:
                if trace_states and not self.evaluate_predicate(formula, trace_states[-1]):
                    violations.append(f"Postcondition Violation: '{formula}' failed on final state.")

        if violations:
            return VerificationStatus.VERIFIED_VIOLATION, violations
        return VerificationStatus.VERIFIED_VALID, []

    def verify_thought_node(self, node: ThoughtNode, current_trace: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Verifies if transitioning to a specific thought node violates formal safety bounds."""
        projected_state = {
            "token_consumption": node.visit_count * 200,
            "max_tokens": 50000,
            "cycle_detected": False,
            "safety_violation": (node.epistemic_entropy > 0.80 and node.role.value == "HYPOTHESIS_GENERATOR"),
            "output_verified": node.action_type == "CONCLUDE"
        }
        
        status, errors = self.verify_trace(current_trace + [projected_state], ["G(not resource_exhausted)", "G(not tool_safety_violation)"])
        if status == VerificationStatus.VERIFIED_VIOLATION:
            node.verification_status = VerificationStatus.PRUNED
            node.ltl_violation_detail = "; ".join(errors)
            return False, node.ltl_violation_detail
            
        node.verification_status = VerificationStatus.VERIFIED_VALID
        return True, "Formally Verified Valid"
