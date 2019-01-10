import termcolor

def lines_subtext(text, start_line, end_line):
    """Return the text excerpt between the specified lines."""
    return "\n".join(text.split("\n")[start_line: end_line])


def split_text_in_three(text, start_line, start_chr, end_line, end_chr):
    """Split the text in three using 2 (line, column) control points"""
    lines = text.split("\n")
    before = "\n".join(lines[:start_line] + [lines[start_line][:start_chr]])
    if start_line == end_line:
        excerpt = lines[start_line][start_chr:end_chr]
    else:
        excerpt = "\n".join(
            [lines[start_line][start_chr:]] +
            ["\n".join(lines[start_line + 1: end_line])] +
            [lines[end_line][:end_chr]]
        )
    after = "\n".join([lines[end_line][end_chr:]] + lines[end_line + 1:])
    return before, excerpt, after


class FormattedKappaError(Exception):
    """Class to raise and pretty-print Kappa script syntax errors.

    When Kappa complains that the script doesn't make sense (through kappy),
    you can catch the error, pass it to FormattedKappaError.from_kappa_error()
    and reraise it. The resulting error will nicely print the errors in
    context.

    Examples
    --------

    >>> kappa_client = kappy.KappaStd()
    >>> kappa_client.add_model_string(model_string)
    >>> try:
    >>>     kappa_client.project_parse()
    >>> except kappy.KappaError as kappa_error:
    >>>     raise FormattedKappaError.from_kappa_error(kappa_error,
    >>>                                                model_string)

    """
    colors = {
        'error': 'red',
        'warning': 'orange'
    }
    
    @classmethod
    def _format_error_item(cls, error_item, model_string):
        color = cls.colors.get(error_item['severity'], 'black')
        header = "[%s] %s" % (error_item['severity'], error_item['text'])
        colored_header = termcolor.colored(header, color, attrs=('bold',))
        rg = error_item['range']
        start_line = rg['from_pos']['line'] - 1
        start_chr = rg['from_pos']['chr']
        end_line = rg['to_pos']['line'] - 1
        end_chr = rg['to_pos']['chr']
        before, excerpt, after = split_text_in_three(
            model_string, start_line, start_chr, end_line, end_chr)
        colored_excerpt = termcolor.colored(excerpt, color, attrs=('bold',))
        body_text = before + colored_excerpt + after
        body_text = lines_subtext(body_text, max(0, start_line - 2),
                                  end_line + 2)
        return colored_header + "\n\n" + body_text
    
    @classmethod
    def formatted_string(cls, error_items, model_string):
        """Create a FormattedKappaError from a Kappy project parsing error."""
        return "\n\n".join(cls._format_error_item(error_item, model_string)
                           for error_item in error_items)
    @classmethod
    def from_kappa_error(cls, kappa_error, model_string):
        """Create a FormattedKappaError from a Kappy project parsing error."""
        return FormattedKappaError(cls.formatted_string(
            model_string=model_string,
            error_items=kappa_error.args[0]
        ))
