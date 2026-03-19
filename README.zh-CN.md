# Research Pipeline Automation

English version: [README.md](./README.md)

`research-pipeline-automation` 是一个通用的自动科研 skill，用来把一份科研方案文档转换成可执行的仓库工作流。

它面向的是“执行型科研自动化”，而不是简单的文本总结。典型使用方式是：你提供一份结构化的项目方案、benchmark 计划或方法设计文档，这个 skill 帮助 agent 在仓库里补齐或重构代码，让仓库能够完成数据下载、预处理、自动实验、结果记录，以及论文初稿生成。

这个 skill 是领域无关的，可以用于：

- 机器学习 benchmark 仓库
- 多模态研究项目
- 生物信号项目，例如 EMG、EEG、ECG、silent speech、BCI
- NLP、CV、语音、机器人科研仓库
- 以论文交付为目标、强调可复现和自动化的实验流水线

EMG 只是一个示例领域，不是这个 skill 的限制条件。

## 这个 Skill 能做什么

这个 skill 的目标是帮助 agent 完成以下工作：

1. 阅读方案文档并抽取：
   - 数据集
   - 预处理契约
   - 模型与 baseline
   - 数据划分协议
   - 指标
   - 实验矩阵
   - 最终交付要求

2. 把仓库收敛到一个统一契约：
   - 一个 processed 数据格式
   - 一个标签 / tokenizer 规范
   - 一个 experiment ledger
   - 一套主自动化入口

3. 搭建或修补实现：
   - 数据下载逻辑
   - 预处理脚本
   - baseline 训练 / 评估入口
   - 配置生成逻辑
   - 自动实验编排
   - watchdog 监控
   - 自愈式重试逻辑
   - 汇总结果
   - 论文初稿生成

4. 让整条链路可运行：
   - 可恢复下载
   - 可恢复实验
   - 后台执行
   - watchdog 自动续跑
   - 自动修复常见执行错误
   - GPU 感知参数调优
   - 显式实验追踪

5. 产出最终科研产物：
   - run 目录
   - 汇总表
   - experiment ledger
   - 论文或报告初稿

## 这个 Skill 不预设什么

这个 skill 不预设：

- 特定任务类型
- 特定深度学习框架
- 必须是 EMG 项目
- 仓库里已经有完整自动化
- 输入方案文档必须写得非常完整

它只要求：任务本身足够结构化，能够被转换成可执行的科研流水线。

## 目录结构

```text
research-pipeline-automation/
  SKILL.md
  README.md
  README.zh-CN.md
  INPUT_SPEC_TEMPLATE.md
  agents/
    openai.yaml
  references/
    spec-template.md
    automation-contract.md
    paper-draft-template.md
    platform-install.md
  scripts/
    install_skill.py
    install_codex.sh
    install_claude_code.sh
    install_openclaw.sh
```

## 各文件作用

### `SKILL.md`

这是给 agent 看的核心工作流文档，定义什么时候触发这个 skill、触发后应该怎么工作。

### `INPUT_SPEC_TEMPLATE.md`

这是给人写方案用的输入模板，用来准备一份适合喂给 skill 的项目说明文档。

### `references/`

这里放辅助说明文件：

- `spec-template.md`
  用来规范不完整的项目方案结构
- `automation-contract.md`
  规定自动化系统应该收敛到什么结构
- `paper-draft-template.md`
  规定论文初稿应该怎么从实验产物生成
- `platform-install.md`
  安装路径和平台说明

### `scripts/`

这里放跨平台安装脚本。

## 典型工作流

通常使用方式如下：

1. 先写一份项目方案 markdown 文档
2. 告诉 agent 使用 `$research-pipeline-automation`
3. 让 agent 先理解方案，再检查仓库，并补齐所需代码
4. 让自动化链路执行：
   - 下载数据
   - 预处理数据
   - 跑实验
   - 记录 setting 和结果
   - 生成论文初稿

一个实用的提示词可以写成：

```text
Use $research-pipeline-automation with docs/project_spec.md.
Build the end-to-end pipeline, set up dataset download and preprocessing, run the experiment matrix with watchdogs, record all settings and results, and draft a paper from the outputs.
```

## 输入文档应包含什么

这个 skill 最适合处理包含以下内容的方案文档：

- 项目目标
- 数据集和来源
- processed 数据格式要求
- 方法和 baseline
- 实验矩阵
- 指标
- CLI 约定
- 日志与产物要求
- Definition of Done

如果你还没有这样的文档，可以直接从下面这个模板开始：

- [INPUT_SPEC_TEMPLATE.md](./INPUT_SPEC_TEMPLATE.md)

## 预期输出

这个 skill 最终希望帮助仓库产出：

- `data/raw/...`
- `data/processed/...`
- `runs/...`
- `results/...`
- `experiment_ledger.json`
- `summary.csv`
- `summary.json` / `summary_test.json`
- 论文初稿，例如 markdown 或 LaTeX 骨架

## 这个 Skill 假设的自动化能力

这个 skill 默认认为科研自动化不能依赖一个交互式终端一直开着。

因此预期自动化能力包括：

- 可恢复的数据下载
- 确定性的预处理
- 后台实验编排
- watchdog 异常恢复
- 有边界的常见错误自修复与重试
- 基于 GPU 情况自动调整参数
- 跳过已完成 run
- 明确处理失败或不可行实验
- 机器可读的 experiment ledger

## 常见故障模式：训练进程还活着，但 GPU 长时间低占用

科研仓库里一个很常见的问题是：

- 训练进程还在
- GPU 利用率长时间接近 0
- CPU 还很忙
- 日志迟迟没有进入 epoch 和指标输出

这通常不是模型算不动，而是数据链路出了瓶颈。

常见原因：

- 压缩小文件太多
- 序列长度波动很大，而且样本很长
- 索引或长度统计在训练进程里临时构建
- 用固定样本数 batching 处理高变长序列任务
- `num_workers` 过高，超过当前机器的共享内存承受能力

相比直接提高 `batch_size`，更合理的做法通常是：

1. 先构建 split 级别的长度索引
2. 把索引缓存到磁盘
3. 使用按 frame / token / timestep 预算的动态 batching
4. 等索引阶段完成后再启动训练

这个处理思路现在已经属于本 skill 预期覆盖的自动化能力。

## 常见故障模式：DataLoader Bus Error / 共享内存不足

另一个很常见的问题是 DataLoader worker 过激，导致训练在数据加载阶段崩掉：

- 日志里出现 worker bus error
- 日志里出现 shared memory / shm 不足
- 提高 `num_workers` 之后更容易出错

这类问题更合理的修法通常是：

1. 降低 `num_workers`
2. 把修正后的 worker 数写回生成配置
3. 重试同一个 job
4. 如果 run 状态已经混乱，就执行干净重启并换新输出目录

这个问题也应该被视为 skill 的标准自愈场景之一。

更具体地说，自动化不应该拿同一个 worker 数无限重试。  
它应该主动把 worker 数往下调；如果当前 run 已经被污染，就直接在新的输出目录里干净重启。

## 常见故障模式：多次重启后出现状态错乱

另一个很常见的问题是自动化状态不一致：

- suite 主进程还在
- watchdog 还在
- 子训练进程也还在
- 但 experiment ledger 已经记录该阶段失败或停止
- GPU 利用率不再能真实反映进展

这种情况下，继续原地重试通常只会让状态更乱。

更合理的恢复方式是“干净重启”：

1. 停掉 suite
2. 停掉 watchdog 和相关监控
3. 停掉这个 run 目录对应的所有子训练进程
4. 删除不可信的 run 目录和旧日志
5. 保留仍然有效的持久缓存：
   - 原始下载数据
   - processed 数据
   - 长度索引等可复用缓存
6. 用新的输出目录重新启动整个流程

这个“干净重启”应该被视为自动化策略的一部分，而不是一次性的人工应急操作。

## 常见故障模式：结果文件已经被污染

还有一种情况也应该触发干净重启：

- `metrics.jsonl` 里出现重复的 `epoch 1 / step 1`
- 同一个 run 目录里前后记录互相矛盾
- `predictions_*.jsonl` 继续在旧失败结果后面追加

这说明这个 run 目录里的结果文件已经被污染，不适合继续沿用。

更合理的处理方式是：

1. 把这个 run 目录标记为不可信
2. 只保留上游可复用资产：
   - 原始数据
   - processed 数据
   - 长度索引和其他缓存
3. 删除旧 run 目录
4. 用新的输出目录重新从 epoch 1 开始

## 硬件感知与调参

这个 skill 期望 agent 根据机器资源做保守且可追踪的决策。

常见调参动作包括：

- 降低 `batch_size`
- 增加 `grad_accum_steps`
- 把文本类或 bookkeeping 任务移到 CPU
- 在硬件不足时收缩 sweep 宽度
- 保证核心实验先稳定，再扩展额外实验
- 当存在安全可行的补丁时，自动修复 OOM 或路径解析错误
- 遇到长期低 GPU 占用时，优先判断是否是数据链路问题，而不是直接判断为算力不足

这些调过的值都应该进入生成配置和 experiment ledger，而不是只体现在临时命令里。

## 安装

### Codex

```bash
cd path/to/research-pipeline-automation
./scripts/install_codex.sh --force
```

默认安装位置：

- `~/.codex/skills/research-pipeline-automation`

### Claude Code

```bash
./scripts/install_claude_code.sh --force
```

安装脚本默认目标：

- `~/.claude/skills/research-pipeline-automation`

### OpenClaw

```bash
./scripts/install_openclaw.sh --force
```

安装脚本默认目标：

- `~/.openclaw/skills/research-pipeline-automation`

### 自定义安装路径

如果本地环境的 skill 根目录不是默认值，可以显式指定：

```bash
./scripts/install_skill.py --platform codex --target-root <skill-root> --force
```

把 `codex` 换成 `claude-code` 或 `openclaw` 即可。

### 复制与软链接

默认安装模式是：

- `symlink`

如果你不想用软链接，可以改成：

```bash
./scripts/install_skill.py --platform codex --mode copy --force
```

## 验证

最小验证方式：

```bash
./scripts/install_skill.py --help
```

安装完成后，目标目录下应该至少有：

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`

## 如何写一份更适合自动化的方案文档

一份好的方案文档，应该让 agent 不需要从零猜实验设计。

最少应明确：

- 要做什么
- 要比较什么
- 要衡量什么
- 要保存什么产物
- 什么叫“完成”

实验矩阵、日志要求、产物要求越具体，自动化越可靠。
