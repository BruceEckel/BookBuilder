lines = [x for x in range(0, 26)]

def extract(lines):
    start = lines.pop()
    while lines[0] != start + 2:
        print(f"extract: {lines.pop()}")

def go(lines):
    while lines:
        print(f"lines[0]: {lines[0]}")
        if lines[0] == 5:
            extract(lines)
        elif lines[0] == 12:
            extract(lines)
        else:
            print(f"pop: {lines}")


if __name__ == '__main__':
    go(lines)
    print(f"lines: {lines}")