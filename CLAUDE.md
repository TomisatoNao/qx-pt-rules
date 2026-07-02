# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Quantumult X and Loon routing rules for Private Tracker (PT) sites. The repo maps PT domain sets to platform-specific `.list` files so users can route tracker traffic through `direct` or proxy policies.

## How rules are generated

Source data lives in `source/` as Clash/Mihomo `payload:` YAML files:

- `source/ptmrs.yaml` → sites reachable directly (the majority)
- `source/ptpro.yaml` → sites requiring a proxy

### Quantumult X

```bash
python scripts/convert.py
```

Outputs two files: `rules/PT-Direct.list` and `rules/PT-Proxy.list`.

### Loon

```bash
python scripts/convert_loon.py
```

Outputs a single combined file: `rules/PT-Loon.list`. Uses Loon's built-in `DIRECT` policy and the standard `PROXY` proxy group name. Also inserts extra `IP-CIDR` rules for the `28.0.9.0/24` block (resolved from `220206.xyz` / emby / tgtodrive domains) to force direct routing at the IP level.

## Conversion mapping

Both scripts are pure stdlib Python — no dependencies. They parse YAML payload entries and map them to platform rule types:

| Clash/Mihomo format | Quantumult X rule | Loon rule |
|---|---|---|
| `+.domain.com` / `.domain.com` | `HOST-SUFFIX,domain.com,POLICY` | `DOMAIN-SUFFIX,domain.com,POLICY` |
| Bare hostname | `HOST,hostname,POLICY` | `DOMAIN,hostname,POLICY` |
| IP CIDR | `IP-CIDR,…` / `IP6-CIDR,…` with `no-resolve` | same |
| Value with `/` (regex) | `URL-REGEX,…` | skipped (Loon has no equivalent) |
