# 三角形判断函数需求

函数 `check_triangle(d1, d2, d3)` 用于判断三条边能够构成哪种三角形。

1. 如果任意边长小于等于 0，则返回 `non-triangle`。
2. 如果三条边不满足三角形两边之和大于第三边，则返回 `non-triangle`。
3. 如果三边相等，则返回 `equilateral triangle`。
4. 如果只有两边相等，则返回 `isosceles triangle`。
5. 如果三边互不相等且构成三角形，则返回 `other triangle`。
