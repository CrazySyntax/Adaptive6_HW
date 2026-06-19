"""Renders the per-dimension percentage breakdown to standard output.

This is the output stage of the pipeline: it takes the percentages produced by
the parser/aggregator and prints each dimension as its own titled block, values
sorted from largest to smallest, each percentage to two decimal places. Blocks
are separated by a blank line.

Example::

    Country:
    ========
    United States 35.10%
    United Kingdom 27.55%

    OS:
    ===
    Windows 64.36%
    ...
"""
from src.dimensions.enums import DimensionName


def display(results: dict[DimensionName, dict[str | None, float]]) -> None:
    """Print ``results`` as percentage breakdowns, one block per dimension.

    Each dimension is printed under its header (e.g. ``Country:``) with its
    values ordered by percentage descending. The input is assumed to already
    hold percentages; ordering is enforced here so the output is correct even
    if the mapping arrives unsorted. A ``None`` value (an extractor that could
    not resolve the dimension) is shown as ``Unknown``.
    """
    blocks: list[str] = []
    for dimension_name, value_percentages in results.items():
        header = f"{dimension_name.label}:"
        lines = [header, "=" * len(header)]
        ranked = sorted(value_percentages.items(), key=lambda item: item[1], reverse=True)
        for value, percentage in ranked:
            label = "Unknown" if value is None else value
            lines.append(f"{label} {percentage:.2f}%")
        blocks.append("\n".join(lines))
    print("\n\n".join(blocks))
