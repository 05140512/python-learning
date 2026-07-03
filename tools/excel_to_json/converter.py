import pandas as pd # 是 Python 里常用的表格数据处理库，核心类型是 DataFrame（类似 Excel 的一张表：行 + 列）。读 .xlsx 时通常还要 openpyxl（read_excel 的引擎依赖）。
import json
from pathlib import Path

def excel_to_json(excel_path, sheet=0, output_json_path="output.json"):
    # 读取Excel
    df = pd.read_excel(excel_path, sheet_name=sheet) # 把 Excel 某张 sheet 读成 DataFrame; sheet_name指定 sheet：可以是索引 0 或名称 "Sheet1"

    # 转换为字典
    # 转成「每行一条记录」的列表，例如 [{"姓名":"张三","年龄":20}, ...]，方便再 json.dump；
    # orient="records" 的含义：每一行 Excel 变成 JSON 里的一个对象，列名当字段名。
    data = df.to_dict(orient="records") 

    # 写入JSON
    output_file = Path(output_json_path) # 把 output_json_path 转换为 路径对象

    # output_file.parent: 获取 output_file 的父目录
    # .mkdir(parents=True, exist_ok=True): 创建父目录，如果父目录不存在则创建若目录不存在就创建；parents=True 表示中间多级目录也一起建；exist_ok=True 表示已存在不报错
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已输出到: {output_file}")