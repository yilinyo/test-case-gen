# 测试用例报告

|case_id|scenario|year|expected|actual|pass|
|---|---|---|---|---|---|
|TC_001|分支 1: year <= 0|0|False|False|True|
|TC_002|分支 1: year <= 0|-1|False|False|True|
|TC_003|分支 2: year % 400 == 0|1200|True|True|True|
|TC_004|分支 2: year % 400 == 0|2400|True|True|True|
|TC_005|分支 2: year % 400 == 0|400|True|True|True|
|TC_006|分支 3: year % 100 == 0|100|False|False|True|
|TC_007|分支 3: year % 100 == 0|1900|False|False|True|
|TC_008|分支 4: year % 4 == 0|4|True|True|True|
|TC_009|分支 4: year % 4 == 0|2024|True|True|True|
|TC_010|默认返回分支|1|False|False|True|
|TC_011|默认返回分支|2399|False|False|True|
|TC_012|默认返回分支|2023|False|False|True|
