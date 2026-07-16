"""Smoke tests: structure + config integrity. Run: python -m pytest -q"""
import json, os, glob
ROOT = os.path.dirname(os.path.dirname(__file__))

def test_settings_valid():
    json.load(open(os.path.join(ROOT, ".claude/settings.json")))

def test_mcp_valid():
    json.load(open(os.path.join(ROOT, ".mcp.json")))

def test_all_skills_have_frontmatter():
    skills = glob.glob(os.path.join(ROOT, ".claude/skills/*/SKILL.md"))
    assert len(skills) >= 18
    for s in skills:
        head = open(s).read().splitlines()
        assert head[0] == "---" and "name:" in "\n".join(head[:6])
