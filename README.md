# 函数测试用例自动生成工具

这是一个基于 `函数测试用例自动生成工具_设计方案.md` 实现的函数级测试用例生成 CLI。

用户可以提供函数源码、参数范围、规则文件或自然语言需求，工具会自动生成测试用例，并可选执行函数，输出 `expected / actual / pass` 测试结果。

## 支持模式

工具支持四种模式：

| 模式 | 命令值 | 主要用途 |
|---|---|---|
| 规则模式 | `rule` | 根据人工编写的测试规格生成测试用例 |
| 代码分析模式 | `auto` | 根据函数代码结构自动生成分支测试用例 |
| 大模型模式 | `llm` | 让大模型根据函数和需求生成测试规格 |
| 混合模式 | `hybrid` | 大模型生成规则草稿，人工确认后再生成用例 |

## 整体工作原理

工具采用“两阶段”设计：

```text
第一阶段：生成测试规格 spec
    ↓
第二阶段：根据 spec 确定性生成测试用例
```

其中，`spec` 是工具的核心中间格式，里面包含参数定义和测试规则。

大模型模式也不会直接生成最终测试结果。大模型只负责生成 `spec`，后续规则校验、测试用例生成、函数执行和结果比较都由本地程序完成。

这样可以减少大模型幻觉带来的影响，也方便复现和调试。

## 快速开始

规则模式生成并执行三角形测试：

```bash
python3 testcase_generator.py \
  --mode rule \
  --spec examples/triangle_spec.json \
  --out outputs/triangle_cases.csv
```

代码分析模式：

```bash
python3 testcase_generator.py \
  --mode auto \
  --call examples.triangle_impl:check_triangle \
  --params examples/triangle_params.json \
  --out outputs/triangle_auto_cases.md \
  --out-spec outputs/triangle_auto_spec.json
```

混合模式生成 Prompt：

```bash
python3 testcase_generator.py \
  --mode hybrid \
  --call examples.triangle_impl:check_triangle \
  --requirement examples/triangle_requirement.md \
  --out-prompt outputs/triangle_llm_prompt.md
```

LLM 模式需要配置 OpenAI 兼容环境变量：

```bash
# 可以直接编辑项目根目录下的 .env
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

然后运行：

```bash
python3 testcase_generator.py \
  --mode llm \
  --call examples.triangle_impl:check_triangle \
  --requirement examples/triangle_requirement.md \
  --out-spec outputs/triangle_llm_spec.json \
  --out outputs/triangle_llm_cases.json
```

也可以指定其他配置文件：

```bash
python3 testcase_generator.py \
  --env-file .env.local \
  --mode llm \
  --call examples.triangle_impl:check_triangle \
  --requirement examples/triangle_requirement.md \
  --out-spec outputs/triangle_llm_spec.json \
  --out outputs/triangle_llm_cases.json
```

## 各模式需要准备的文件

不同模式需要的输入文件不一样。

| 模式 | 必须准备 | 可选准备 | 说明 |
|---|---|---|---|
| `rule` | `spec.json` | 被测函数文件 | 按人工规则生成测试用例；如果 `spec` 中有 `target`，会自动执行函数 |
| `auto` | 被测函数文件 | `params.json` | 根据代码分支自动生成规则；`params.json` 用来限制参数范围 |
| `llm` | 被测函数文件、需求说明文件、`.env` | `params.json` | 调用大模型生成 `spec`，再生成测试用例 |
| `hybrid` | 被测函数文件、需求说明文件 | `.env`、人工保存的 `spec.json` | 先生成 Prompt，人工让大模型生成 `spec`，确认后再用 `rule` 模式 |

### rule 模式需要的文件

`rule` 模式至少需要：

```text
spec.json
```

示例：

```bash
python3 testcase_generator.py \
  --mode rule \
  --spec examples/triangle_spec.json \
  --out outputs/triangle_cases.csv
```

`spec.json` 里通常包含：

```json
{
  "function": "check_triangle",
  "target": "examples.triangle_impl:check_triangle",
  "params": {
    "d1": {
      "type": "int",
      "min": -1,
      "max": 10
    }
  },
  "rules": [
    {
      "id": "non_positive",
      "name": "边长小于等于 0",
      "when": "d1 <= 0",
      "expect": "non-triangle"
    }
  ]
}
```

其中：

- `params` 告诉工具参数有哪些、范围是多少；
- `rules` 告诉工具有哪些测试场景；
- `target` 告诉工具要执行哪个函数。

如果 `spec.json` 里没有 `target`，也可以在命令行用 `--call` 指定函数。

### auto 模式需要的文件

`auto` 模式必须需要：

```text
被测函数文件
```

通常还会准备：

```text
params.json
```

示例：

```bash
python3 testcase_generator.py \
  --mode auto \
  --call examples.number_impl:classify_number \
  --params examples/number_params.json \
  --out outputs/number_auto_cases.md \
  --out-spec outputs/number_auto_spec.json
```

被测函数文件示例：

```python
def classify_number(n: int) -> str:
    if n < 0:
        return "negative"

    if n == 0:
        return "zero"

    if n % 2 == 0:
        return "positive even"

    return "positive odd"
```

`params.json` 示例：

```json
{
  "params": {
    "n": {
      "type": "int",
      "min": -5,
      "max": 8
    }
  }
}
```

`params.json` 的作用是告诉工具参数范围。没有它时，工具会根据函数类型注解猜测参数，并使用默认范围。

### llm 模式需要的文件

`llm` 模式必须需要：

```text
被测函数文件
需求说明文件
.env 配置文件
```

示例：

```bash
python3 testcase_generator.py \
  --mode llm \
  --call examples.triangle_impl:check_triangle \
  --requirement examples/triangle_requirement.md \
  --out-spec outputs/triangle_llm_spec.json \
  --out outputs/triangle_llm_cases.json
```

被测函数文件用于让大模型理解函数签名和代码结构。

需求说明文件用于告诉大模型真实业务规则，例如：

```markdown
函数 check_triangle(d1, d2, d3) 用于判断三条边是否构成三角形。

如果任意边小于等于 0，返回 non-triangle。
如果不满足三角形不等式，返回 non-triangle。
如果三边相等，返回 equilateral triangle。
如果只有两边相等，返回 isosceles triangle。
否则返回 other triangle。
```

`.env` 用于配置大模型接口：

```env
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

`llm` 模式运行后会先生成 `spec`，再根据 `spec` 生成测试用例。

### hybrid 模式需要的文件

`hybrid` 模式必须需要：

```text
被测函数文件
需求说明文件
```

示例：

```bash
python3 testcase_generator.py \
  --mode hybrid \
  --call examples.triangle_impl:check_triangle \
  --requirement examples/triangle_requirement.md \
  --out-prompt outputs/triangle_llm_prompt.md
```

它会生成：

```text
outputs/triangle_llm_prompt.md
```

然后流程是：

```text
1. 把 Prompt 发给大模型
2. 大模型返回 spec JSON
3. 人工检查并保存为 outputs/triangle_llm_spec.json
4. 再用 rule 模式生成测试用例
```

后续命令：

```bash
python3 testcase_generator.py \
  --mode rule \
  --spec outputs/triangle_llm_spec.json \
  --out outputs/triangle_final_cases.csv
```

## 常见文件作用

| 文件 | 作用 |
|---|---|
| `*_impl.py` | 被测函数实现 |
| `*_params.json` | 参数类型、范围和候选值配置，主要给 `auto` 模式使用 |
| `*_spec.json` | 测试规格，包含参数和规则，主要给 `rule` 模式使用 |
| `*_requirement.md` | 自然语言需求说明，给 `llm` 和 `hybrid` 模式使用 |
| `.env` | 大模型 API Key、Base URL 和模型名配置 |
| `*_prompt.md` | 混合模式生成的大模型 Prompt |
| `outputs/*.csv` | CSV 测试报告 |
| `outputs/*.json` | JSON 测试报告或生成出来的 `spec` |
| `outputs/*.md` | Markdown 测试报告 |

## 更多样例函数

`examples/` 目录下还提供了几个可用于演示的被测函数：

| 文件 | 函数 | 说明 | 推荐模式 |
|---|---|---|---|
| `examples/number_impl.py` | `classify_number` | 判断负数、零、正偶数、正奇数 | `auto` |
| `examples/number_impl.py` | `absolute_value` | 求绝对值 | `auto` |
| `examples/grade_impl.py` | `grade_level` | 根据分数返回 A/B/C/D/F 或 invalid | `auto` |
| `examples/date_impl.py` | `is_leap_year` | 判断闰年 | `auto` |
| `examples/date_impl.py` | `days_in_month` | 判断某年某月天数 | `llm` 或 `rule` |
| `examples/password_impl.py` | `password_strength` | 判断密码强度 | `llm` 或 `rule` |
| `examples/shipping_impl.py` | `shipping_fee` | 根据重量和会员状态计算运费 | `auto` |

运行示例：

```bash
python3 testcase_generator.py \
  --mode auto \
  --call examples.grade_impl:grade_level \
  --params examples/grade_params.json \
  --out outputs/grade_auto_cases.md \
  --out-spec outputs/grade_auto_spec.json
```

```bash
python3 testcase_generator.py \
  --mode auto \
  --call examples.date_impl:is_leap_year \
  --params examples/date_params.json \
  --out outputs/leap_year_auto_cases.md \
  --out-spec outputs/leap_year_auto_spec.json
```

```bash
python3 testcase_generator.py \
  --mode auto \
  --call examples.shipping_impl:shipping_fee \
  --params examples/shipping_params.json \
  --out outputs/shipping_auto_cases.md \
  --out-spec outputs/shipping_auto_spec.json
```

## 规则模式

规则模式使用用户手写的 `spec` 文件。

命令示例：

```bash
python3 testcase_generator.py \
  --mode rule \
  --spec examples/triangle_spec.json \
  --out outputs/triangle_cases.csv
```

流程：

```text
读取 spec JSON
    ↓
校验 params 和 rules
    ↓
根据 params 枚举候选输入
    ↓
用 rule.when 判断输入属于哪个场景
    ↓
生成测试用例
    ↓
如果存在 target，则执行函数
    ↓
比较 expected 和 actual
    ↓
导出报告
```

原理：

- `params` 决定参数可以取哪些候选值；
- `rules` 决定什么输入属于什么测试场景；
- `rule.when` 是场景触发条件；
- `rule.expect` 是该场景的期望输出；
- 工具枚举输入后，逐条匹配规则，生成测试用例。

适用场景：

- 黑盒测试；
- 需求明确；
- 希望用人工规则判断代码是否正确；
- 课程实验报告需要可解释测试场景。

优点：

- 准确性最高；
- `expected` 来自需求规则；
- 能发现代码实现与需求不一致的问题。

限制：

- 需要用户手写规则；
- 规则表达式需要符合工具支持的安全表达式范围。

## 代码分析模式

代码分析模式根据 Python 函数源码自动生成测试规格。

命令示例：

```bash
python3 testcase_generator.py \
  --mode auto \
  --call examples.triangle_impl:check_triangle \
  --params examples/triangle_params.json \
  --out outputs/triangle_auto_cases.md \
  --out-spec outputs/triangle_auto_spec.json
```

流程：

```text
导入被测函数
    ↓
读取函数源码
    ↓
使用 AST 分析 if / return
    ↓
提取分支条件和返回值
    ↓
生成临时 spec
    ↓
枚举参数候选值
    ↓
匹配每个分支条件
    ↓
生成分支覆盖测试用例
    ↓
执行函数并导出报告
```

原理：

工具会分析类似下面的函数结构：

```python
def func(x):
    if x <= 0:
        return "invalid"

    if x == 1:
        return "one"

    return "other"
```

它会生成类似规则：

```text
branch_01: x <= 0
branch_02: not (x <= 0) and x == 1
branch_03: not (x <= 0) and not (x == 1)
```

然后根据参数范围找出能够覆盖这些分支的输入。

适用场景：

- 白盒测试；
- 分支覆盖；
- 快速了解已有函数行为；
- 回归测试。

优点：

- 不需要手写规则；
- 能快速生成分支覆盖用例；
- 可以自动导出中间 `spec`，便于查看和修改。

限制：

- 当前主要支持简单顺序 `if / return` 函数；
- `expected` 来自当前代码返回值；
- 如果代码本身写错，自动模式也可能把错误返回值当作期望结果。

## 大模型模式

大模型模式让大模型根据函数源码和需求说明生成测试规格。

命令示例：

```bash
python3 testcase_generator.py \
  --mode llm \
  --call examples.triangle_impl:check_triangle \
  --requirement examples/triangle_requirement.md \
  --out-spec outputs/triangle_llm_spec.json \
  --out outputs/triangle_llm_cases.json
```

流程：

```text
读取被测函数源码
    ↓
读取自然语言需求说明
    ↓
构造 Prompt
    ↓
调用 OpenAI 兼容大模型接口
    ↓
大模型返回 spec JSON
    ↓
本地校验 spec
    ↓
根据 spec 生成测试用例
    ↓
执行函数
    ↓
导出测试报告
```

原理：

大模型负责把自然语言需求转换成结构化规则，例如：

```json
{
  "id": "non_positive",
  "name": "边长小于等于 0，非三角形",
  "when": "d1 <= 0 or d2 <= 0 or d3 <= 0",
  "expect": "non-triangle"
}
```

之后工具不会盲目信任大模型输出，而是会校验：

- JSON 是否合法；
- 必要字段是否完整；
- 参数名是否正确；
- `when` 表达式是否安全；
- 是否使用了不支持的语法。

适用场景：

- 不想手写规则；
- 已有自然语言需求说明；
- 希望自动补充边界场景；
- 需要体现智能化测试用例设计流程。

优点：

- 降低规则编写成本；
- 能从需求说明中生成测试场景；
- 适合课程项目展示大模型辅助测试设计。

限制：

- 需要配置大模型 API；
- 默认从项目根目录 `.env` 读取 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`；
- 生成质量依赖模型和需求说明；
- 大模型可能生成错误或不完整规则，所以必须经过校验和人工检查。

## 混合模式

混合模式是推荐的稳妥流程。

它不会直接调用大模型生成最终测试用例，而是先生成一个 Prompt 文件，用户可以把 Prompt 发给大模型，得到 `spec` 草稿后人工确认，再用规则模式生成最终测试用例。

命令示例：

```bash
python3 testcase_generator.py \
  --mode hybrid \
  --call examples.triangle_impl:check_triangle \
  --requirement examples/triangle_requirement.md \
  --out-prompt outputs/triangle_llm_prompt.md
```

流程：

```text
读取函数源码
    ↓
读取需求说明
    ↓
生成大模型 Prompt
    ↓
用户将 Prompt 发给大模型
    ↓
大模型返回 spec 草稿
    ↓
用户检查和修改 spec
    ↓
使用 rule 模式生成最终测试用例
```

后续命令：

```bash
python3 testcase_generator.py \
  --mode rule \
  --spec outputs/triangle_llm_spec.json \
  --out outputs/triangle_final_cases.csv
```

适用场景：

- 没有配置 API Key；
- 希望人工确认大模型生成的规则；
- 对测试准确性要求较高；
- 课程答辩中需要展示“AI 生成 + 人工确认 + 程序执行”的流程。

优点：

- 比纯大模型模式更可控；
- 比纯手写规则更省力；
- 适合展示完整的人机协作流程。

限制：

- 需要用户手动复制 Prompt 和保存模型返回的 `spec`；
- 整体流程比 `llm` 模式多一步人工确认。

## 四种模式对比

| 模式 | 是否需要手写规则 | 是否需要大模型 API | expected 来源 | 适合用途 |
|---|---|---|---|---|
| `rule` | 需要 | 不需要 | 人工规则 | 黑盒测试、需求验证 |
| `auto` | 不需要 | 不需要 | 当前代码返回值 | 白盒测试、分支覆盖 |
| `llm` | 不需要 | 需要 | 大模型生成的规则 | 从需求自动生成测试规格 |
| `hybrid` | 部分需要 | 不一定 | 人工确认后的规则 | 更稳妥的大模型辅助流程 |

## 测试规格格式

核心字段：

- `function`：函数名；
- `target`：可选，被测函数位置，格式为 `module:function` 或 `file.py:function`；
- `max_cases_per_rule`：每条规则最多生成多少条测试用例；
- `params`：参数类型、范围和候选值；
- `rules`：测试场景规则，每条规则包含 `id/name/when/expect`。

示例：

```json
{
  "function": "check_triangle",
  "target": "examples.triangle_impl:check_triangle",
  "max_cases_per_rule": 3,
  "params": {
    "d1": {
      "type": "int",
      "min": -1,
      "max": 10
    },
    "d2": {
      "type": "int",
      "min": -1,
      "max": 10
    },
    "d3": {
      "type": "int",
      "min": -1,
      "max": 10
    }
  },
  "rules": [
    {
      "id": "equilateral",
      "name": "三边相等，等边三角形",
      "when": "d1 > 0 and d2 > 0 and d3 > 0 and d1 == d2 and d2 == d3",
      "expect": "equilateral triangle"
    }
  ]
}
```

## rules 的作用

`rules` 是测试场景定义。

每条规则说明：

- 什么输入属于这个场景；
- 这个场景期望输出什么；
- 报告里如何展示该场景。

规则字段说明：

| 字段 | 作用 |
|---|---|
| `id` | 场景编号 |
| `name` | 场景名称 |
| `when` | 场景触发条件 |
| `expect` | 期望结果 |

工具生成用例时会枚举 `params` 中的候选输入，然后判断是否满足 `rule.when`。如果满足，就生成一条测试用例，并把 `rule.expect` 作为 `expected`。

## 每条规则生成多少用例

默认每条规则最多生成 3 条测试用例。

可以通过 `max_cases_per_rule` 调整：

```json
{
  "max_cases_per_rule": 5
}
```

这是“最多数量”，不是固定数量。如果某条规则只能找到 1 个满足条件的输入，就只会生成 1 条。

## 表达式安全限制

`when` 是受限 Python 布尔表达式。工具会用 AST 白名单校验。

允许：

- 参数名；
- 常量；
- `and`、`or`、`not`；
- 比较运算；
- 基础算术运算。

禁止：

- 函数调用；
- 属性访问；
- 下标访问；
- `import`；
- `exec`；
- `eval`；
- 文件操作；
- 系统命令。

## LLM 请求故障排查

如果运行 `llm` 模式时报错：

```text
LLM API request failed: HTTP 403
error code: 1010
```

一般表示请求被大模型服务商的网关、代理或 Cloudflare 规则拒绝。优先检查：

- `.env` 中的 `OPENAI_BASE_URL` 是否正确；
- `OPENAI_BASE_URL` 是否是 API 基础地址，例如官方 OpenAI 是 `https://api.openai.com/v1`；
- `OPENAI_API_KEY` 是否有效；
- `OPENAI_MODEL` 是否是该服务商支持的模型名；
- 当前网络或 IP 是否被服务商限制；
- 如果使用第三方 OpenAI 兼容接口，确认它是否允许 Python 后端请求。

官方 OpenAI 示例：

```env
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

如果你使用的是第三方中转地址，需要按该服务商文档填写对应的 API 基础地址和模型名。工具会自动在 `OPENAI_BASE_URL` 后追加 `/responses`。

## 输出格式

`--out` 后缀决定导出格式：

- `.csv`：适合实验报告和 Excel；
- `.json`：适合程序读取；
- `.md`：适合 Markdown 报告。

报告字段包括：

- `case_id`；
- `function`；
- `scenario_id`；
- `scenario`；
- `condition`；
- 输入参数；
- `expected`；
- `actual`；
- `pass`；
- `error`。

## 依赖

当前项目只使用 Python 标准库。

推荐 Python 版本：

```text
Python 3.10+
```

不需要安装第三方包。
