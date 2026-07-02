from __future__ import annotations

import ipaddress
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
RULES = ROOT / "rules"


ITEM_RE = re.compile(r"-\s*['\"]([^'\"]+)['\"]")


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


def to_qx_rule(value: str, policy: str) -> str:
    value = value.strip()

    if value.startswith("+."):
        return f"HOST-SUFFIX,{value[2:]},{policy}"

    if value.startswith("."):
        return f"HOST-SUFFIX,{value[1:]},{policy}"

    try:
        ipaddress.ip_network(value, strict=False)
    except ValueError:
        pass
    else:
        rule_type = "IP6-CIDR" if ":" in value else "IP-CIDR"
        return f"{rule_type},{value},{policy},no-resolve"

    if "/" in value:
        return f"URL-REGEX,{value},{policy}"

    return f"HOST,{value},{policy}"


def dedup_rules(rules: list[str]) -> list[str]:
    """Remove rules covered by suffix containment.

    - A HOST rule is removed if a HOST-SUFFIX rule already covers that hostname.
    - A longer HOST-SUFFIX rule is removed if a shorter one already covers it.
    """
    # Collect all suffix values
    suffix_values: set[str] = set()
    for rule in rules:
        rtype = rule.split(",")[0]
        if rtype == "HOST-SUFFIX":
            suffix_values.add(rule.split(",")[1])

    result: list[str] = []
    for rule in rules:
        parts = rule.split(",")
        rtype, value = parts[0], parts[1]

        if rtype == "HOST":
            covered = any(value == sv or value.endswith("." + sv) for sv in suffix_values)
            if covered:
                continue

        if rtype == "HOST-SUFFIX":
            covered = any(
                value != sv and (value == sv or value.endswith("." + sv))
                for sv in suffix_values
            )
            if covered:
                continue

        result.append(rule)

    return result


def write_list(source_name: str, output_name: str, policy: str, desc: str) -> None:
    source_path = SOURCE / source_name
    output_path = RULES / output_name
    items = parse_payload(source_path)
    rules = [to_qx_rule(item, policy) for item in items]
    rules = dedup_rules(rules)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(
            [
                f"# NAME: {policy}",
                f"# DESC: {desc}",
                f"# SOURCE: {source_name}",
                f"# TOTAL: {len(rules)}",
                "",
                *rules,
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    write_list("ptmrs.yaml", "PT-Direct.list", "PT-Direct", "PT sites routed directly")
    write_list("ptpro.yaml", "PT-Proxy.list", "PT-Proxy", "PT sites routed through proxy")
    write_list("bybit-geo.yaml", "Bybit-Geo.list", "💞 地域限制", "Bybit exchange & geo-restriction bypass")


if __name__ == "__main__":
    main()
