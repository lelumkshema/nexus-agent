"""
NEXUS-AGENT: Neuro-Symbolic Skill Registry & Skill Graph
Maintains a Directed Acyclic Graph (DAG) of synthesized tools, tracking dependencies,
execution counts, success rates, and compositional combinations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional
import time


@dataclass
class SynthesizedSkill:
    name: str
    specification: str
    code: str
    callable_func: Optional[Callable] = None
    dependencies: List[str] = field(default_factory=list)
    invocation_count: int = 0
    successful_invocations: int = 0
    created_at: float = field(default_factory=time.time)

    @property
    def reliability_score(self) -> float:
        if self.invocation_count == 0:
            return 1.0
        return self.successful_invocations / self.invocation_count


class NeuroSymbolicSkillGraph:
    """Manages verified tools and their compositional dependency graph."""

    def __init__(self):
        self.skills: Dict[str, SynthesizedSkill] = {}

    def register_skill(
        self,
        name: str,
        specification: str,
        code: str,
        callable_func: Callable,
        dependencies: Optional[List[str]] = None
    ) -> SynthesizedSkill:
        """Registers a newly verified skill into the graph."""
        skill = SynthesizedSkill(
            name=name,
            specification=specification,
            code=code,
            callable_func=callable_func,
            dependencies=dependencies or []
        )
        self.skills[name] = skill
        return skill

    def execute_skill(self, name: str, *args, **kwargs) -> Any:
        """Executes a registered skill and updates telemetry statistics."""
        if name not in self.skills:
            raise KeyError(f"Skill '{name}' not found in registry.")

        skill = self.skills[name]
        skill.invocation_count += 1
        try:
            result = skill.callable_func(*args, **kwargs)
            skill.successful_invocations += 1
            return result
        except Exception as e:
            raise RuntimeError(f"Skill execution failed for '{name}': {str(e)}")

    def get_graph_summary(self) -> List[Dict[str, Any]]:
        """Returns JSON-serializable representation of the skill graph."""
        return [
            {
                "name": s.name,
                "specification": s.specification,
                "dependencies": s.dependencies,
                "invocations": s.invocation_count,
                "reliability": round(s.reliability_score, 3),
            }
            for s in self.skills.values()
        ]
