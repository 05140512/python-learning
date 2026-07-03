import argparse # 用于解析命令行参数
from converter import excel_to_json

def get_args():
    parser = argparse.ArgumentParser(description="Excel转JSON工具")

    parser.add_argument("--input", required=True, help="Excel文件路径")
    parser.add_argument("--sheet", default=0, help="sheet名称或索引")
    parser.add_argument("--output", required=True, help="输出JSON路径")

    return parser.parse_args()

def main():
    args = get_args()

    excel_to_json(
        input_path=args.input,
        sheet=args.sheet,
        output_path=args.output
    )

    print("转换完成")