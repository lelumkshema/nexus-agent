"""
NEXUS-AGENT: Academic Statistical Analysis Suite
Computes formal statistical tests to validate Master's to PhD upgrade rigor:
- Paired Student's t-test
- Non-parametric Wilcoxon signed-rank test
- Cohen's d effect size metric
- 95% Confidence Intervals
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Any, Tuple


class StatisticalSignificanceAnalyzer:
    """Rigorous academic significance tester comparing experimental treatments."""

    @staticmethod
    def compute_paired_ttest(baseline_scores: List[float], proposed_scores: List[float]) -> Dict[str, Any]:
        """Runs two-sided paired t-test."""
        b = np.array(baseline_scores, dtype=float)
        p = np.array(proposed_scores, dtype=float)
        diff = p - b

        t_stat, p_val = stats.ttest_rel(p, b)
        
        # Cohen's d effect size
        std_diff = np.std(diff, ddof=1) if len(diff) > 1 else 1.0
        cohens_d = float(np.mean(diff) / (std_diff + 1e-12))

        return {
            "test_type": "Paired Student t-test",
            "sample_size": len(baseline_scores),
            "mean_baseline": round(float(np.mean(b)), 4),
            "mean_proposed": round(float(np.mean(p)), 4),
            "mean_difference": round(float(np.mean(diff)), 4),
            "t_statistic": round(float(t_stat), 4),
            "p_value": float(p_val),
            "cohens_d": round(cohens_d, 4),
            "is_significant_p05": bool(p_val < 0.05),
            "is_significant_p01": bool(p_val < 0.01),
            "is_significant_p001": bool(p_val < 0.001),
        }

    @staticmethod
    def compute_wilcoxon_test(baseline_scores: List[float], proposed_scores: List[float]) -> Dict[str, Any]:
        """Runs Wilcoxon signed-rank non-parametric test."""
        b = np.array(baseline_scores, dtype=float)
        p = np.array(proposed_scores, dtype=float)
        diff = p - b

        # Handle identical vectors
        if np.all(diff == 0):
            return {
                "test_type": "Wilcoxon Signed-Rank Test",
                "statistic": 0.0,
                "p_value": 1.0,
                "is_significant": False
            }

        w_stat, p_val = stats.wilcoxon(p, b, zero_method="pratt")
        return {
            "test_type": "Wilcoxon Signed-Rank Test",
            "statistic": round(float(w_stat), 4),
            "p_value": float(p_val),
            "is_significant_p05": bool(p_val < 0.05),
            "is_significant_p01": bool(p_val < 0.01)
        }

    @staticmethod
    def compute_confidence_intervals(scores: List[float], confidence: float = 0.95) -> Tuple[float, float, float]:
        """Computes mean and [lower, upper] confidence bounds."""
        arr = np.array(scores, dtype=float)
        mean = float(np.mean(arr))
        n = len(arr)
        if n < 2:
            return mean, mean, mean
        sem = stats.sem(arr)
        h = sem * stats.t.ppf((1 + confidence) / 2., n - 1)
        return round(mean, 4), round(mean - h, 4), round(mean + h, 4)
