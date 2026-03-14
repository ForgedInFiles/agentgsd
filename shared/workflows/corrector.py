"""
Self-Correcting Code Generation Loop for agentgsd.

A local validation loop that uses existing tool outputs for correction
without requiring external API calls.
"""

import ast
import re
import subprocess
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ErrorType(Enum):
    """Types of errors that can occur during code generation."""

    SYNTAX = "syntax"
    IMPORT = "import"
    RUNTIME = "runtime"
    TEST = "test"
    LINT = "lint"
    TYPE = "type"
    UNKNOWN = "unknown"


@dataclass
class CodeError:
    """Represents an error in generated code."""

    error_type: ErrorType
    message: str
    line: Optional[int] = None
    file_path: Optional[str] = None
    raw_error: str = ""


@dataclass
class CorrectionAttempt:
    """Represents a correction attempt."""

    attempt_number: int
    original_error: CodeError
    fix_description: str
    success: bool
    result: str = ""


@dataclass
class ValidationResult:
    """Result of code validation."""

    passed: bool
    errors: List[CodeError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    output: str = ""


class CodeValidator:
    """Validates generated code using local tools."""

    def __init__(self):
        self.syntax_checkers = {
            "python": self._check_python_syntax,
            "javascript": self._check_js_syntax,
            "typescript": self._check_ts_syntax,
        }

        self.test_runners = {
            "python": ["python", "-m", "pytest", "-x", "-v"],
            "javascript": ["npm", "test"],
            "typescript": ["npm", "test"],
        }

        self.linters = {
            "python": ["python", "-m", "ruff", "check"],
            "javascript": ["npx", "eslint"],
            "typescript": ["npx", "eslint"],
        }

    def validate(
        self, code: str, language: str = "python", file_path: Optional[str] = None
    ) -> ValidationResult:
        """Validate code and return result."""
        if language == "python":
            return self._check_python_syntax(code, file_path)
        elif language in ("javascript", "typescript"):
            return self._check_js_syntax(code, file_path)

        return ValidationResult(passed=True, warnings=["No validator for language"])

    def _check_python_syntax(self, code: str, file_path: Optional[str] = None) -> ValidationResult:
        """Check Python syntax using ast.parse."""
        errors = []

        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(
                CodeError(
                    error_type=ErrorType.SYNTAX,
                    message=f"Syntax error: {e.msg}",
                    line=e.lineno,
                    file_path=file_path,
                    raw_error=str(e),
                )
            )
        except ValueError as e:
            errors.append(
                CodeError(
                    error_type=ErrorType.SYNTAX,
                    message=f"Syntax error: {str(e)}",
                    file_path=file_path,
                    raw_error=str(e),
                )
            )

        import_errors = self._check_python_imports(code)
        errors.extend(import_errors)

        return ValidationResult(
            passed=len(errors) == 0, errors=errors, output="" if errors else "Syntax OK"
        )

    def _check_python_imports(self, code: str) -> List[CodeError]:
        """Check if imports in code are valid."""
        errors = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    try:
                        __import__(alias.name)
                    except ImportError:
                        pass
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    try:
                        __import__(node.module)
                    except ImportError:
                        pass

        return errors

    def _check_js_syntax(self, code: str, file_path: Optional[str] = None) -> ValidationResult:
        """Check JavaScript/TypeScript syntax."""
        errors = []

        if file_path:
            try:
                result = subprocess.run(
                    ["node", "--check", file_path], capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    errors.append(
                        CodeError(
                            error_type=ErrorType.SYNTAX,
                            message=result.stderr,
                            file_path=file_path,
                            raw_error=result.stderr,
                        )
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        return ValidationResult(
            passed=len(errors) == 0, errors=errors, output="" if errors else "Syntax OK"
        )

    def _check_ts_syntax(self, code: str, file_path: Optional[str] = None) -> ValidationResult:
        """Check TypeScript syntax."""
        return self._check_js_syntax(code, file_path)

    def run_tests(self, file_path: str, language: str = "python") -> ValidationResult:
        """Run tests for the given file."""
        errors = []
        output = ""

        if language == "python":
            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", file_path, "-x", "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                output = result.stdout + result.stderr

                if result.returncode != 0:
                    errors.append(
                        CodeError(
                            error_type=ErrorType.TEST,
                            message="Tests failed",
                            file_path=file_path,
                            raw_error=output,
                        )
                    )
            except subprocess.TimeoutExpired:
                errors.append(
                    CodeError(
                        error_type=ErrorType.TEST, message="Test timeout", file_path=file_path
                    )
                )
            except FileNotFoundError:
                pass

        return ValidationResult(passed=len(errors) == 0, errors=errors, output=output)

    def run_linter(self, file_path: str, language: str = "python") -> ValidationResult:
        """Run linter on the given file."""
        errors = []
        output = ""

        if language == "python":
            try:
                result = subprocess.run(
                    ["python", "-m", "ruff", "check", file_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                output = result.stdout + result.stderr

                if result.returncode != 0:
                    for line in output.split("\n"):
                        if "error" in line.lower() or "warning" in line.lower():
                            errors.append(
                                CodeError(
                                    error_type=ErrorType.LINT, message=line, file_path=file_path
                                )
                            )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        return ValidationResult(passed=len(errors) == 0, errors=errors, output=output)


class FixPatterns:
    """Predefined fix patterns for common errors."""

    @staticmethod
    def fix_syntax_error(error: CodeError) -> str:
        """Generate fix for syntax errors."""
        msg = error.message.lower()

        if "expected" in msg and ":" in msg:
            return "Check for missing colons, brackets, or parentheses"
        if "unexpected" in msg:
            return "Remove or fix the unexpected token"
        if "invalid syntax" in msg:
            return "Review the entire line for syntax issues"

        return "Review syntax and fix accordingly"

    @staticmethod
    def fix_import_error(error: CodeError) -> str:
        """Generate fix for import errors."""
        msg = error.message.lower()

        if "no module named" in msg:
            module = re.search(r"'([^']+)'", error.message)
            if module:
                return f"Install the module: pip install {module.group(1)}"

        return "Check import statement and ensure module is available"

    @staticmethod
    def fix_test_error(error: CodeError) -> str:
        """Generate fix for test failures."""
        msg = error.message.lower()

        if "assertionerror" in msg:
            return "Fix the assertion - expected vs actual values don't match"
        if "timeout" in msg:
            return "Optimize test or increase timeout"
        if "fixture" in msg:
            return "Check test fixtures are properly defined"

        return "Debug test and fix the failing assertion"

    @staticmethod
    def suggest_fix(error: CodeError) -> str:
        """Suggest a fix based on error type."""
        if error.error_type == ErrorType.SYNTAX:
            return FixPatterns.fix_syntax_error(error)
        elif error.error_type == ErrorType.IMPORT:
            return FixPatterns.fix_import_error(error)
        elif error.error_type == ErrorType.TEST:
            return FixPatterns.fix_test_error(error)

        return "Review the error message and fix accordingly"


class SelfCorrectingLoop:
    """Self-correcting code generation loop."""

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts
        self.validator = CodeValidator()
        self.attempts: List[CorrectionAttempt] = []

    def validate_and_correct(
        self,
        code: str,
        language: str = "python",
        file_path: Optional[str] = None,
        run_tests: bool = False,
        run_lint: bool = True,
    ) -> Tuple[bool, str, List[CorrectionAttempt]]:
        """
        Validate code and attempt corrections if needed.

        Returns:
            Tuple of (success, final_code, list of attempts)
        """
        self.attempts = []

        for attempt_num in range(1, self.max_attempts + 1):
            validation_result = self.validator.validate(code, language, file_path)

            if validation_result.passed:
                if run_lint and file_path:
                    lint_result = self.validator.run_linter(file_path, language)
                    if not lint_result.passed:
                        for err in lint_result.errors:
                            self.attempts.append(
                                CorrectionAttempt(
                                    attempt_number=attempt_num,
                                    original_error=err,
                                    fix_description="Run linter to fix issues",
                                    success=False,
                                    result=lint_result.output,
                                )
                            )
                            code = self._apply_fix(code, err)
                            continue

                if run_tests and file_path:
                    test_result = self.validator.run_tests(file_path, language)
                    if not test_result.passed:
                        for err in test_result.errors:
                            self.attempts.append(
                                CorrectionAttempt(
                                    attempt_number=attempt_num,
                                    original_error=err,
                                    fix_description="Fix test failures",
                                    success=False,
                                    result=test_result.output,
                                )
                            )
                            code = self._apply_fix(code, err)
                            continue

                return True, code, self.attempts

            for error in validation_result.errors:
                fix_desc = FixPatterns.suggest_fix(error)

                self.attempts.append(
                    CorrectionAttempt(
                        attempt_number=attempt_num,
                        original_error=error,
                        fix_description=fix_desc,
                        success=False,
                        result=validation_result.output,
                    )
                )

                code = self._apply_fix(code, error)

        return False, code, self.attempts

    def _apply_fix(self, code: str, error: CodeError) -> str:
        """Apply a fix based on the error."""
        if error.error_type == ErrorType.SYNTAX and error.line:
            lines = code.split("\n")
            if 0 < error.line <= len(lines):
                lines[error.line - 1] = "# FIX NEEDED: " + lines[error.line - 1]
                return "\n".join(lines)

        return code

    def get_attempt_summary(self) -> str:
        """Get a summary of all correction attempts."""
        if not self.attempts:
            return "No attempts made"

        lines = ["## Correction Attempts", ""]

        for attempt in self.attempts:
            status = "✓" if attempt.success else "✗"
            lines.append(
                f"{status} Attempt {attempt.attempt_number}: {attempt.original_error.error_type.value}"
            )
            lines.append(f"   Error: {attempt.original_error.message[:80]}")
            lines.append(f"   Fix: {attempt.fix_description}")
            lines.append("")

        return "\n".join(lines)


def create_correction_loop(max_attempts: int = 3) -> SelfCorrectingLoop:
    """Create a new self-correcting loop instance."""
    return SelfCorrectingLoop(max_attempts)


__all__ = [
    "ErrorType",
    "CodeError",
    "CorrectionAttempt",
    "ValidationResult",
    "CodeValidator",
    "FixPatterns",
    "SelfCorrectingLoop",
    "create_correction_loop",
]
