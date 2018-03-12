# Test files individually to find problem characters

def pandoc_test(md):
    command = (
        f"pandoc {md.name}"
        f" -t epub3 -o {md.stem}.epub"
        " -f markdown-native_divs "
        " -f markdown+smart "
        f'--metadata title="TEST"')
    print(md.name)
    os.system(command)


def test_markdown_individually():
    clean(config.test_dir)
    config.test_dir.mkdir()
    for md in config.markdown_dir.glob("*.md"):
        shutil.copy(md, config.test_dir)
    os.chdir(config.test_dir)
    files = sorted(list(Path().glob("*.md")))
    pprint.pprint(files)
    with open('combined.md', 'w') as combined:
        for f in files:
            combined.write(f.read_text() + "\n")
    pandoc_test(Path('combined.md'))
