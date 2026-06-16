你是一个软件测试用例设计助手。

请根据以下函数源码和需求说明，生成函数测试规格 JSON。

要求：
1. 输出必须是合法 JSON；
2. 不要输出 Markdown；
3. 不要添加解释文字；
4. 每个测试场景必须包含 id、name、when、expect；
5. when 字段必须是 Python 布尔表达式；
6. rules 必须覆盖正常情况、异常情况、边界情况；
7. 参数名必须与函数参数一致；
8. 不要使用函数调用、属性访问、下标访问；
9. 不要生成工具不支持的表达式；
10. 如果需求说明和函数源码冲突，以需求说明为准。

目标函数：examples.triangle_impl:check_triangle

函数源码：
def check_triangle(d1: int, d2: int, d3: int) -> str:
    if d1 <= 0 or d2 <= 0 or d3 <= 0:
        return "non-triangle"

    if d1 + d2 <= d3 or d1 + d3 <= d2 or d2 + d3 <= d1:
        return "non-triangle"

    if d1 == d2 and d2 == d3:
        return "equilateral triangle"

    if d1 == d2 or d1 == d3 or d2 == d3:
        return "isosceles triangle"

    return "other triangle"


需求说明：
# 三角形判断函数需求

函数 `check_triangle(d1, d2, d3)` 用于判断三条边能够构成哪种三角形。

1. 如果任意边长小于等于 0，则返回 `non-triangle`。
2. 如果三条边不满足三角形两边之和大于第三边，则返回 `non-triangle`。
3. 如果三边相等，则返回 `equilateral triangle`。
4. 如果只有两边相等，则返回 `isosceles triangle`。
5. 如果三边互不相等且构成三角形，则返回 `other triangle`。


输出 JSON 格式：
{
  "function": "...",
  "target": "examples.triangle_impl:check_triangle",
  "max_cases_per_rule": 3,
  "params": {
    "参数名": {
      "type": "int",
      "min": -10,
      "max": 10
    }
  },
  "rules": [
    {
      "id": "...",
      "name": "...",
      "when": "...",
      "expect": "..."
    }
  ]
}
