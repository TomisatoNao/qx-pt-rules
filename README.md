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

导入两个订阅，分别选择对应策略即可：

```ini
# 直连 — 订阅时策略选 DIRECT
https://raw.githubusercontent.com/TomisatoNao/qx-pt-rules/main/rules/PT-Loon-Direct.list

# 代理 — 订阅时策略选你的代理组（如 🚀 节点选择）
https://raw.githubusercontent.com/TomisatoNao/qx-pt-rules/main/rules/PT-Loon-Proxy.list
```

规则本身不带策略，策略在 Loon 客户端订阅时手动指定。

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
