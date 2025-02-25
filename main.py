#!/usr/bin/env python

import argparse
import asyncio

from src import (
    bootstrap,
    matcher,
)


async def main(b: bootstrap.Bootstrap):
    parser = argparse.ArgumentParser(description="POC")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    matcher_parser = subparsers.add_parser(
        "matcher",
        help="match data from one to another",
    )
    matcher_parser.set_defaults(func=matcher.main)
    matcher_parser.add_argument("input_file", help="Path to the input xslx file")
    matcher_parser.add_argument(
        "--limit",
        "-l",
        help="Hard limit of watched rows (0 for unlimited, optional)",
        default=1,
    )
    matcher_parser.add_argument("--output_file", "-o", default="./result.csv")

    args = parser.parse_args()
    if args.command:
        return await args.func(b, args)

    parser.print_help()


if __name__ == "__main__":
    import contextlib

    b = bootstrap.Bootstrap()
    b.log.info("Start")
    with contextlib.suppress(asyncio.CancelledError):
        asyncio.run(main(b), loop_factory=lambda: b.loop)

    b.log.info("Stop")
