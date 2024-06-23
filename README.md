## Interview Answer
- q1.py 使用注释在可能有缺陷的地方做了标记
- q1_clean.py 对q1.py中标记处的问题的重构版本
- q1_api.py 使用fastapi实现q1

## 可选加分项完成情况以及说明

- 使得代码可以正确运行 （推荐 FastAPI）
```shell
poetry install
docker run --name test-redis -d -p 6379:6379 redis:7
uvicorn q1_api:app --host 0.0.0.0
```

- 添加 test cases （推荐 pytest ）
```shell
pytest
```

- 添加 type hint （推荐使用 mypy 之类的工具做静态类型分析）
```shell
mypy
```

- 添加 logger
- 添加 typed error 和 更可读的 error message
- 按照 Clean Architecture 的形式拆分层次，并且加以适当的测试
- 添加项目依赖和配置 （requirements.txt or pyproject.toml)
- 使用 docker 打包项目，构建可运行镜像
```shell
docker-compose up --build
```
- 接入 Sqlite or Postgresql （ 纯SQL 或 ORM 都可以）
- 改写为 Async
- 添加 Authentication （ 推荐 JWT ）
- 添加 Authorization

    采用JWT和Bearer Token方式验证
    - q1/auth.py 

- （未实现）添加 GraphQL 接口 （推荐 Strawberry-GraphQL ）
- （未实现）改写为 Event Driven Architecture
- 实现 CQRS 模式

    假设add_score是一个大量投票加分需要QPS很高的场景，将add_score拆分为三个逻辑：

    - q1/service.py
        - add_score      数据写到redis的列表立即返回
        - update_score   收集列表数据汇总写入持久化并更新redis缓存
        - read_score     读取redis缓存
    - q1_scheduler.py  工作进程，在后端更新update_score

