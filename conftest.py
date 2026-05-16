"""
Root conftest.py
Applies project-wide pytest settings. Prevent bytecode generation.
AI-specific fixtures live in ai/tests/; UI/API fixtures in automation-project/conftest.py.
"""
import sys
sys.dont_write_bytecode = True
