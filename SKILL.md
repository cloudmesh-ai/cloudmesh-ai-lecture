# Skill: Convert dates.md to dates-table.md

This skill describes the process of converting the hierarchical `dates.md` file into a flattened Markdown table `dates-table.md` for better visibility and summary.

## Input
- `docs/lecture/dates.md`: A hierarchical list of lectures, sections, and dates.

## Output
- `docs/lecture/dates-table.md`: A Markdown table containing the processed schedule.

## Transformation Process
1. **Parse**: Read each line of `dates.md`.
2. **Filter**: Identify lines that represent a specific lecture/item (usually starting with `- L.`, `- P.`, or `- W.`).
3. **Extract**:
    - **ID**: The lecture ID (e.g., `L.1.0`).
    - **Status**: The emoji indicating the status (🟢, 🟡, 🔴, ⚪).
    - **Topic**: The text within the hyperlink brackets.
    - **Link**: The URL within the hyperlink parentheses.
    - **Date**: The date wrapped in double asterisks (e.g., `**August 27, 2026**`).
4. **Format**: Arrange the extracted data into a Markdown table with the following columns:
    - `ID`
    - `Status`
    - `Topic`
    - `Date`
    - `Link`

## Execution Command
To perform this conversion, run the following script:
```bash
python3 bin/dates_to_table.py
```
