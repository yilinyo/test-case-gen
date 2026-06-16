# 测试用例报告

|case_id|scenario|weight|is_member|expected|actual|pass|
|---|---|---|---|---|---|---|
|TC_001|分支 1: weight <= 0|-1|False|-1|-1|False|
|TC_002|分支 1: weight <= 0|-1|True|-1|-1|False|
|TC_003|分支 1: weight <= 0|0|False|-1|-1|False|
|TC_004|分支 2: is_member and weight <= 5|1|True|0|0|True|
|TC_005|分支 2: is_member and weight <= 5|2|True|0|0|True|
|TC_006|分支 2: is_member and weight <= 5|3|True|0|0|True|
|TC_007|分支 3: weight <= 1|1|False|5|5|True|
|TC_008|分支 4: weight <= 5|2|False|10|10|True|
|TC_009|分支 4: weight <= 5|3|False|10|10|True|
|TC_010|分支 4: weight <= 5|4|False|10|10|True|
|TC_011|分支 5: weight <= 20|6|False|20|20|True|
|TC_012|分支 5: weight <= 20|6|True|20|20|True|
|TC_013|分支 5: weight <= 20|7|False|20|20|True|
|TC_014|默认返回分支|21|False|50|50|True|
|TC_015|默认返回分支|21|True|50|50|True|
|TC_016|默认返回分支|22|False|50|50|True|
