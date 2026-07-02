from __future__ import annotations

import ipaddress
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
RULES = ROOT / "rules"

ITEM_RE = re.compile(r"-\s*['\"]([^'\"]+)['\"]")

# Additional domain rules that should always go direct
EXTRA_DIRECT_DOMAINS: list[str] = [
    "DOMAIN-SUFFIX,220206.xyz,DIRECT",
    "DOMAIN-SUFFIX,833000.xyz,DIRECT",
    "DOMAIN-SUFFIX,2019102.xyz,DIRECT",
    "DOMAIN-SUFFIX,tgtodrive.top,DIRECT",
]


def parse_payload(path: Path) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line == "payload:":
            continue

        for match in ITEM_RE.finditer(raw_line):
            value = match.group(1).strip()
            if value and value not in seen:
                seen.add(value)
                items.append(value)

    return items


def to_loon_rule(value: str, policy: str) -> str | None:
    """Convert a Clash/Mihomo payload entry to a Loon rule line.

    Returns None if the entry can't be converted (e.g. URL-REGEX).
    """
    value = value.strip()

    if value.startswith("+."):
        return f"DOMAIN-SUFFIX,{value[2:]},{policy}"

    if value.startswith("."):
        return f"DOMAIN-SUFFIX,{value[1:]},{policy}"

    try:
        ipaddress.ip_network(value, strict=False)
    except ValueError:
        pass
    else:
        rule_type = "IP6-CIDR" if ":" in value else "IP-CIDR"
        return f"{rule_type},{value},{policy},no-resolve"

    # Anything with a slash that isn't a valid IP network → skip (URL-REGEX,
    # not supported in Loon)
    if "/" in value:
        return None

    return f"DOMAIN,{value},{policy}"


def write_loon_rules(
    direct_source: str,
    proxy_source: str,
    output_name: str,
) -> None:
    direct_path = SOURCE / direct_source
    proxy_path = SOURCE / proxy_source
    output_path = RULES / output_name

    lines: list[str] = []

    # --- Header ---
    lines.append("# NAME: PT-Loon")
    lines.append("# DESC: PT sites routing rules for Loon")
    lines.append(
        "# NOTE: PROXY refers to your Loon proxy policy group. "
        "Rename if yours is different (e.g. 🚀 节点选择, Auto, etc.)."
    )
    lines.append("")

    # --- DIRECT rules (from ptmrs.yaml) ---
    lines.append("# ===== DIRECT =====")
    direct_items = parse_payload(direct_path)
    direct_count = 0
    for item in direct_items:
        rule = to_loon_rule(item, "DIRECT")
        if rule:
            lines.append(rule)
            direct_count += 1

    lines.append("")

    # --- PROXY rules (from ptpro.yaml) ---
    lines.append("# ===== PROXY =====")
    proxy_items = parse_payload(proxy_path)
    proxy_count = 0
    for item in proxy_items:
        rule = to_loon_rule(item, "PROXY")
        if rule:
            lines.append(rule)
            proxy_count += 1

    lines.append("")

    # --- Extra direct domains ---
    lines.append("# ===== EXTRA DIRECT DOMAINS =====")
    lines.extend(EXTRA_DIRECT_DOMAINS)

    lines.append("")

    # --- Footer ---
    lines.append(f"# TOTAL: {direct_count} direct + {proxy_count} proxy"
                 f" + {len(EXTRA_DIRECT_DOMAINS)} domain")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_loon_rules("ptmrs.yaml", "ptpro.yaml", "PT-Loon.list")
    print("Done → rules/PT-Loon.list")


if __name__ == "__main__":
    main()
