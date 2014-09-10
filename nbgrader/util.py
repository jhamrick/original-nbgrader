def get_min_level(cells):
    try:
        min_level = min(x.level for x in cells if x.cell_type == 'heading')
    except ValueError:
        min_level = 1
    return min_level


def get_toc(cells):
    min_level = get_min_level(cells)
    toc = []
    for cell in cells:
        if cell.cell_type != 'heading':
            continue

        level = cell.level
        source = cell.source
        indent = "\t" * (level - min_level)
        link = '<a href="#{}">{}</a>'.format(
            source.replace(" ", "-"), source)
        toc.append("{}* {}".format(indent, link))

    toc = "\n".join(toc)
    return toc
