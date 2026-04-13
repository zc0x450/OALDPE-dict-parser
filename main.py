import argparse
import re
import os
import sys
from datetime import datetime

# 在这里导入借用代码文件夹下reader.py中的查询函数
from borrowed_code.reader import query

try:
    from bs4 import BeautifulSoup

    HAS_BEAUTIFULSOUP = True
except ImportError:
    HAS_BEAUTIFULSOUP = False
    print("警告: 未找到BeautifulSoup库，将使用基本HTML解析。")
    print("      建议安装以获得更好的解析效果: pip install beautifulsoup4")

ascii_title = r"""
   ____          _      _____  _____  ______      _____        _____   _____ ______ _____  
  / __ \   /\   | |    |  __ \|  __ \|  ____|    |  __ \ /\   |  __ \ / ____|  ____|  __ \ 
 | |  | | /  \  | |    | |  | | |__) | |__ ______| |__) /  \  | |__) | (___ | |__  | |__) |
 | |  | |/ /\ \ | |    | |  | |  ___/|  __|______|  ___/ /\ \ |  _  / \___ \|  __| |  _  / 
 | |__| / ____ \| |____| |__| | |    | |____     | |  / ____ \| | \ \ ____) | |____| | \ \ 
  \____/_/    \_\______|_____/|_|    |______|    |_| /_/    \_\_|  \_\_____/|______|_|  \_\                                                                      
        
    OALDPE-PARSER
 ------------------------------------------------------------------------------------------
"""


def format_dictionary_result(raw_html, format_type="clean"):
    """
    格式化词典查询结果

    参数:
        raw_html: 原始HTML结果
        format_type: 'clean' - 清理后的结构化文本
                    'full' - 完整HTML（原始）
    """
    if format_type == "full":
        return raw_html

    # 分割多个条目
    entries = raw_html.split("\n---\n")
    formatted_entries = []

    for i, entry in enumerate(entries, 1):
        if format_type == "clean":
            content = format_clean(entry)
        else:
            # 默认使用clean格式
            content = format_clean(entry)

        if content.strip():
            if len(entries) > 1:
                formatted_entries.append(f"【条目 {i}】\n{content}")
            else:
                formatted_entries.append(content)

    # 用分隔线连接多个条目
    if len(formatted_entries) > 1:
        return "\n\n" + "=" * 60 + "\n\n".join(formatted_entries) + "\n" + "=" * 60
    elif formatted_entries:
        return formatted_entries[0]
    else:
        return ""


def format_clean(html_content):  # 结构化函数，提取中英文并分离有用信息
    """清理格式，输出结构化内容：英文+简体中文+繁体中文，完全分开"""
    if not HAS_BEAUTIFULSOUP:
        # 简化版HTML清理（无BeautifulSoup时使用）
        clean = re.sub(r"<[^>]+>", " ", html_content)
        clean = re.sub(r"\s+", " ", clean)
        return clean.strip()

    soup = BeautifulSoup(html_content, "html.parser")
    result_parts = []

    # 1. 提取单词和基本信息
    headword = soup.find("h1", class_="headword")
    if headword:
        result_parts.append(f"单词: {headword.get_text(strip=True)}")

    pos = soup.find("span", class_="pos")
    if pos:
        result_parts.append(f"词性: {pos.get_text(strip=True)}")

    # 提取音标
    phons = []
    for phon in soup.find_all("span", class_="phon"):
        phons.append(phon.get_text(strip=True))
    if phons:
        if len(phons) >= 2:
            result_parts.append(f"音标: 英{phons[0]} | 美{phons[1]}")
        else:
            result_parts.append(f"音标: {phons[0]}")

    result_parts.append("")  # 空行

    # 2. 提取英文释义
    result_parts.append("【英文释义】")
    sense_num = 1
    for sense in soup.find_all("li", class_="sense"):
        def_elem = sense.find("span", class_="def")
        if def_elem:
            eng = def_elem.get_text(strip=True)
            result_parts.append(f"{sense_num}. {eng}")
            sense_num += 1

    result_parts.append("")  # 空行

    # 3. 提取简体中文释义
    result_parts.append("【简体中文释义】")
    sense_num = 1
    for sense in soup.find_all("li", class_="sense"):
        chn_simple = sense.find("chn", class_="simple")
        if chn_simple:
            text = chn_simple.get_text(strip=True)
            if text:
                result_parts.append(f"{sense_num}. {text}")
        sense_num += 1

    result_parts.append("")  # 空行

    # 4. 提取繁体中文释义
    result_parts.append("【繁体中文释义】")
    sense_num = 1
    for sense in soup.find_all("li", class_="sense"):
        chn_traditional = sense.find("chn", class_="traditional")
        if chn_traditional:
            text = chn_traditional.get_text(strip=True)
            if text:
                result_parts.append(f"{sense_num}. {text}")
        sense_num += 1

    result_parts.append("")  # 空行

    # 5. 提取例句（英文一行，简体中文一行，繁体中文一行）
    ex_texts = soup.find_all("div", class_="exText")
    if ex_texts:
        result_parts.append("【例句】")
        for ex in ex_texts:
            x_elem = ex.find("span", class_="x")
            if x_elem:
                # 提取英文例句
                english_parts = []
                for child in x_elem.children:
                    if isinstance(child, str):
                        text = child.strip()
                        if text:
                            english_parts.append(text)
                    elif child.name and child.name != "xt":
                        text = child.get_text(strip=True)
                        if text:
                            english_parts.append(text)

                english_only = " ".join(english_parts)
                english_only = re.sub(r"\s+", " ", english_only).strip()

                # 提取简体中文翻译
                chn_simple = ex.find("chn", class_="simple")
                simple_text = ""
                if chn_simple:
                    simple_text = chn_simple.get_text(strip=True)

                # 提取繁体中文翻译
                chn_traditional = ex.find("chn", class_="traditional")
                traditional_text = ""
                if chn_traditional:
                    traditional_text = chn_traditional.get_text(strip=True)

                # 从xt标签中查找中文翻译
                if not simple_text or not traditional_text:
                    xt_elem = x_elem.find("xt")
                    if xt_elem:
                        if not simple_text:
                            chn_simple_in_xt = xt_elem.find("chn", class_="simple")
                            if chn_simple_in_xt:
                                simple_text = chn_simple_in_xt.get_text(strip=True)
                        if not traditional_text:
                            chn_traditional_in_xt = xt_elem.find(
                                "chn", class_="traditional"
                            )
                            if chn_traditional_in_xt:
                                traditional_text = chn_traditional_in_xt.get_text(
                                    strip=True
                                )

                # 输出例句
                if english_only and english_only.strip():
                    result_parts.append(f"  - {english_only}")

                    if simple_text:
                        result_parts.append(f"    {simple_text}")

                    if traditional_text and traditional_text != simple_text:
                        result_parts.append(f"    {traditional_text}")

                    # 每个例句单元之间添加空行
                    result_parts.append("")

    return "\n".join(result_parts)


def check_dict_file(dict_path):
    """检查词典文件是否存在"""
    if not os.path.exists(dict_path):
        print(f"错误: 找不到词典文件 '{dict_path}'")
        print(f"请确认:")
        print(f"  1. 文件 '{dict_path}' 是否存在")
        print(f"  2. 文件是否在程序所在目录")
        print(f"当前目录: {os.getcwd()}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description=ascii_title, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("-w", "--word", type=str, help="查询单个单词")
    parser.add_argument(
        "-e", "--excel", type=str, help="查询Excel文件中的单词列表（功能开发中）"
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["clean", "full"],
        default="clean",
        help="输出格式: clean(默认)/full",
    )
    parser.add_argument("-o", "--output", type=str, help="将结果保存到文件（可选）")

    args = parser.parse_args()

    # 词典文件路径
    DICT_PATH = "oaldpe.mdx"  # 词典文件放在和main.py同级的根目录下

    # 检查词典文件是否存在
    if not check_dict_file(DICT_PATH):
        return

    if args.word:  # 完善此处代码，使其实现对单个词汇的查找
        # 查询单词
        raw_result = query(DICT_PATH, args.word)

        if raw_result:
            print(f"\n查询: {args.word}")
            print("=" * 100)  # 测试，用于分割词汇和result 主要是好看点

            # 格式化结果
            cleaned_result = format_dictionary_result(
                raw_result, format_type=args.format
            )
            print(cleaned_result)

            # 保存到文件（可选） 未测试，后续测试
            if args.output:
                try:
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(f"查询: {args.word}\n")
                        f.write(
                            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        )
                        f.write("=" * 60 + "\n")
                        f.write(cleaned_result)
                    print(f"\n结果已保存到: {args.output}")
                except Exception as e:
                    print(f"保存文件时出错: {e}")
        else:
            print(f"未找到单词 '{args.word}' 的释义。")

    elif args.excel:  # 完善此处代码，使其实现对表格内词汇的批量查询
        # Excel批量查询功能
        print("Excel批量查询功能正在开发中...")
        print(f"您指定的Excel文件: {args.excel}")

    else:
        parser.print_help()

        # 显示使用说明
        print("\n格式选项说明:")
        print(
            "  -f clean    : 结构化的美观输出（默认）"
        )  # 进行格式美化，去掉源代码标签并进行排版
        print(
            "  -f full     : 原始HTML格式输出"
        )  # 用来检验clean结果是否和源代码有出入，也便于对结果进行美化

        # 显示示例
        print("\n使用示例:")
        print(
            "  python main.py -w hello                 # 查询hello单词（默认clean格式）"
        )
        print("  python main.py -w hello -f full         # 显示原始HTML格式")
        print("  python main.py -w hello -o result.txt   # 保存结果到文件")


if __name__ == "__main__":
    main()
