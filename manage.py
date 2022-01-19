import sys


def main():
    try:
        from main.utils import run
    except ImportError as e:
        raise e
    run(sys.argv)


if __name__ == '__main__':
    main()
