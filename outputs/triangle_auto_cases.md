# 测试用例报告

|case_id|scenario|d1|d2|d3|expected|actual|pass|
|---|---|---|---|---|---|---|---|
|TC_001|分支 1: d1 <= 0 or d2 <= 0 or d3 <= 0|-1|-1|-1|non-triangle|non-triangle|True|
|TC_002|分支 1: d1 <= 0 or d2 <= 0 or d3 <= 0|-1|-1|0|non-triangle|non-triangle|True|
|TC_003|分支 1: d1 <= 0 or d2 <= 0 or d3 <= 0|-1|-1|1|non-triangle|non-triangle|True|
|TC_004|分支 2: d1 + d2 <= d3 or d1 + d3 <= d2 or d2 + d3 <= d1|1|1|2|non-triangle|non-triangle|True|
|TC_005|分支 2: d1 + d2 <= d3 or d1 + d3 <= d2 or d2 + d3 <= d1|1|1|3|non-triangle|non-triangle|True|
|TC_006|分支 2: d1 + d2 <= d3 or d1 + d3 <= d2 or d2 + d3 <= d1|1|1|4|non-triangle|non-triangle|True|
|TC_007|分支 3: d1 == d2 and d2 == d3|1|1|1|equilateral triangle|equilateral triangle|True|
|TC_008|分支 3: d1 == d2 and d2 == d3|2|2|2|equilateral triangle|equilateral triangle|True|
|TC_009|分支 3: d1 == d2 and d2 == d3|3|3|3|equilateral triangle|equilateral triangle|True|
|TC_010|分支 4: d1 == d2 or d1 == d3 or d2 == d3|1|2|2|isosceles triangle|isosceles triangle|True|
|TC_011|分支 4: d1 == d2 or d1 == d3 or d2 == d3|1|3|3|isosceles triangle|isosceles triangle|True|
|TC_012|分支 4: d1 == d2 or d1 == d3 or d2 == d3|1|4|4|isosceles triangle|isosceles triangle|True|
|TC_013|默认返回分支|2|3|4|other triangle|other triangle|True|
|TC_014|默认返回分支|2|4|3|other triangle|other triangle|True|
|TC_015|默认返回分支|2|4|5|other triangle|other triangle|True|
