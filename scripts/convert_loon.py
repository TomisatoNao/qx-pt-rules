from __future__ import annotations

import ipaddress
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
RULES = ROOT / "rules"

ITEM_RE = re.compile(r"-\s*['\"]([^'\"]+)['\"]")

# Extra domains that should always go direct
EXTRA_DIRECT_DOMAINS: list[str] = [
    "DOMAIN-SUFFIX,220206.xyz",
    "DOMAIN-SUFFIX,833000.xyz",
    "DOMAIN-SUFFIX,2019102.xyz",
    "DOMAIN-SUFFIX,tgtodrive.top",
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


def to_loon_rule(value: str) -> str | None:
    """Convert a Clash/Mihomo payload entry to a Loon rule line (no policy)."""
    value = value.strip()

    if value.startswith("+."):
        return f"DOMAIN-SUFFIX,{value[2:]}"

    if value.startswith("."):
        return f"DOMAIN-SUFFIX,{value[1:]}"

    try:
        ipaddress.ip_network(value, strict=False)
    except ValueError:
        pass
    else:
        rule_type = "IP6-CIDR" if ":" in value else "IP-CIDR"
        return f"{rule_type},{value},no-resolve"

    # Skip URL-REGEX (not supported in Loon)
    if "/" in value:
        return None

    return f"DOMAIN,{value}"


def write_loon_list(source_name: str, output_name: str, desc: str) -> None:
    source_path = SOURCE / source_name
    output_path = RULES / output_name
    items = parse_payload(source_path)
    rules = [r for item in items if (r := to_loon_rule(item)) is not None]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(
            [
                f"# NAME: {output_name}",
                f"# DESC: {desc}",
                f"# TOTAL: {len(rules)}",
                "",
                *rules,
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    write_loon_list("ptmrs.yaml", "PT-Loon-Direct.list", "PT sites — subscribe with DIRECT policy")
    write_loon_list("ptpro.yaml", "PT-Loon-Proxy.list", "PT sites — subscribe with proxy policy")

    # Append extra direct domains
    direct_path = RULES / "PT-Loon-Direct.list"
    extra_str = "\n".join(EXTRA_DIRECT_DOMAINS)
    with direct_path.open("a", encoding="utf-8") as f:
        f.write(extra_str + "\n")

    print("Done → rules/PT-Loon-Direct.list, rules/PT-Loon-Proxy.list")


if __name__ == "__main__":
    main()
