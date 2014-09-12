from jinja2 import Environment


def get_assignment_cell_type(cell):
    """Get the assignment cell type from the assignment metadata."""
    if 'assignment' not in cell.metadata:
        return '-'
    if 'cell_type' not in cell.metadata['assignment']:
        return '-'
    return cell.metadata['assignment']['cell_type']


def make_jinja_environment():
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=False)
    return env
