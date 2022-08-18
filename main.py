import argparse


def main(start=None, end=None):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get customer payments and write them to a JSON file."
    )
    parser.add_argument(
        "-s", "--start", help="get payments on or after this date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "-e", "--end", help="get payments before this date (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    main(start=args.start, end=args.end)
