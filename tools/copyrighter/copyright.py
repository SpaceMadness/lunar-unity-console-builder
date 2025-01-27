from copyright_param import CopyrightParam


class Copyright:

    def __init__(self, text):
        self.text = text
        self.params = []

    def add_param(self, param):
        self.params.append(param)

    def set_param(self, name, value):
        for param in self.params:
            if name == param.name:
                param.value = value
                return

        self.add_param(CopyrightParam(name, value))

    def process(self):
        new_text = self.text

        for param in self.params:
            name = param.decorated_name
            value = param.value

            new_text = new_text.replace(name, value)

        return new_text

    @staticmethod
    def remove_header_comment(text):
        lines = text.splitlines(keepends=True)

        index = Copyright.find_first_non_comment_line_index(lines)
        if index == 0:
            return text

        lines = lines[index:]
        return ''.join(lines)

    @staticmethod
    def find_first_non_comment_line_index(lines):
        comment_found = False
        multiline = False
        skip_blank_lines = False

        for index, line in enumerate(lines):
            stripped_line = line.strip()

            if skip_blank_lines:
                if len(stripped_line) > 0:
                    return index
                continue

            if comment_found:
                if multiline:
                    skip_blank_lines = stripped_line.endswith('*/')
                else:
                    skip_blank_lines = not stripped_line.startswith('//')
            else:
                multiline = stripped_line.startswith('/*')
                comment_found = multiline or stripped_line.startswith('//')

                if not comment_found:
                    if len(stripped_line) > 0:
                        return index
                    skip_blank_lines = True

        return 0  # no comment found
