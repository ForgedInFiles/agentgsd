"""
Shared skills system module for agent-skills.io framework integration.

This module provides skill loading, management, and activation functionality
following the agent-skills.io standards. Skills are defined as directories
containing a SKILL.md file with YAML frontmatter.

Example:
    >>> from shared.skills import load_skills, activate_skill, skills_xml
    >>> skills = load_skills()
    >>> for skill in skills:
    ...     print(f"{skill.name}: {skill.description}")
    >>> instructions = activate_skill("my-skill")
"""

from shared.skills.loader import (
    Skill,
    load_skills,
    skills_xml,
    activate_skill,
)

__all__ = [
    "Skill",
    "load_skills",
    "skills_xml",
    "activate_skill",
]
