class CopyrightParam:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    @property
    def decorated_name(self):
        return f"${{{self.name}}}"

    def __str__(self):
        return f"{{{self.name}:{self.value}}}"
