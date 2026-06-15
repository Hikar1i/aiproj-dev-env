## 原始提问:

codex可以极大程度上提升我的编程开发效率, 但是每次我新开一个项目或者新接手一个已有项目时, 我总会花一些时间去完成以下事情:
1.创建一些不被git追踪, 但我本地AI开发过程中所需要的目录, 比如我会创建一个.dev目录用于存放一些测试的代码, 开发的中间产物, 再创建一个.docs目录用于存放AI生成的需求文档, 设计文档, plan计划文档, 测试文档等, 再创建一个.refercens目录用于存放我人为, 手动存储的一些用于AI参考的文档或素材, 以及.bak目录用于存放一些需要备份的内容
2.每次我都需要重复向AI说明, 每个目录的作用, 并且告知Agent生成的什么内容存放到哪个目录下, 比如我会向AI这么说:"...所有的需求文档, 设计文档, plan计划文档都存放至`.docs`目录下的合适的子目录内, 并且今后追加的内容都要遵守该规定..."
3.创建.gitignore文件, 并根据不同的项目类型或不同的编程语言填充合适的忽略文件类型, 并确保以上目录不被记录在.gitignore中 (很多AI coding agent都不能直接读取.gitignore忽略目录下的文件和目录, 请确认codex是否也如此)

我应该通过怎么样的方式, 才能达到按照上述描述快速初始化AI编程项目的目的, 我应该创建一个SKILL, 或者VSCODE插件还是在AGENTS.md中做约束, 或者还有什么其他好的办法, 请分析该问题并检索一下其他人是否也有类似需求, 他们又是如何解决的


## chatgpt回复:

最适合你的不是在 **Skill、VS Code 插件、AGENTS.md** 中三选一，而是采用下面这套分层组合：

> **一个幂等的项目初始化脚本/CLI 作为核心 + 一个 Codex Skill 作为调用入口 + 全局 AGENTS.md 保存长期规则 + 项目本地 AGENTS.override.md 保存个性化规则 + `.git/info/exclude` 管理本地忽略目录。**

推荐结构：

```text
确定性文件操作：        aiproj init 脚本/CLI
Codex 一键调用入口：    $project-bootstrap Skill
所有项目通用约定：      ~/.codex/AGENTS.md
当前项目本地约定：      <repo>/AGENTS.override.md
项目本地忽略规则：      <repo>/.git/info/exclude
项目语言忽略规则：      <repo>/.gitignore
```

**现阶段不建议开发 VS Code 插件。** 插件开发和维护成本明显更高，而且只能覆盖 VS Code，不能同时服务于 Codex CLI、Codex App、其他编辑器和普通终端。

---

# 一、Codex 能否读取 `.gitignore` 中的目录

需要区分三个概念。

## 1. Codex 并不会把 `.gitignore` 当作安全边界

在本地 CLI 或 IDE 的 workspace-write 模式下，Codex可以读取工作区文件。即使文件被 Git 忽略，只要 Codex 知道准确路径，仍然可以通过直接读取或 Shell 命令访问它。因此：

```text
.gitignore ≠ 禁止 Codex 读取
.gitignore ≠ 安全隔离
.gitignore 只表示 Git 默认不追踪
```

目前 Codex 社区仍有人要求增加类似 `.codexignore` 的真正访问排除机制，这说明 `.gitignore` 不能承担“禁止 AI 访问”的作用。不要因为某目录在 `.gitignore` 中，就在里面保存希望 Codex绝对不能读取的密钥或生产凭据。([OpenAI开发者][1])

## 2. 但 Codex 的文件搜索通常会忽略这些目录

Codex CLI/IDE 中的 `@文件搜索`、文件候选和部分基于 ripgrep 的自动发现，通常会遵守 `.gitignore`、全局 Git ignore 和 `.git/info/exclude`。因此，被忽略的文件可能出现以下现象：

```text
@ 输入文件名时搜不到
Codex 扫描项目结构时没有主动发现
但明确告诉它路径后仍然可以读取
```

这与你观察到的其他 Agent 行为基本一致。Codex GitHub 仓库里已经有人提出了与你几乎完全相同的场景：将测试脚本、临时函数和样例数据放进 `playground/`、`.local/`、`temp/` 等 Git 忽略目录后，`@` 文件搜索找不到，但明确提供路径或使用 Shell 仍然可以读取。([GitHub][2])

另外，目录名称以 `.` 开头时，即使没有被 Git 忽略，也可能不出现在部分 `@` 搜索候选中。因此 `.docs`、`.dev` 这类隐藏目录不能完全依赖 Codex 自动发现。([GitHub][3])

需要读取这些目录时，可以在 AGENTS.md 中规定：

```bash
rg --hidden --no-ignore "关键字" .docs .references .dev
```

或者直接告诉 Codex：

```text
请读取 .references/需求说明.pdf
```

## 3. Codex App 的工作树不会自动带上这些文件

这是最需要注意的一点。

Codex App 使用 Git worktree 或 Handoff 转移任务时，Git 忽略文件不会随着线程移动。因此，你本地 `.docs`、`.references`、`.dev` 中的内容可能在 Local 模式能访问，但切换到 Codex 管理的 worktree 后不存在。([OpenAI开发者][4])

所以你的工作流应区分：

| 使用方式                       | 本地忽略目录               |
| -------------------------- | -------------------- |
| Codex CLI 在当前目录运行          | 可以访问，但通常不会被搜索自动发现    |
| Codex IDE 在当前工作区运行         | 可以直接读取，但 `@` 搜索可能找不到 |
| Codex App Local 模式         | 基本与本地 CLI 相同         |
| Codex App managed worktree | 不会自动复制本地忽略文件         |
| Codex Web / 云端任务           | 本地未提交文件通常不存在         |

如果 `.references` 中的材料是任务必需输入，在 worktree 或云端运行前，需要显式复制、上传或通过初始化脚本同步。

---

# 二、为什么应使用 `.git/info/exclude`，而不是修改 `.gitignore`

你的目录具有以下性质：

* 仅供你个人本地使用；
* 不应提交；
* 不一定适合团队其他成员；
* 不希望在项目 `.gitignore` 中留下个人工作流规则。

这正是 `.git/info/exclude` 的设计用途。

Git 官方文档建议：

* 所有开发者都应使用的忽略规则放进项目 `.gitignore`；
* 只对当前本地仓库有效、不需要共享的规则放进 `.git/info/exclude`。([Git][5])

初始化脚本应向下面这个文件写入内容：

```text
<repo>/.git/info/exclude
```

例如：

```gitignore
# >>> aiproj local workspace
/.dev/
/.docs/
/.references/
/.bak/
/AGENTS.override.md
# <<< aiproj local workspace
```

这里建议把你写的 `.refercens` 修正为：

```text
.references
```

## 不建议使用全局 Git ignore

虽然可以这样配置：

```bash
git config --global core.excludesFile ~/.config/git/ignore
```

但不建议全局忽略 `.docs/`、`.dev/` 等名称，因为：

1. 某些项目可能真的有需要提交的 `.docs` 或 `.dev`；
2. 全局规则不容易在项目内察觉；
3. Codex 的文件搜索也可能继承全局 ignore，导致更多“文件明明存在但搜不到”的情况。([GitHub][6])

由初始化脚本逐仓库写入 `.git/info/exclude` 更安全。

---

# 三、AGENTS.md 应该怎样分层

Codex 官方支持全局和项目级 AGENTS.md，并且会在每次启动时构建一条指令链：

1. `~/.codex/AGENTS.override.md` 或 `~/.codex/AGENTS.md`
2. 项目根目录的 `AGENTS.override.md` 或 `AGENTS.md`
3. 当前子目录下更具体的 AGENTS 文件

越接近当前工作目录的规则优先级越高。Codex 默认会在开始任务前读取这些文件。([OpenAI开发者][7])

## 1. 全局 `~/.codex/AGENTS.md`

这里保存你所有项目都适用的规则，但不要放具体技术栈命令。

建议内容：

```markdown
# Personal development conventions

## Local AI workspace

When a repository contains the following directories, use them according to
these rules:

- `.dev/`: Disposable experiments, diagnostic scripts, temporary test code,
  generated intermediate artifacts, and one-off validation programs.
- `.docs/`: AI-generated requirements, designs, implementation plans, test
  plans, analysis reports, and other project documentation.
- `.references/`: User-provided reference documents and materials. Treat these
  files as read-only unless explicitly instructed otherwise.
- `.bak/`: Local backups. Never treat backup files as the current source of
  truth unless explicitly instructed.

Documentation placement:

- Requirements go under `.docs/requirements/`.
- Design documents go under `.docs/design/`.
- Plans go under `.docs/plans/`.
- Test documents go under `.docs/tests/`.
- Investigation notes go under `.docs/research/`.

Operational rules:

- Do not place production source code in these directories.
- Do not import runtime code from `.dev/`.
- Do not modify `.references/` without explicit permission.
- Do not use `.bak/` as implementation input unless explicitly requested.
- These directories may be Git-ignored. When searching them, use explicit
  paths or commands such as `rg --hidden --no-ignore`.
- Never assume Git-ignored files exist in another worktree or cloud
  environment.
```

这样你不需要每次再向 Codex 重复解释目录作用。

不过，全局规则最好写成：

```text
When a repository contains...
```

而不是：

```text
Every repository must always create...
```

否则 Codex 在一些你不想使用该结构的仓库中，也可能主动创建目录。

## 2. 项目本地 `AGENTS.override.md`

如果你不想修改项目已经提交的 `AGENTS.md`，初始化工具可以生成：

```text
<repo>/AGENTS.override.md
```

然后把它加入 `.git/info/exclude`。

Codex 会优先读取同级的 `AGENTS.override.md`，而不是同级 `AGENTS.md`。这非常适合保存：

* 你个人在该项目里的特殊约定；
* 本地启动命令；
* 临时数据库地址；
* 本地测试方法；
* 文档目录规则；
* Agent 可使用但不应提交的说明。([OpenAI开发者][7])

例如：

```markdown
# Local project instructions

## AI workspace

This repository uses the following local-only directories:

- `.dev/`: temporary scripts and experiments
- `.docs/`: generated project documentation
- `.references/`: manually supplied reference materials
- `.bak/`: local backups

All generated requirements, designs, implementation plans, investigation
reports, and test plans must be stored in an appropriate subdirectory under
`.docs/`.

Before creating a document, select one of:

- `.docs/requirements`
- `.docs/design`
- `.docs/plans`
- `.docs/tests`
- `.docs/research`

Treat `.references/` as read-only.

These directories are intentionally excluded through `.git/info/exclude`.
They may not appear in `@` file search. Access them by explicit path and use
`rg --hidden --no-ignore` when necessary.

## Detected project profile

- Project type: Spring Boot
- Build command: `mvn clean package`
- Test command: `mvn test`
- Main configuration directory: `src/main/resources`
```

这比修改团队共享的 `AGENTS.md` 更适合你的个人工作流。

---

# 四、为什么核心必须是初始化脚本，而不能只依靠 Skill

Skill 本质上仍然是让 Agent执行一套流程。创建目录、修改 ignore、合并 `.gitignore` 这些操作需要具备：

* 幂等性；
* 精确的文件修改；
* 冲突检测；
* 可重复执行；
* Dry Run；
* 不破坏已有内容；
* 跨项目一致性。

单纯写一段 Skill 指令，例如：

```text
创建这些目录，然后根据项目类型修改 .gitignore
```

仍然可能产生以下不确定性：

* 每次目录结构略有不同；
* 重复追加 ignore；
* 覆盖已有 AGENTS.md；
* 错误判断项目类型；
* 修改不应修改的 `.gitignore`；
* 忘记处理已有文件；
* Agent 在上下文较长时遗漏部分步骤。

Codex 官方对 Skill 的建议也是：大部分 Skill 可以只用说明，但需要确定性行为或外部工具时，应加入脚本。Skill 可以包含 `SKILL.md`、`scripts/`、`references/` 和 `assets/`。([OpenAI开发者][8])

所以建议采用：

```text
Skill 负责：
- 判断什么时候运行
- 收集少量参数
- 调用初始化脚本
- 检查结果并向你汇报

脚本负责：
- 创建目录
- 写入 .git/info/exclude
- 检测技术栈
- 生成 AGENTS.override.md
- 生成或合并 .gitignore
- 校验最终状态
```

---

# 五、推荐实现：`aiproj` 初始化工具

建议将工具命名为：

```text
aiproj
```

或者：

```text
codex-project-init
```

用 Python 编写即可，方便同时支持 Windows 11、Ubuntu 和 WSL。

期望使用方式：

```bash
aiproj init
```

也可以指定：

```bash
aiproj init --profile springboot
aiproj init --profile python
aiproj init --profile node
aiproj init --profile auto
```

查看但不修改：

```bash
aiproj init --dry-run
```

重新生成本地指令：

```bash
aiproj agents refresh
```

检查配置：

```bash
aiproj doctor
```

## 初始化流程

脚本应按以下顺序执行：

```text
1. 使用 git rev-parse --show-toplevel 定位仓库根目录
2. 检查目录名是否与已追踪目录冲突
3. 检测项目类型
4. 创建本地 AI 工作目录
5. 创建 .docs 子目录
6. 更新 .git/info/exclude
7. 生成或更新 AGENTS.override.md
8. 检查项目 .gitignore
9. 根据项目类型选择性补充语言忽略规则
10. 执行校验并输出报告
```

## 推荐目录

保留你现有的命名习惯即可：

```text
.dev/
├── scripts/
├── experiments/
├── fixtures/
├── output/
└── tmp/

.docs/
├── requirements/
├── design/
├── plans/
├── tests/
├── research/
├── decisions/
└── archive/

.references/
├── documents/
├── images/
├── examples/
└── vendor/

.bak/
├── code/
├── config/
├── database/
└── bootstrap/
```

其中 `.docs/decisions` 可以存放 ADR、重要设计决策和方案取舍。

## 必须进行冲突检查

初始化已有项目时不能直接创建或忽略目录。例如项目可能已经追踪了 `.docs`。

脚本需要先执行：

```bash
git ls-files .dev .docs .references .bak
```

如果发现已有追踪内容，应停止自动忽略并提示：

```text
.docs is already tracked by Git.
Suggested local directory: .ai-docs
```

或者统一改成冲突更小的根目录：

```text
.ai-workspace/
├── dev/
├── docs/
├── references/
└── backup/
```

实际上，从工具设计角度，我更推荐统一根目录：

```text
.ai/
├── dev/
├── docs/
├── references/
└── backup/
```

优点是：

* `.git/info/exclude` 只需一条 `/.ai/`；
* 避免多个顶级隐藏目录；
* 更容易迁移、备份和清理；
* Agent 只需记住一个入口；
* 将来可以加入 `.ai/config.toml`；
* 更容易同步到 Codex worktree。

但如果你已经习惯四个目录，继续使用也没有问题。

---

# 六、`.gitignore` 应如何自动生成

不要让 Agent 每次联网临时生成 `.gitignore`。

GitHub 官方维护了 Java、Python、Node 等项目的 `.gitignore` 模板，适合将所需模板固定放进初始化工具的 `assets/gitignore/` 中。([GitHub][9])

Skill 目录可以设计为：

```text
$HOME/.agents/skills/project-bootstrap/
├── SKILL.md
├── scripts/
│   └── bootstrap.py
├── assets/
│   ├── agents/
│   │   └── AGENTS.override.md.j2
│   └── gitignore/
│       ├── Java.gitignore
│       ├── Python.gitignore
│       ├── Node.gitignore
│       ├── VisualStudioCode.gitignore
│       └── JetBrains.gitignore
└── references/
    └── project-detection.md
```

Codex 目前会从用户级：

```text
$HOME/.agents/skills
```

发现个人 Skill。Skill 可以在 Codex CLI、IDE Extension 和 Codex App 中使用，并可以通过 `$skill-name` 显式调用。([OpenAI开发者][8])

## 合并 `.gitignore` 时不要简单逐行去重

因为 `.gitignore` 中存在顺序和否定规则，例如：

```gitignore
*
!important.txt
```

简单去重和排序可能改变语义。

应采用一个受管理区块：

```gitignore
# >>> aiproj generated: java
target/
*.class
*.jar
*.war
*.ear
# <<< aiproj generated: java
```

再次运行时，只替换这个区块，不改动用户已有内容。

推荐策略：

```text
新项目且无 .gitignore：
    直接根据检测到的技术栈创建

已有项目且存在 .gitignore：
    默认只分析并报告
    使用 --gitignore merge 时才追加受管理区块

已有受管理区块：
    更新区块内容

检测到复杂否定规则：
    不自动修改，只给出建议
```

同时确保这些个人目录只进入 `.git/info/exclude`，不要进入项目 `.gitignore`。

---

# 七、Skill 应该怎样设计

Skill 名称：

```yaml
name: project-bootstrap
```

触发说明应写得足够明确：

```yaml
---
name: project-bootstrap
description: Initialize or repair a local AI-assisted development workspace in
  a new or existing Git repository. Creates local documentation, experiment,
  reference, and backup directories; configures .git/info/exclude; generates
  AGENTS.override.md; and safely initializes language-specific .gitignore
  rules. Use when the user asks to initialize, bootstrap, standardize, or
  prepare a repository for Codex-assisted development.
---
```

核心指令可以保持很短：

```markdown
1. Locate the repository root.
2. Run `python scripts/bootstrap.py init --repo <root> --profile auto`.
3. Never manually reproduce the bootstrap operations unless the script fails.
4. Do not overwrite tracked AGENTS.md files.
5. Stop and report when a target local directory is already tracked.
6. After completion, run the bootstrap validation command.
7. Summarize created, modified, skipped, and conflicting files.
```

然后在 Codex 中运行：

```text
$project-bootstrap
```

或者：

```text
使用 $project-bootstrap 初始化当前项目，这是一个已有的 Spring Boot 项目。
```

Codex Skills 官方支持显式调用和基于描述的隐式调用；对于这种会修改多个文件的操作，建议以显式调用为主，避免 Codex在你只是讨论项目时误触发初始化。可以在 `agents/openai.yaml` 中关闭隐式调用。([OpenAI开发者][8])

---

# 八、是否需要做成 Codex Plugin

暂时不需要。

官方定位是：

* **Skill**：编写和保存可复用工作流；
* **Plugin**：将多个 Skill、MCP、应用集成和资源打包分发。([OpenAI开发者][8])

你的第一阶段只有一个个人初始化工作流，因此：

```text
个人使用：
$HOME/.agents/skills/project-bootstrap

团队内部复用：
Git 仓库中的 .agents/skills/project-bootstrap

需要给多人安装或包含多个 Skill：
再封装成 Codex Plugin
```

---

# 九、为什么不推荐优先开发 VS Code 插件

VS Code 插件只有在以下需求出现后才值得开发：

* 在命令面板提供“初始化 AI 项目”；
* 提供勾选目录和技术栈的图形界面；
* 显示项目初始化状态；
* 自动识别新打开的仓库；
* 在侧边栏展示 `.docs` 文档；
* 支持点击同步到 Codex worktree；
* 团队成员不愿意使用命令行。

而当前需求只需要：

```text
创建目录
写几个文本文件
识别项目类型
更新本地 Git 配置
```

这些都适合 CLI。并且 CLI 可以被：

* Codex Skill 调用；
* VS Code Task 调用；
* IDEA External Tool 调用；
* Shell Alias 调用；
* Windows Terminal 调用；
* WSL 调用；
* 将来的 VS Code 插件调用。

所以正确演进路线是：

```text
先写 CLI
    ↓
封装 Codex Skill
    ↓
稳定后再按需做 VS Code 插件
```

而不是把核心逻辑直接写死在插件中。

---

# 十、模板仓库、Cookiecutter 和 Copier 是否适合

## Cookiecutter

Cookiecutter 适合从模板创建全新项目，例如直接生成一个完整 Python 包或标准项目骨架。([GitHub][10])

它适合：

```text
从零创建新项目
```

但你的场景同时包括：

```text
接手已经存在的项目
```

对已有项目进行非破坏式合并、检测已有 AGENTS.md、更新 `.git/info/exclude`，Cookiecutter 不如定制 CLI 灵活。

## Copier

Copier 同样支持项目模板，并且比 Cookiecutter 更强调项目创建后的模板更新能力。([Copier][11])

如果你未来希望统一生成：

* Spring Boot 项目；
* Vue 项目；
* Python 服务；
* Docker Compose；
* CI 配置；
* AGENTS.md；
* 文档目录；
* 测试框架；

那么可以维护 Copier 模板。

但对你现在的需求，Copier 可以作为“新项目生成器”，不能完全替代“已有项目初始化器”。

推荐划分：

```text
aiproj init
    适用于所有已有或新项目

copier copy your-spring-template
    适用于从零创建标准 Spring Boot 项目
```

---

# 十一、Git Template 可以作为补充，但不能单独解决

Git 支持自定义初始化模板，并可以通过 `init.templateDir` 配置。模板内容会在 `git init` 时复制到新仓库的 `.git` 目录。([Git][12])

它可以预置：

```text
.git/info/exclude
.git/hooks/*
```

但存在限制：

* 只在 `git init` 或 clone 初始化阶段生效；
* 主要复制到 `.git` 内部；
* 不适合生成工作区中的 `.docs`、`.dev`；
* 不处理已有仓库；
* 不识别 Java、Python、Node 等项目类型；
* 不适合合并已有 AGENTS.md。

可以把它作为小优化，但不应作为核心方案。

---

# 十二、其他人是否也有类似需求

有，而且非常普遍。

## 1. AGENTS.md 已经成为通用模式

AGENTS.md 是一个面向 Coding Agent 的开放格式，用于保存项目级构建命令、测试方式、目录约定和编码规则。官方站点称其已经被大量开源项目采用。([Agents.md][13])

## 2. Codex 用户明确提出过“本地忽略目录无法 @ 搜索”

Codex issue 中有人明确描述：

* 将测试脚本放在 Git 忽略目录；
* 这些文件不应提交；
* 希望 Agent 在明确要求后仍能读取；
* 但 `@` 文件搜索只显示 Git 可见文件。

这与你的 `.dev`、`.docs`、`.references` 工作流高度相似。([GitHub][2])

## 3. 社区普遍采用“Agent 规则文件 + 项目模板/脚本”

常见组合包括：

```text
AGENTS.md / CLAUDE.md
+
Cookiecutter / Copier / 模板仓库
+
本地初始化脚本
+
.git/info/exclude
```

并且已经出现专门维护 AGENTS.md、工作流索引、ADR、当前状态、版本历史等文件的“Agent 项目操作层”模板。([Reddit][14])

## 4. 研究结果表明，规则文件应当保持精简

2026 年关于 AGENTS.md 的研究结果并不完全一致：

* 一项研究发现，自动生成或内容过多的 AGENTS.md 可能降低任务成功率，并增加超过 20% 的推理成本；
* 另一项研究发现，AGENTS.md 与更低的中位运行时间和更少输出 Token 相关。([arXiv][15])

这两个结果并不真正矛盾，它们共同说明：

> AGENTS.md 有价值，但不应变成长篇项目百科。它应只记录 Agent 无法从代码中可靠推断、且会直接影响执行正确性的规则。

你的目录职责、文档放置规则、测试命令和禁止事项适合写进去；完整框架教程、长篇业务背景则应放进 `.references` 或 `.docs`，让 Agent 按需读取。

近期也有研究专门将项目初始化信息抽取成可复用的 bootstrap contract，说明“把项目启动知识持久化，而不是每次在对话里重新探索”正在成为明确的工程方向。([arXiv][16])

---

# 十三、最终推荐方案

按优先级实施：

## 第一阶段：立即实施

创建：

```text
~/.codex/AGENTS.md
```

保存你的全局目录约定。

然后编写一个跨平台 Python 脚本：

```text
aiproj init
```

实现：

```text
创建目录
写 .git/info/exclude
生成 AGENTS.override.md
识别项目类型
安全处理 .gitignore
验证结果
```

## 第二阶段：接入 Codex

将脚本封装为用户级 Skill：

```text
~/.agents/skills/project-bootstrap/
```

今后进入项目后直接执行：

```text
$project-bootstrap
```

## 第三阶段：支持新项目模板

当你开始频繁新建同类型项目时，再维护：

```text
Spring Boot Copier 模板
Python Copier 模板
Vue/React Copier 模板
```

## 第四阶段：确有 UI 需求再开发插件

只有当 CLI 已经稳定，并且你确实需要 VS Code 命令面板、侧边栏或团队图形化安装时，再开发 VS Code 插件。插件只负责 UI，底层继续调用 `aiproj`，不要复制一套初始化逻辑。

最终使用体验应当是：

```bash
cd existing-project
aiproj init
```

或者直接在 Codex 中：

```text
$project-bootstrap
```

完成后得到：

```text
.dev/
.docs/
.references/
.bak/
AGENTS.override.md
.git/info/exclude 已更新
.gitignore 已按项目技术栈检查或补充
```

这种方案同时满足：**执行结果稳定、规则无需重复说明、不污染团队仓库、兼容已有项目、兼容 Codex CLI/IDE/App，并且未来可以平滑升级成插件或团队工具。**

[1]: https://developers.openai.com/codex/agent-approvals-security?utm_source=chatgpt.com "Agent approvals & security – Codex"
[2]: https://github.com/openai/codex/issues/2952?utm_source=chatgpt.com "Issue #2952 · openai/codex"
[3]: https://github.com/openai/codex/issues/2846?utm_source=chatgpt.com "Include dotfiles in @-file search suggestions · Issue #2846"
[4]: https://developers.openai.com/codex/app/worktrees?utm_source=chatgpt.com "Worktrees – Codex app"
[5]: https://git-scm.com/docs/gitignore?utm_source=chatgpt.com "gitignore Documentation"
[6]: https://github.com/openai/codex/issues/8616?utm_source=chatgpt.com "Codex CLI: file references report 'no matches' even for ..."
[7]: https://developers.openai.com/codex/guides/agents-md?utm_source=chatgpt.com "Custom instructions with AGENTS.md – Codex"
[8]: https://developers.openai.com/codex/skills?utm_source=chatgpt.com "Agent Skills – Codex"
[9]: https://github.com/github/gitignore?utm_source=chatgpt.com "A collection of useful .gitignore templates"
[10]: https://github.com/cookiecutter/cookiecutter?utm_source=chatgpt.com "cookiecutter/cookiecutter: A cross-platform command-line ..."
[11]: https://copier.readthedocs.io/en/stable/updating/?utm_source=chatgpt.com "Updating a project - copier - Read the Docs"
[12]: https://git-scm.com/docs/git-init?utm_source=chatgpt.com "Git - git-init Documentation"
[13]: https://agents.md/?utm_source=chatgpt.com "AGENTS.md"
[14]: https://www.reddit.com/r/LLMDevs/comments/1syrxx2/i_made_an_opensource_template_pack_for/?utm_source=chatgpt.com "I made an open-source template pack for coding-agent ..."
[15]: https://arxiv.org/abs/2602.11988?utm_source=chatgpt.com "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"
[16]: https://arxiv.org/abs/2605.15815?utm_source=chatgpt.com "BootstrapAgent: Distilling Repository Setup into Reusable Agent Knowledge"
