# Quantumult X PT Rules

Custom PT routing rules for Quantumult X.

## Files

- `rules/PT-Direct.list`: PT domains that should use `direct`.
- `rules/PT-Proxy.list`: PT domains that should use your proxy policy.
- `scripts/convert.py`: Converts Clash/Mihomo `payload:` YAML domain sets to Quantumult X `.list` files.

## Quantumult X

Add these lines to `[filter_remote]` after publishing this repo:

```ini
https://raw.githubusercontent.com/TomisatoNao/qx-pt-rules/main/rules/PT-Direct.list, tag=PT-Direct, force-policy=direct, update-interval=86400, opt-parser=true, enabled=true
https://raw.githubusercontent.com/TomisatoNao/qx-pt-rules/main/rules/PT-Proxy.list, tag=PT-Proxy, force-policy=PROXY, update-interval=86400, opt-parser=true, enabled=true
```

Replace `PROXY` with the real Quantumult X policy group name if yours is different.

## Loon

Import the combined rule file:

```ini
https://raw.githubusercontent.com/TomisatoNao/qx-pt-rules/main/rules/PT-Loon.list
```

Rules use Loon's built-in `DIRECT` policy and the `PROXY` policy group for proxy traffic. If your proxy group has a different name (e.g. `🚀 节点选择`, `Auto`), replace `PROXY` in the `.list` file before importing, or use Loon's rule-subscription rename feature.

## Convert

### Quantumult X

```bash
python scripts/convert.py
```

### Loon

```bash
python scripts/convert_loon.py
```

Put the source YAML files in `source/`:

```text
source/ptmrs.yaml
source/ptpro.yaml
```

Then run:

```bash
python scripts/convert.py
```
