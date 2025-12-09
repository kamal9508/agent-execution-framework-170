"""Code analysis tools."""
import ast
import logging
from typing import Dict, List, Any
from radon.complexity import cc_visit
from radon.metrics import mi_visit

from app.models.state import WorkflowState

logger = logging.getLogger(__name__)


def extract_functions(state: WorkflowState, **kwargs) -> Dict[str, Any]:
    """Extract functions from code.

    Args:
        state: Workflow state containing 'code' key

    Returns:
        Updated state data with functions
    """
    code = state.get("code", "")

    if not code:
        logger.warning("No code found in state")
        return {"functions": [], "function_count": 0}

    try:
        tree = ast.parse(code)
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "line_number": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "has_docstring": ast.get_docstring(node) is not None
                }
                functions.append(func_info)

        logger.info(f"Extracted {len(functions)} functions")

        return {
            "functions": functions,
            "function_count": len(functions)
        }

    except SyntaxError as e:
        logger.error(f"Syntax error in code: {e}")
        return {
            "functions": [],
            "function_count": 0,
            "syntax_error": str(e)
        }


def check_complexity(state: WorkflowState, threshold: int = 10, **kwargs) -> Dict[str, Any]:
    """Check cyclomatic complexity of code.

    Args:
        state: Workflow state containing 'code' key
        threshold: Complexity threshold

    Returns:
        Updated state data with complexity info
    """
    code = state.get("code", "")

    if not code:
        return {"complexity_issues": [], "max_complexity": 0}

    try:
        complexity_data = cc_visit(code)
        issues = []
        max_complexity = 0

        for item in complexity_data:
            if item.complexity > threshold:
                issues.append({
                    "name": item.name,
                    "complexity": item.complexity,
                    "line_number": item.lineno,
                    "type": item.classname or "function"
                })
            max_complexity = max(max_complexity, item.complexity)

        logger.info(
            f"Found {len(issues)} complexity issues (threshold: {threshold})")

        return {
            "complexity_issues": issues,
            "max_complexity": max_complexity,
            "complexity_threshold": threshold
        }

    except Exception as e:
        logger.error(f"Complexity check failed: {e}")
        return {
            "complexity_issues": [],
            "max_complexity": 0,
            "error": str(e)
        }


def detect_issues(state: WorkflowState, **kwargs) -> Dict[str, Any]:
    """Detect basic code quality issues.

    Args:
        state: Workflow state containing 'code' key

    Returns:
        Updated state data with detected issues
    """
    code = state.get("code", "")
    issues = []

    if not code:
        return {"issues": issues, "issue_count": 0}

    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if len(line) > 100 and not stripped.startswith("#"):
            issues.append({
                "line": i,
                "type": "line_too_long",
                "message": "Line exceeds 100 characters"
            })

        if "TODO" in line or "FIXME" in line:
            issues.append({
                "line": i,
                "type": "todo_comment",
                "message": "TODO/FIXME comment found"
            })

        if stripped.startswith("print("):
            issues.append({
                "line": i,
                "type": "debug_statement",
                "message": "Print statement (consider using logging)"
            })

    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    issues.append({
                        "line": node.lineno,
                        "type": "missing_docstring",
                        "message": f"{node.__class__.__name__} '{node.name}' missing docstring"
                    })
    except:
        pass

    logger.info(f"Detected {len(issues)} issues")

    return {
        "issues": issues,
        "issue_count": len(issues)
    }


def suggest_improvements(state: WorkflowState, **kwargs) -> Dict[str, Any]:
    """Generate improvement suggestions based on analysis.

    Args:
        state: Workflow state with analysis results

    Returns:
        Updated state data with suggestions
    """
    suggestions = []

    complexity_issues = state.get("complexity_issues", [])
    if complexity_issues:
        suggestions.append({
            "category": "complexity",
            "priority": "high",
            "message": f"Reduce complexity in {len(complexity_issues)} function(s)",
            "details": [f"{issue['name']} (complexity: {issue['complexity']})"
                        for issue in complexity_issues[:3]]
        })

    issues = state.get("issues", [])
    issue_types = {}
    for issue in issues:
        issue_type = issue["type"]
        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

    for issue_type, count in issue_types.items():
        if issue_type == "missing_docstring":
            suggestions.append({
                "category": "documentation",
                "priority": "medium",
                "message": f"Add docstrings to {count} function(s)/class(es)"
            })
        elif issue_type == "line_too_long":
            suggestions.append({
                "category": "formatting",
                "priority": "low",
                "message": f"Shorten {count} long line(s)"
            })

    total_issues = len(issues) + len(complexity_issues)
    function_count = state.get("function_count", 1)
    quality_score = max(0, 100 - (total_issues / function_count * 10))

    logger.info(
        f"Generated {len(suggestions)} suggestions, quality score: {quality_score:.1f}")

    return {
        "suggestions": suggestions,
        "suggestion_count": len(suggestions),
        "quality_score": quality_score
    }
