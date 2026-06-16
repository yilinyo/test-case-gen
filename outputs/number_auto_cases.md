# 测试用例报告

|case_id|scenario|n|expected|actual|pass|
|---|---|---|---|---|---|
|TC_001|分支 1: n < 0|-5|negative|negative|True|
|TC_002|分支 1: n < 0|-4|negative|negative|True|
|TC_003|分支 1: n < 0|-3|negative|negative|True|
|TC_004|分支 2: n == 0|0|zero|zero|True|
|TC_005|分支 3: n % 2 == 0|2|positive even|positive even|True|
|TC_006|分支 3: n % 2 == 0|4|positive even|positive even|True|
|TC_007|分支 3: n % 2 == 0|6|positive even|positive even|True|
|TC_008|默认返回分支|1|positive odd|positive odd|True|
|TC_009|默认返回分支|3|positive odd|positive odd|True|
|TC_010|默认返回分支|5|positive odd|positive odd|True|
