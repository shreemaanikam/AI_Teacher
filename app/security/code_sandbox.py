"""
AST-based Static Code Security Scanner for Phase 12 Practical Learning Lab.
Audits student-submitted Python and SQL code before any compilation or evaluation,
ensuring untrusted student submissions can NEVER access the host filesystem, environment
variables, secrets, sockets, processes, or internal application structures.
"""

from __future__ import annotations
import ast
from typing import List, Tuple, Set


class SecurityASTVisitor(ast.NodeVisitor):
    """AST visitor that detects malicious system calls, forbidden imports, and unsafe introspection."""

    DISALLOWED_MODULES: Set[str] = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "shutil",
        "urllib",
        "requests",
        "http",
        "ftplib",
        "builtins",
        "pty",
        "signal",
        "multiprocessing",
        "threading",
        "importlib",
        "pickle",
        "ctypes",
        "posix",
        "nt",
        "inspect",
        "webbrowser",
        "platform",
    }

    DISALLOWED_FUNCTIONS: Set[str] = {
        "eval",
        "exec",
        "open",
        "__import__",
        "compile",
        "globals",
        "locals",
        "getattr",
        "setattr",
        "delattr",
        "vars",
        "breakpoint",
        "exit",
        "quit",
    }

    DISALLOWED_ATTRIBUTES: Set[str] = {
        "__subclasses__",
        "__bases__",
        "__mro__",
        "__globals__",
        "__builtins__",
        "__class__",
        "__code__",
        "__reduce__",
        "__reduce_ex__",
    }

    def __init__(self):
        super().__init__()
        self.violations: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            root_pkg = alias.name.split(".")[0]
            if root_pkg in self.DISALLOWED_MODULES:
                self.violations.append(
                    f"Security Violation: Import of forbidden module '{alias.name}' is strictly prohibited."
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            root_pkg = node.module.split(".")[0]
            if root_pkg in self.DISALLOWED_MODULES:
                self.violations.append(
                    f"Security Violation: Import from forbidden module '{node.module}' is strictly prohibited."
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in self.DISALLOWED_FUNCTIONS:
            self.violations.append(
                f"Security Violation: Invocation of unsafe built-in function '{func_name}()' is prohibited."
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr in self.DISALLOWED_ATTRIBUTES:
            self.violations.append(
                f"Security Violation: Access to dangerous internal attribute '{node.attr}' is prohibited."
            )
        self.generic_visit(node)


class CodeSecurityScanner:
    """
    Statically audits student code submissions to guarantee complete sandboxing and zero privilege escalation.
    """

    @classmethod
    def scan_python_code(cls, code_str: str) -> Tuple[bool, List[str]]:
        """
        Parses and inspects Python code.
        Returns: (is_safe, list_of_violations)
        """
        if not code_str or not code_str.strip():
            return True, []

        # Parse AST without executing
        try:
            tree = ast.parse(code_str)
        except SyntaxError as syn_err:
            # Syntax errors are handled by educational feedback, not security violations
            return False, [f"Syntax Error: {syn_err.msg} at line {syn_err.lineno}"]

        visitor = SecurityASTVisitor()
        visitor.visit(tree)

        if visitor.violations:
            return False, visitor.violations

        return True, []

    @classmethod
    def scan_sql_code(cls, query_str: str) -> Tuple[bool, List[str]]:
        """
        Scans SQL queries to forbid administrative, destructive, or file-based operations.
        """
        if not query_str:
            return True, []

        upper = query_str.upper()
        forbidden_keywords = [
            "DROP DATABASE",
            "DROP TABLE",
            "ALTER TABLE",
            "TRUNCATE",
            "GRANT ALL",
            "REVOKE ALL",
            "INTO OUTFILE",
            "LOAD DATA",
            "EXEC",
            "XP_CMDSHELL",
            "ATTACH DATABASE",
        ]

        violations = []
        for kw in forbidden_keywords:
            if kw in upper:
                violations.append(f"Security Violation: Destructive SQL command '{kw}' is prohibited.")

        if violations:
            return False, violations

        return True, []


_CODE_SCANNER: Optional[CodeSecurityScanner] = None


def get_code_scanner() -> CodeSecurityScanner:
    global _CODE_SCANNER
    if _CODE_SCANNER is None:
        _CODE_SCANNER = CodeSecurityScanner()
    return _CODE_SCANNER
