class UserNotLoggedIn(Exception):
    pass


class MissingFileInfo(Exception):
    pass


class BlogPermissionError(Exception):
    pass


class TemplateError(Exception):
    """
    Exception used for errors in a CMS template.
    """

    def __init__(self, message: str, tpl: "SpecialTemplate", lineno: int):
        self.tpl = tpl
        self.message = message
        self.lineno = lineno
        super().__init__(message)

    def __str__(self):
        try:
            l = ("\n" + unsafe(self.tpl.template_obj.text) + "\n").split("\n")[
                self.lineno
            ]
        except Exception as e:
            l = unsafe(self.tpl.template_obj.text)
        return f"Template: {self.tpl.template_obj.title}\nLine: {self.lineno}\n>>> {l}\n{self.message}"
