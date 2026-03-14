"""
Skills loader and management module for agentskills.io framework integration.

This module provides the core functionality for discovering, loading, and
activating skills following the agentskills.io standards. Each skill is
defined as a directory containing a SKILL.md file with YAML frontmatter.

The SKILLS_PATH environment variable controls where skills are loaded from,
with colon-separated paths supported (e.g., "./skills:/opt/skills").
Defaults to "./skills" if not set.

YAML Frontmatter Format:
    ---
    name: skill-identifier
    description: Human-readable description of the skill
    version: 1.0.0
    author: Your Name
    tags: [tag1, tag2]
    ---

    # Skill Instructions
    Your skill instructions here...
"""

import os
from typing import List, Optional


SKILLS_PATH = os.environ.get(
    "SKILLS_PATH", os.path.expanduser("~/.agentgsd/skills") + ":./skills:packages/agentgsd/skills"
)


class Skill:
    """
    Represents an agent skill following agentskills.io framework.

    A skill is a self-contained unit of functionality with metadata
    and instructions that can be loaded and activated by the agent.

    Attributes:
        name: Unique identifier for the skill
        description: Human-readable description of what the skill does
        location: Directory path where the skill is located
        instructions_content: The skill instructions/guidelines
        metadata: Additional metadata from YAML frontmatter

    Example:
        >>> skill = Skill(
        ...     name="file-organizer",
        ...     description="Organizes files into categories",
        ...     location="packages/agentgsd/skills/file-organizer",
        ...     instructions_content="You are a file organizer...",
        ...     metadata={"version": "1.0.0", "author": "Dev"}
        ... )
        >>> print(skill.name)
        file-organizer
    """

    def __init__(
        self,
        name: str,
        description: str,
        location: str,
        instructions_content: str = "",
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Initialize a Skill instance.

        Args:
            name: Unique identifier for the skill
            description: Human-readable description of the skill
            location: Directory path to the skill files
            instructions_content: The skill's instruction text
            metadata: Additional metadata from YAML frontmatter
        """
        self.name = name
        self.description = description
        self.location = location
        self.instructions_content = instructions_content
        self.metadata = metadata or {}

    @classmethod
    def from_directory(cls, directory: str) -> Optional["Skill"]:
        """
        Load a skill from a directory following agentskills.io standards.

        The directory must contain a SKILL.md file with YAML frontmatter
        in the format expected by the agentskills.io framework.

        Args:
            directory: Path to the skill directory

        Returns:
            Skill instance if successfully loaded, None otherwise

        Example:
            >>> skill = Skill.from_directory("./skills/my-skill")
            >>> if skill:
            ...     print(f"Loaded: {skill.name}")
        """
        skill_md = os.path.join(directory, "SKILL.md")
        if not os.path.isfile(skill_md):
            return None

        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        yaml_content = parts[1].strip()
        body = parts[2].strip()

        metadata = cls._parse_yaml_frontmatter(yaml_content)

        name = metadata.pop("name", os.path.basename(directory))
        description = metadata.pop("description", "")

        return cls(name, description, directory, body, metadata)

    @staticmethod
    def _parse_yaml_frontmatter(yaml_content: str) -> dict:
        """
        Parse simple YAML frontmatter into a dictionary.

        Handles basic key: value pairs commonly found in frontmatter.

        Args:
            yaml_content: The YAML content string to parse

        Returns:
            Dictionary of parsed metadata

        Example:
            >>> metadata = Skill._parse_yaml_frontmatter(
            ...     'name: test\\nversion: 1.0\\nauthor: "John"'
            ... )
            >>> metadata["name"]
            'test'
        """
        metadata = {}
        for line in yaml_content.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip("\"'")

                if val.startswith("[") and val.endswith("]"):
                    val = [v.strip().strip("\"'") for v in val[1:-1].split(",")]

                metadata[key] = val

        return metadata

    def instructions(self) -> str:
        """
        Get the full skill instructions.

        Returns the instructions content, loading from SKILL.md if not
        already cached in memory.

        Returns:
            The skill instructions as a string

        Example:
            >>> skill = Skill.from_directory("./skills/my-skill")
            >>> if skill:
            ...     print(skill.instructions()[:100])
        """
        if self.instructions_content:
            return self.instructions_content

        skill_md = os.path.join(self.location, "SKILL.md")
        if os.path.isfile(skill_md):
            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()
            parts = content.split("---", 2)
            return parts[2].strip() if len(parts) > 2 else ""

        return ""

    def __repr__(self) -> str:
        """Return a string representation of the Skill."""
        return f"Skill(name={self.name!r}, description={self.description!r})"

    def __str__(self) -> str:
        """Return a human-readable string of the Skill."""
        return f"{self.name}: {self.description}"


def load_skills(paths: Optional[List[str]] = None) -> List[Skill]:
    """
    Discover and load all skills from the specified paths.

    Searches each path in the SKILLS_PATH (colon-separated) for directories
    containing valid SKILL.md files with YAML frontmatter.

    Args:
        paths: Optional list of paths to load skills from. If None, uses
               the SKILLS_PATH environment variable. Can be a single path
               string which will be split by colons.

    Returns:
        List of loaded Skill instances

    Example:
        >>> skills = load_skills()
        >>> print(f"Loaded {len(skills)} skills")

        >>> skills = load_skills(["./custom-skills", "/opt/skills"])
        >>> for skill in skills:
        ...     print(f"  - {skill.name}")
    """
    skills = []

    if paths is None:
        path_str = os.environ.get("SKILLS_PATH", SKILLS_PATH)
        paths = path_str.split(":") if path_str else []
    elif isinstance(paths, str):
        paths = paths.split(":")

    for base_path in paths:
        base_path = base_path.strip()
        if not base_path or not os.path.isdir(base_path):
            continue

        for entry in os.listdir(base_path):
            skill_dir = os.path.join(base_path, entry)
            if os.path.isdir(skill_dir):
                skill = Skill.from_directory(skill_dir)
                if skill is not None:
                    skills.append(skill)

    return skills


def skills_xml(paths: Optional[List[str]] = None) -> str:
    """
    Generate XML representation of available skills for system prompts.

    Creates an XML string listing all available skills with their names,
    descriptions, and locations. This format is suitable for inclusion
    in system prompts for LLM-based agents.

    Args:
        paths: Optional list of paths to load skills from. If None, uses
               the SKILLS_PATH environment variable.

    Returns:
        XML string listing available skills, or empty string if no skills

    Example:
        >>> xml = skills_xml()
        >>> print(xml)
        <available_skills>
        <skill name="file-organizer" description="Organizes files" location="packages/agentgsd/skills/file-organizer"/>
        <skill name="code-reviewer" description="Reviews code" location="./skills/code-reviewer"/>
        </available_skills>
    """
    skills = load_skills(paths)
    if not skills:
        return ""

    xml_lines = ["<available_skills>"]
    for skill in skills:
        name_attr = _xml_escape(skill.name)
        desc_attr = _xml_escape(skill.description)
        loc_attr = _xml_escape(skill.location)
        xml_lines.append(
            f'<skill name="{name_attr}" description="{desc_attr}" location="{loc_attr}"/>'
        )
    xml_lines.append("</available_skills>")

    return "\n".join(xml_lines)


def activate_skill(name: str, paths: Optional[List[str]] = None) -> str:
    """
    Activate a skill by name and return its instructions.

    Searches for a skill with the given name and returns its full
    instructions formatted for use by the agent.

    Args:
        name: The name identifier of the skill to activate
        paths: Optional list of paths to search for skills

    Returns:
        Formatted skill instructions, or error message if not found

    Example:
        >>> result = activate_skill("file-organizer")
        >>> print(result[:50])
        === Skill: file-organizer ===
        You are a file organizer...

        >>> result = activate_skill("nonexistent")
        >>> print(result)
        error: skill 'nonexistent' not found
    """
    skills = load_skills(paths)

    for skill in skills:
        if skill.name == name:
            return f"=== Skill: {skill.name} ===\n{skill.instructions()}"

    return f"error: skill '{name}' not found"


def _xml_escape(text: str) -> str:
    """
    Escape special XML characters in a string.

    Args:
        text: The text to escape

    Returns:
        Text with XML special characters escaped
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


__all__ = [
    "Skill",
    "load_skills",
    "skills_xml",
    "activate_skill",
    "SKILLS_PATH",
]
