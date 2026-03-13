import argparse


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


def main():
    parser = argparse.ArgumentParser(
        description=ascii_title, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("-w", "--word", type=str, help="look up a single word")
    parser.add_argument(
        "-e", "--excel", type=str, help="look up the words contained in an excel sheet"
    )

    args = parser.parse_args()
    if args.word:
        pass
    elif args.excel:
        pass
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
