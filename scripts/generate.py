#!/usr/bin/env python3
"""Generate distribution directories for all valid skills across agent targets."""

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
DIST_DIR = REPO_ROOT / "dist"
AGENT_TARGETS = [".claude", ".codex", ".gemini"]
JUNK_PATTERNS = {"__pycache__", ".DS_Store", "*.pyc"}

# Import validate_skill from skill-creator scripts
sys.path.insert(0, str(SKILLS_DIR / "skill-creator" / "scripts"))
from quick_validate import validate_skill


def should_ignore(path, names):
    """Return set of names to ignore during copytree."""
    return {n for n in names if n in {"__pycache__", ".DS_Store"} or n.endswith(".pyc")}


def main():
    # Clean dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    # Discover skills (subdirectories of skills/ that contain SKILL.md)
    skill_dirs = sorted(
        d for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()
    )

    if not skill_dirs:
        print("No skills found in skills/")
        sys.exit(1)

    valid_skills = []
    failed_skills = []

    for skill_dir in skill_dirs:
        is_valid, message = validate_skill(skill_dir)
        if is_valid:
            valid_skills.append(skill_dir)
        else:
            failed_skills.append((skill_dir.name, message))
            print(f"  SKIP {skill_dir.name}: {message}")

    if not valid_skills:
        print("\nNo valid skills to generate.")
        sys.exit(1)

    # Copy each valid skill into each agent target
    for agent in AGENT_TARGETS:
        agent_skills_dir = DIST_DIR / agent / "skills"
        for skill_dir in valid_skills:
            dest = agent_skills_dir / skill_dir.name
            shutil.copytree(skill_dir, dest, ignore=should_ignore)

    # Summary
    print(f"\nGenerated {len(valid_skills)} skill(s) for {len(AGENT_TARGETS)} agent(s):")
    for skill_dir in valid_skills:
        print(f"  {skill_dir.name}")
    print(f"\nAgent targets: {', '.join(AGENT_TARGETS)}")
    if failed_skills:
        print(f"\nSkipped {len(failed_skills)} skill(s) due to validation failures:")
        for name, msg in failed_skills:
            print(f"  {name}: {msg}")
    print(f"\nOutput: {DIST_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
