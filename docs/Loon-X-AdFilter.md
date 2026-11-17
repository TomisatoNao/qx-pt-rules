# Loon X 信息流过滤（实验版）

这是实验原型，尚未在维护者或用户的 X 官方 App 上实测。能否工作取决于 App 能否接受 Loon 的 HTTPS 解密、实际接口和响应格式。不能保证安装后生效。

## 安装

在 Loon 的“插件”管理中通过 URL 添加以下地址；不要作为完整配置导入：

```text
https://raw.githubusercontent.com/TomisatoNao/qx-pt-rules/main/plugins/Loon/X-AdFilter.plugin
```

插件会自动引用同仓库的 `scripts/x-ad-filter.js`，不需要单独安装 JS。需要 Loon 3.5.1(983) 或更新版本，已开启 MitM，并在 iOS 中安装、完全信任 Loon 证书。只下载此仓库插件不会改动现有 PT 分流或节点。

## 范围和限制

- 仅匹配首页、搜索、推文详情、用户时间线和列表的指定 GraphQL 操作。
- 仅从 `entries` / `items` 数组移除有非空 `promotedMetadata` 标记或 `promoted-tweet-` 条目 ID 的项目。
- 普通推文、游标、无广告响应、错误 JSON、非 200 状态以及未识别结构保持原样。
- 不屏蔽 `abs.twitter.com`、`abs.twimg.com` 或图片视频域名，不修改节点和分流。
- 没有联网回传、Cookie 采集、持久化和定时任务。
- 不绕过证书固定，不支持所有接口、二进制响应、用户文字软广或所有新广告类型。

插件需要解密 `api.twitter.com`、`api.x.com`、`twitter.com`、`x.com`。如果官方 App 拒绝解密，可能导致连接失败。首页空白、连接错误或加载变慢时立即停用本插件；其他插件如也解密这些域名，需要分别检查。

## 判断是否执行

脚本日志：

```text
[X-AdFilter] JSON processed; promoted entries removed: N
```

`N > 0` 表示匹配并删除了标记条目，不代表全部广告都已过滤。没有日志也不能直接认定是证书固定：也可能没有匹配接口、脚本下载失败或其他重写优先处理。

需要继续适配时，请提供脚本日志或脱敏接口样本；不要公开 Cookie、Authorization、令牌、证书私钥或完整个人时间线。

## 验证

```sh
node tests/x-ad-filter.test.cjs
```

测试使用构造的模拟 JSON，涵盖推广标记、模块条目、分页游标、无改动响应、嵌套引用、错误响应、请求范围和处理预算。通过这些测试不代表已通过 X 官方 App 的实时验证。

## 文档

- [Loon 插件](https://nsloon.app/docs/Plugin/)
- [Loon 脚本配置](https://nsloon.app/docs/Script/script_v2/)
- [Loon 脚本 API](https://nsloon.app/docs/Script/script_api/)
