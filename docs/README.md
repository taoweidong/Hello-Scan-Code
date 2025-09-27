# Hello-Scan-Code 架构文档

本目录包含Hello-Scan-Code项目的完整架构文档，基于4+1视图模型进行组织。

## 文档结构

```
docs/
├── README.md                    # 本文档
├── architecture-overview.md    # 架构总览
├── views/                      # 4+1视图文档
│   ├── use-case-view.md        # 用例视图
│   ├── logical-view.md         # 逻辑视图
│   ├── process-view.md         # 进程视图
│   ├── development-view.md     # 开发视图
│   └── physical-view.md        # 物理视图
├── diagrams/                   # 架构图表
│   ├── use-case-diagrams/      # 用例图
│   ├── class-diagrams/         # 类图
│   ├── sequence-diagrams/      # 时序图
│   └── deployment-diagrams/    # 部署图
└── specifications/             # 技术规范
    ├── api-specification.md    # API规范
    ├── data-models.md          # 数据模型
    └── design-patterns.md      # 设计模式
```

## 4+1视图模型说明

### 1. 用例视图 (Use Case View)
- 描述系统功能需求
- 定义用户与系统的交互方式
- 识别主要的业务场景

### 2. 逻辑视图 (Logical View)
- 展示系统的静态结构
- 描述类与类之间的关系
- 体现设计模式的应用

### 3. 进程视图 (Process View)
- 描述系统的动态行为
- 展示并发处理机制
- 说明性能和可靠性设计

### 4. 开发视图 (Development View)
- 描述代码的组织结构
- 展示模块间的依赖关系
- 指导开发和维护工作

### 5. 物理视图 (Physical View)
- 描述系统的部署架构
- 说明软硬件环境配置
- 展示系统的可扩展性

## 快速导航

- [架构总览](./architecture-overview.md) - 开始了解整体架构
- [用例视图](./views/use-case-view.md) - 了解系统功能
- [逻辑视图](./views/logical-view.md) - 深入理解设计
- [技术规范](./specifications/) - 查看详细规范

## 文档维护

本文档集合与代码同步维护，任何架构变更都应同时更新相应的文档。