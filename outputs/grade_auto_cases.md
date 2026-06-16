# 测试用例报告

|case_id|scenario|score|expected|actual|pass|
|---|---|---|---|---|---|
|TC_001|分支 1: score < 0 or score > 100|-5|invalid|invalid|True|
|TC_002|分支 1: score < 0 or score > 100|-4|invalid|invalid|True|
|TC_003|分支 1: score < 0 or score > 100|-1|invalid|invalid|True|
|TC_004|分支 2: score >= 90|90|A|A|True|
|TC_005|分支 2: score >= 90|100|A|A|True|
|TC_006|分支 3: score >= 80|80|B|B|True|
|TC_007|分支 3: score >= 80|89|B|B|True|
|TC_008|分支 4: score >= 70|70|C|C|True|
|TC_009|分支 4: score >= 70|79|C|C|True|
|TC_010|分支 5: score >= 60|60|D|D|True|
|TC_011|分支 5: score >= 60|69|D|D|True|
|TC_012|默认返回分支|0|F|F|True|
|TC_013|默认返回分支|1|F|F|True|
|TC_014|默认返回分支|50|F|F|True|
