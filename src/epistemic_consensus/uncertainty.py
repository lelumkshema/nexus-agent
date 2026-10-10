"""
NEXUS-AGENT: Epistemic & Aleatoric Uncertainty Quantification
Formal mathematical decomposition of model predictive uncertainty into:
1. Epistemic Uncertainty (Model ignorance / Hallucination risk)
2. Aleatoric Uncertainty (Inherent stochasticity of domain)
"""

import numpy as np
from typing import List, Dict, Tuple, Any
from ..core.state import EpistemicBelief


class EpistemicUncertaintyQuantifier:
    """Computes Shannon Entropy, Jensen-Shannon Divergence, and Epistemic Variance."""

    def __init__(self, temperature_ensemble: List[float] = [0.2, 0.5, 0.8]):
        self.temperatures = temperature_ensemble

    def calculate_shannon_entropy(self, probabilities: np.ndarray) -> float:
        """Computes H(p) = - sum(p_i * log2(p_i + eps))."""
        p = np.clip(probabilities, 1e-12, 1.0)
        p = p / np.sum(p)
        return float(-np.sum(p * np.log2(p)))

    def decompose_uncertainty(
        self, ensemble_logits: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Decomposes total predictive uncertainty into Epistemic and Aleatoric components.
        Total Uncertainty H(Y|X) = Epistemic (Mutual Info I(Y, \theta | X)) + Aleatoric E[H(Y|X,\theta)]
        """
        # ensemble_logits shape: (num_models, num_classes)
        probs = np.exp(ensemble_logits - np.max(ensemble_logits, axis=-1, keepdims=True))
        probs = probs / np.sum(probs, axis=-1, keepdims=True)

        # Expected distribution (mean predictive distribution)
        mean_probs = np.mean(probs, axis=0)
        total_entropy = self.calculate_shannon_entropy(mean_probs)

        # Expected entropy of individual models (aleatoric uncertainty)
        individual_entropies = [self.calculate_shannon_entropy(p) for p in probs]
        aleatoric_uncertainty = float(np.mean(individual_entropies))

        # Mutual Information (epistemic uncertainty)
        epistemic_uncertainty = max(0.0, total_entropy - aleatoric_uncertainty)

        return total_entropy, epistemic_uncertainty, aleatoric_uncertainty

    def compute_jensen_shannon_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculates JSD between two belief probability vectors."""
        p = p / np.sum(p)
        q = q / np.sum(q)
        m = 0.5 * (p + q)
        kl_pm = np.sum(p * np.log2(np.clip(p / m, 1e-12, 1e12)))
        kl_qm = np.sum(q * np.log2(np.clip(q / m, 1e-12, 1e12)))
        return float(0.5 * (kl_pm + kl_qm))
