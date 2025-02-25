import argparse
import json
import typing as t

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from .. import (
    ai,
    bootstrap,
)

TUPLE = tuple()
SYSTEM_PROMPT = (
    "Return result as RAW json string, without any markup"
    ' where requested items are array located in top-level key "result".'
    " If there is no suitable option return empty JSON object."
)


async def main(b: bootstrap.Bootstrap, args: argparse.Namespace) -> None:
    b.log.info("Matching: %s", args)

    wb: openpyxl.workbook.Workbook = openpyxl.load_workbook(
        args.input_file,
        read_only=True,
    )

    with open(args.output_file, "w") as output:
        try:
            await _main(b, int(args.limit), wb, ai.Repo(b), output)
        finally:
            wb.close()


async def _main(
    b: bootstrap.Bootstrap,
    limit: int,
    wb: openpyxl.workbook.Workbook,
    openai: ai.Repo,
    output_file: t.IO[str],
) -> None:
    original: Worksheet = wb["Original"]
    original_rows = {}
    for row in original:
        if len(row) == 0:
            continue

        row_0: openpyxl.cell.Cell = row[0]
        if not row_0:
            continue

        report_name = row_0.value.strip()
        reports = original_rows.get(report_name, [])
        reports.append(row)
        original_rows[report_name] = reports

    if "event" in original_rows:
        del original_rows["event"]

    keys: t.Iterable = original_rows.keys()
    original_reports_formatted = ", ".join(keys)
    b.log.debug("Collected originals (%d): %s", len(keys), original_reports_formatted)

    watched: Worksheet = wb["Watched"]
    for row in watched:
        for num, cell in enumerate(row):
            if not cell.value or num != 0:
                continue

            value = cell.value.strip().removeprefix("- ")
            if value in ("Reports", "No Numbers", "Assets"):
                continue

            prompt = (
                f"There is list of reports: {original_reports_formatted}."
                f" Which report from the list is meant by '{value}'?"
            )
            resp, result = await openai.complete(prompt, SYSTEM_PROMPT)
            b.log.info("OpenAI: %s -> %s", prompt, resp)

            result = result.removeprefix("```json").removesuffix("```").strip()

            found = json.loads(result).get("result", TUPLE)
            b.log.info("%s: %s", value, found)

            if not found:
                found = TUPLE

            output_file.write(f'"{value}"\t"{",".join(found)}"\n')

            limit -= 1
            if limit == 0:
                return
