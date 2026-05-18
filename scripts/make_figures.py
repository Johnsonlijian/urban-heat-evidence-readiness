from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"

COLORS = {
    "actionable": "#2a9d8f",
    "proxy_limited": "#e9c46a",
    "evidence_blind": "#9b2226",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def city_label(city: str) -> str:
    return city.replace("_", " ")


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig1_evidence_stack() -> None:
    rows = [
        ["Overture footprints", "Feature enumeration and geometry audit", "Not a complete building census"],
        ["Sentinel attributes", "Vertical-form interpretation where populated", "Not a complete heat-risk descriptor"],
        ["ERA5 daily files", "Traceable heat-window inventory", "Not street-scale or indoor climate"],
        ["OSM cache", "Context where city assignment is valid", "Not a reliable 30-city predictor here"],
        ["GHS-BUILT-H", "City-window background height context", "Not building-level height truth"],
    ]
    fig, ax = plt.subplots(figsize=(12, 4.2))
    ax.axis("off")
    ax.text(
        0.0,
        0.98,
        "Evidence stack for heat-adaptation screening",
        fontsize=16,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.0,
        0.90,
        "Open-data layers are treated as separate evidentiary states before any screening claim is made.",
        fontsize=10.5,
        color="#444444",
        transform=ax.transAxes,
    )
    table = ax.table(
        cellText=rows,
        colLabels=["Layer", "Audited role", "Claim boundary"],
        colWidths=[0.24, 0.40, 0.36],
        cellLoc="left",
        bbox=[0.0, 0.05, 1.0, 0.68],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10.5)
    table.scale(1, 1.75)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#ffffff")
        if r == 0:
            cell.set_facecolor("#e9ecef")
            cell.set_text_props(fontweight="bold", color="#15324f")
        elif c == 1:
            cell.set_facecolor("#eef7ea")
        elif c == 2:
            cell.set_facecolor("#fff1ed")
        else:
            cell.set_facecolor("#ffffff")
    save_figure(fig, "Figure_1_evidence_stack_table")


def fig2_height_availability(a1_rows: list[dict[str, str]]) -> None:
    rows = sorted(a1_rows, key=lambda r: float(r["height_rate_in_sample"]), reverse=True)
    cities = [city_label(r["city"]) for r in rows]
    vals = [float(r["height_rate_in_sample"]) * 100 for r in rows]
    colors = [
        COLORS["evidence_blind"] if v < 0.1 else COLORS["actionable"] if v >= 10 else COLORS["proxy_limited"]
        for v in vals
    ]
    fig_h = max(8, len(rows) * 0.31)
    fig, ax = plt.subplots(figsize=(9.8, fig_h))
    y = list(range(len(rows)))
    ax.barh(y, vals, color=colors, edgecolor="none")
    ax.set_yticks(y)
    ax.set_yticklabels(cities, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("Overture height non-null rate (%)")
    ax.set_title("Sentinel building-height availability across 30 cities", loc="left", fontsize=14, fontweight="bold")
    ax.axvline(0.1, color=COLORS["evidence_blind"], linestyle=":", linewidth=1.2, label="0.1% evidence-blind boundary")
    ax.axvline(10, color="#264653", linestyle="--", linewidth=1.2, label="10% actionability threshold")
    sorted_vals = sorted(vals)
    median = (sorted_vals[14] + sorted_vals[15]) / 2
    ax.axvline(median, color="#005f73", linewidth=1.2, label=f"median {median:.2f}%")
    ax.set_xlim(0, 103)
    ax.grid(axis="x", color="#cccccc", alpha=0.35)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.055), ncol=3, fontsize=8, frameon=False)
    fig.subplots_adjust(bottom=0.10)
    save_figure(fig, "Figure_2_height_availability")


def fig3_mapped_vs_actionable(rows: list[dict[str, str]]) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 6.7))
    for typ in ["actionable", "proxy_limited", "evidence_blind"]:
        subset = [r for r in rows if r["typology"] == typ]
        xs = [float(r["features_total_ogr"]) for r in subset]
        ys = [max(float(r["height_rate_in_sample"]), 1e-5) for r in subset]
        ax.scatter(
            xs,
            ys,
            s=75,
            color=COLORS[typ],
            label=typ.replace("_", "-"),
            alpha=0.9,
            edgecolor="white",
            linewidth=0.6,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Overture feature count (log scale)")
    ax.set_ylabel("Overture height non-null rate (log scale)")
    ax.set_title("Mapped buildings do not guarantee attribute readiness", loc="left", fontsize=14, fontweight="bold")
    ax.grid(True, which="both", color="#cccccc", alpha=0.25)
    label_offsets = {
        "New_York": (-78, 14, "right"),
        "Los_Angeles": (-82, -26, "right"),
        "Sao_Paulo": (-30, 26, "right"),
        "Lagos": (14, 12, "left"),
        "Jakarta": (14, -12, "left"),
        "Delhi": (-28, -20, "right"),
        "Sydney": (-64, 12, "right"),
        "London": (16, 14, "left"),
    }
    for r in rows:
        if r["city"] in label_offsets:
            dx, dy, ha = label_offsets[r["city"]]
            ax.annotate(
                city_label(r["city"]),
                (float(r["features_total_ogr"]), max(float(r["height_rate_in_sample"]), 1e-5)),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=8.2,
                ha=ha,
                arrowprops={"arrowstyle": "-", "color": "#777777", "lw": 0.9},
                bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#dddddd", "alpha": 0.92},
                zorder=5,
            )
    ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    fig.subplots_adjust(bottom=0.18)
    save_figure(fig, "Figure_3_mapped_vs_attribute_readiness")


def fig4_typology_matrix(rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda r: (r["typology"] != "actionable", r["typology"] != "proxy_limited", -float(r["height_rate_in_sample"])))
    body = []
    for r in ordered:
        body.append(
            [
                city_label(r["city"]),
                f"{int(float(r['features_total_ogr'])):,}",
                str(int(float(r["era5_days"]))),
                f"{float(r['height_rate_in_sample']) * 100:.3g}",
                r["typology"].replace("_", "-"),
            ]
        )
    cols = ["City", "Features", "ERA5 days", "Height (%)", "State"]
    fig, ax = plt.subplots(figsize=(12, 9.2))
    ax.axis("off")
    ax.set_title("Typology matrix for heat-adaptation screening", loc="left", fontsize=16, fontweight="bold", pad=12)
    table = ax.table(
        cellText=body,
        colLabels=cols,
        colWidths=[0.24, 0.18, 0.14, 0.14, 0.20],
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.2)
    table.scale(1, 1.13)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#ffffff")
        if r == 0:
            cell.set_facecolor("#e9ecef")
            cell.set_text_props(fontweight="bold", color="#15324f")
        elif c == 4:
            state = body[r - 1][4] if r > 0 else ""
            if state == "actionable":
                cell.set_facecolor(COLORS["actionable"])
            elif state == "proxy-limited":
                cell.set_facecolor(COLORS["proxy_limited"])
            else:
                cell.set_facecolor(COLORS["evidence_blind"])
                cell.set_text_props(color="white", fontweight="bold")
            if state != "evidence-blind":
                cell.set_text_props(color="black", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#f8f9fa")
    ax.text(
        0.0,
        -0.03,
        "Counts under current rules: actionable=4, proxy-limited=19, evidence-blind=7.",
        fontsize=9,
        transform=ax.transAxes,
        color="#444444",
    )
    save_figure(fig, "Figure_4_typology_matrix_table")


def main() -> None:
    a1_rows = read_csv(DATA / "A1_overture_completeness_public.csv")
    readiness_rows = read_csv(DATA / "evidence_readiness_scores.csv")
    fig1_evidence_stack()
    fig2_height_availability(a1_rows)
    fig3_mapped_vs_actionable(readiness_rows)
    fig4_typology_matrix(readiness_rows)
    print(f"Wrote figures to {FIGURES}")


if __name__ == "__main__":
    main()

