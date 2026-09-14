# GitHub Sentinel

GitHub Sentinel 是面向开发者和项目管理人员的开源工具类 AI Agent。它按日或按周获取订阅仓库的最新动态，生成可读报告并投递到通知渠道。

当前版本是阶段一架构骨架，已提供领域模型、应用服务、端口适配器、内存仓储、HTTP API 和自动化测试。真实 GitHub API、数据库持久化、AI 模型以及外部通知将在后续阶段逐步接入。

## 架构

```text
HTTP / Scheduler
       ↓
Application Services
       ↓
Domain Entities and Rules
       ↓
Ports ← Infrastructure Adapters
```

领域层不依赖 Web 框架、数据库或外部 SDK，因此可独立测试。应用服务负责用例编排，基础设施层实现 GitHub、仓储、AI 和通知接口。

## 本地启动

需要 Python 3.12：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn github_sentinel.main:app --reload
```

访问：

- OpenAPI：<http://localhost:8000/docs>
- 存活检查：<http://localhost:8000/health/live>
- 就绪检查：<http://localhost:8000/health/ready>

如果设置了 `SENTINEL_API_KEY`，管理接口需要请求头 `X-API-Key`。健康检查保持公开。

## 测试与检查

```bash
pytest
ruff check .
mypy src
```

## 容器启动

```bash
cp .env.example .env
docker compose up --build
```

阶段一仍使用进程内存储；Compose 中的 PostgreSQL 和 Redis 是为下一阶段预留的基础设施。应用重启后，内存中的订阅和报告会被清空。

## 下一步

阶段二将实现 SQLAlchemy 持久化、Alembic 迁移、订阅唯一约束、分页查询和仓库可访问性校验。
