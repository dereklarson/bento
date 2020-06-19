def format_code(code_string, indents=1):
    raw_lines = code_string.strip().split("\n")
    indent_list = [len(line) - len(line.lstrip(" ")) for line in raw_lines]
    # Get the first non-zero indent
    base_indent = min(set(indent_list) - set([0]))
    stripped_lines = [line.replace(" " * base_indent, "") for line in raw_lines]
    indent_str = " " * 4 * indents
    return indent_str + f"\n{indent_str}".join(stripped_lines)
