
import csv
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
COMPARISON = RESULTS / "comparison.csv"
RECOMMENDATIONS = RESULTS / "architecture_recommendations.csv"
OUTPUT = RESULTS / "project_summary.md"


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def main():
    comparison = read_csv(COMPARISON)
    recommendations = read_csv(RECOMMENDATIONS)

    if not comparison or not recommendations:
        raise ValueError("Input CSV files must contain data rows.")

    recommendation_by_width = {
        int(row["width"]): row for row in recommendations
    }

    lines = [
        "# AutoAccel Project Summary",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Project objective",
        "",
        "Evaluate conventional and Karatsuba multiplier architectures "
        "using RTL simulation, synthesis-based generic logic-cell "
        "comparison, and formal verification.",
        "",
        "## Synthesis comparison and recommendations",
        "",
        "| Width | Conventional cells | Karatsuba cells | Recommended architecture | Cell-count reduction |",
        "|---:|---:|---:|---|---:|",
    ]

    for row in sorted(comparison, key=lambda item: int(item["width"])):
        width = int(row["width"])
        recommendation = recommendation_by_width.get(width)

        if recommendation is None:
            raise ValueError(
                f"No recommendation found for width {width}"
            )

        lines.append(
            f"| {width} | "
            f"{int(row['conventional_cells']):,} | "
            f"{int(row['karatsuba_cells']):,} | "
            f"{recommendation['recommended_architecture']} | "
            f"{recommendation['cell_count_reduction_percent']}% |"
        )

    lines.extend([
        "",
        "## Verification status",
        "",
        "- RTL simulations: previously reported as passing at tested configurations.",
        "- Formal equivalence: 8-bit proof passed.",
        "- 16-bit formal equivalence: unresolved; direct SAT proof did not complete.",
        "- Selector unit tests: 4 tests passed in the latest reported run.",
        "",
        "## Interpretation and limitations",
        "",
        "Recommendations minimize the generic logic-cell count reported by "
        "the current synthesis flow. These counts are not physical silicon "
        "area measurements and do not establish power consumption or timing.",
        "",
        "The recommendations apply to the tested operand widths and current "
        "RTL and synthesis configuration. Further verification and "
        "technology-specific implementation are needed before making broader "
        "hardware performance claims.",
        "",
    ])

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Project summary generated: {OUTPUT}")


if __name__ == "__main__":
    main()
