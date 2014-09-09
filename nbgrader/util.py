def get_min_level(cells):
    try:
        min_level = min(x.level for x in cells if x.cell_type == 'heading')
    except ValueError:
        min_level = 1
    return min_level


def mark_headings(cells):
    min_level = get_min_level(cells)
    curr_heading = [''] * min_level
    for cell in cells:
        if cell.cell_type == 'heading':
            level = cell.level
            source = cell.source

            if level <= len(curr_heading):
                while level <= len(curr_heading):
                    curr_heading.pop()
            else:
                while level > (len(curr_heading) + 1):
                    curr_heading.append('')

            curr_heading.append(source)

        cell.metadata['tree'] = tuple(curr_heading)


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
