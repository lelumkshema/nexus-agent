"""NEXUS-AGENT: Benchmark & Statistical Evaluation Suite."""
from .tasks import get_academic_benchmark_tasks
from .baselines import BaselineEvaluator
from .statistical_analysis import StatisticalSignificanceAnalyzer

__all__ = [
    "get_academic_benchmark_tasks",
    "BaselineEvaluator",
    "StatisticalSignificanceAnalyzer",
]
