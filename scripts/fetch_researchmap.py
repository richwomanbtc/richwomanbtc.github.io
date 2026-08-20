#!/usr/bin/env python3
"""Backward-compatible wrapper for the researchmap sync CLI."""

from researchmap_site.cli import main

raise SystemExit(main())
