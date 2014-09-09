def mark_headings(cells):
    # first pull out all the heading cells
    headings = []
    for cell in cells:
        if cell.cell_type != 'heading':
            continue
        headings.append((cell.level, cell.source, cell))

    if len(headings) == 0:
        return

    # then figure out the hierarchy of each heading
    min_level = min(x[0] for x in headings)
    curr_heading = [''] * min_level
    for i in xrange(len(headings)):
        level, source, cell = headings[i]
        if level <= len(curr_heading):
            while level <= len(curr_heading):
                curr_heading.pop()
        else:
            while level > (len(curr_heading) + 1):
                curr_heading.append('')

        curr_heading.append(source)
        headings[i] = tuple(curr_heading)
        cell.metadata['tree'] = tuple(curr_heading)


def get_points(cells):
    try:
        min_level = min(x.level for x in cells if x.cell_type == 'heading')
    except ValueError:
        min_level = 1

    heading_points = {}
    last_heading = [''] * min_level
    for cell in cells:
        if cell.cell_type == 'heading':
            last_heading = cell.metadata['tree']
            continue

        meta = cell.metadata.get('assignment', {})
        points = meta.get('points', 0)
        if points == '':
            points = 0
        else:
            points = float(points)

        curr_heading = list(last_heading)
        while len(curr_heading) > 0:
            if tuple(curr_heading) not in heading_points:
                heading_points[tuple(curr_heading)] = 0
            heading_points[tuple(curr_heading)] += points
            curr_heading.pop()

    return heading_points


def get_toc(cells):
    headings = [x for x in cells if x.cell_type == 'heading']
    if len(headings) == 0:
        return []

    min_level = min(x.level for x in headings)
    toc = []
    for cell in headings:
        level = cell.level
        source = cell.source
        indent = "\t" * (level - min_level)
        link = '<a href="#{}">{}</a>'.format(
            source.replace(" ", "-"), source)
        toc.append("{}* {}".format(indent, link))
    toc = "\n".join(toc)
    return toc
