"""Command-line entry point for researchmap synchronization."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .client import DEFAULT_TIMEOUT_SECONDS, ResearchmapClient, ResearchmapError
from .config import ConfigError, load_config
from .sync import synchronize

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Synchronize this static site with the public researchmap API."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "site.toml",
        help="path to site configuration (default: site.toml)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "_auto_contents",
        help="generated content directory (default: _auto_contents)",
    )
    parser.add_argument(
        "--manual-content",
        type=Path,
        default=PROJECT_ROOT / "_contents",
        help="manual Markdown directory (default: _contents)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"HTTP timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS:g})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout <= 0:
        print("error: --timeout must be greater than zero", file=sys.stderr)
        return 2

    try:
        config = load_config(args.config)
        with ResearchmapClient(config.researchmap.base_url, timeout=args.timeout) as client:
            result = synchronize(
                config,
                client,
                args.output,
                manual_content_directory=args.manual_content,
            )
    except (ConfigError, ResearchmapError, OSError, ValueError) as error:
        print(f"researchmap sync failed: {error}", file=sys.stderr)
        return 1

    print(
        f"Generated {len(result.generated_files)} files in "
        f"{result.output_directory} at {result.last_updated}"
    )
    return 0
