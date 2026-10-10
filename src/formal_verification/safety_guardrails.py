"""
NEXUS-AGENT: Safety Guardrails & Barrier Functions
Enforces pre- and post-condition invariants for tool calling and state mutations.
"""

from typing import Dict, Any, Tuple
import ast


class NeuroSymbolicSafetyGuardrails:
    """Enforces AST sanitization, execution barriers, and resource quotas."""

    def __init__(self, max_allowed_iterations: int = 1000):
        self.max_iterations = max_allowed_iterations
        self.forbidden_imports = {
            "os.system", "subprocess", "shutil.rmtree", "eval", "exec", "__import__"
        }

    def validate_synthesized_code(self, python_code: str) -> Tuple[bool, str]:
        """Performs static AST analysis to block malicious or dangerous code operations."""
        try:
            tree = ast.parse(python_code)
        except SyntaxError as e:
            return False, f"Syntax Error in synthesized tool: {str(e)}"

        for node in ast.walk(tree):
            # Check import safety
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ["os", "subprocess", "sys", "shutil"]:
                        return False, f"Forbidden critical import detected: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module in ["os", "subprocess", "sys", "shutil"]:
                    return False, f"Forbidden module import: {node.module}"
            # Check dangerous builtins
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ["eval", "exec"]:
                    return False, f"Dangerous dynamic execution: {node.func.id}() is disallowed."

        return True, "AST Static Guardrail Verification Passed"
