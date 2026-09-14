# GitHub Sentinel API 接口文档

## 变更概览

新增版本化的订阅管理、手动同步、报告管理和健康检查 HTTP API。当前接口版本为 `v1`。

## 鉴权与通用约定

- 管理接口前缀：`/api/v1`。
- 设置 `SENTINEL_API_KEY` 后，管理接口必须携带 `X-API-Key` 请求头。
- 健康检查不要求鉴权。
- 请求和响应使用 JSON，时间使用带时区的 ISO 8601 格式。
- 资源 ID 使用 UUID。
- `repository` 使用 `owner/name` 格式。

## 接口列表

### 创建订阅

- 方法与路径：`POST /api/v1/subscriptions`
- 变更类型：新增
- 兼容性：兼容

#### 请求参数

- `repository`：必填，GitHub 仓库全名。
- `schedule_type`：`daily` 或 `weekly`，默认 `daily`。
- `timezone`：IANA 时区，默认 `Asia/Shanghai`。
- `event_types`：至少一项，可选 `release`、`pull_request`、`issue`、`commit`。
- `notification_channels`：通知目标字符串列表。

#### 响应字段

返回订阅 ID、仓库、周期、时区、事件类型、通知目标、启用状态、同步时间及创建更新时间。

#### 错误码

- `401`：API Key 无效。
- `422`：请求格式或业务字段校验失败。

### 查询订阅列表

- 方法与路径：`GET /api/v1/subscriptions`
- 变更类型：新增
- 兼容性：兼容

返回订阅对象数组。阶段一暂不分页，持久化阶段将增加分页参数。

### 查询单个订阅

- 方法与路径：`GET /api/v1/subscriptions/{id}`
- 变更类型：新增
- 兼容性：兼容

- `404`：订阅不存在。

### 修改订阅

- 方法与路径：`PATCH /api/v1/subscriptions/{id}`
- 变更类型：新增
- 兼容性：兼容

允许修改周期、时区、事件类型、通知目标和启用状态，不允许通过该接口改变仓库身份。

### 删除订阅

- 方法与路径：`DELETE /api/v1/subscriptions/{id}`
- 变更类型：新增
- 兼容性：兼容

成功返回 `204`；订阅不存在返回 `404`。

### 手动同步订阅

- 方法与路径：`POST /api/v1/subscriptions/{id}/sync`
- 变更类型：新增
- 兼容性：兼容

返回获取事件数、新增事件数、报告 ID 和投递数。阶段一使用无网络 GitHub 适配器，因此默认返回零事件；测试可以替换为假客户端。

### 手动生成报告

- 方法与路径：`POST /api/v1/subscriptions/{id}/reports`
- 变更类型：新增
- 兼容性：兼容

请求包含 `period_start` 和 `period_end`。系统基于该时间段内已保存的事件生成报告。

### 查询报告列表

- 方法与路径：`GET /api/v1/reports`
- 变更类型：新增
- 兼容性：兼容

阶段一暂不分页，持久化阶段将增加订阅、状态和时间范围筛选。

### 查询单个报告

- 方法与路径：`GET /api/v1/reports/{id}`
- 变更类型：新增
- 兼容性：兼容

- `404`：报告不存在。

### 健康检查

- 方法与路径：`GET /health/live`、`GET /health/ready`
- 变更类型：新增
- 兼容性：兼容

存活检查表示进程可响应；阶段一就绪检查表示应用完成初始化。接入数据库和 Redis 后，就绪检查将增加依赖状态判断。

## 迁移或废弃说明

这是首个 API 版本，无迁移和废弃项。未来不兼容变更应新增 API 版本；分页等兼容性参数可在 `v1` 中扩展。

## 变更记录

| 日期 | 变更内容 |
| --- | --- |
| 2026-09-14 | 创建 GitHub Sentinel v1 API 接口文档。 |
