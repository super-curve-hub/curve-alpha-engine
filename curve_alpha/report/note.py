import pandas as pd

def make_top20_markdown(ranking: pd.DataFrame) -> str:
    top = ranking.head(20).copy()
    lines = ["# Curve Alpha Top20", ""]
    for i, row in top.iterrows():
        lines.append(
            f"{i+1}. {row['ticker']} - {row.get('name','')} | "
            f"Score {row['curve_alpha_score']} | {row['rating']}"
        )
    lines.append("")
    lines.append("## Factor Summary")
    lines.append("")
    for _, row in top.head(10).iterrows():
        lines.append(
            f"- {row['ticker']}: Quality {row.get('quality_score', 50):.1f}, "
            f"Value {row.get('value_score', 50):.1f}, "
            f"Momentum {row.get('momentum_score', 50):.1f}, "
            f"Macro {row.get('macro_score', 50):.1f}, "
            f"Theme {row.get('theme_score', 50):.1f}"
        )
    return "\n".join(lines)
