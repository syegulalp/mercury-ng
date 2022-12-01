import functools
from bottle import SimpleTemplate
import cms.models.models as models
import re
import imp
from cms.errors import TemplateError

class SpecialTemplate(SimpleTemplate):
    """
    Modified version of the Bottle SimpleTemplate. Modifications include special keywords and caching of compiled templates in a blog's template set.
    """

    localcache = {}
    ssi = {}

    insert_re = re.compile(r"""^\s*?%\s*?insert\s*?\(['"](.*?)['"]\)""", re.MULTILINE)

    def __init__(self, template: "models.Template", *a, **ka):
        self.template_obj = template
        self.theme = self.template_obj.theme

        ka["source"] = self.template_obj.text

        super().__init__(*a, **ka)

    def _insert(self, _env, _name=None, **kwargs):
        try:
            template_to_insert = SpecialTemplate.localcache[(self.theme.id, _name)]
        except KeyError:
            template_to_insert = models.Template.get(
                theme=self.theme, title=_name
            )._cached()
            SpecialTemplate.localcache[(self.theme.id, _name)] = template_to_insert
        env = _env.copy()
        env.update(kwargs)
        return template_to_insert.execute(env["_stdout"], env)

    def _load(self, _env, _name=None, **kwargs):
        try:
            template_to_insert = SpecialTemplate.localcache[(self.theme.id, _name)]
        except KeyError:
            template_to_insert = models.Template.get(theme=self.theme, title=_name)
            if template_to_insert.text.startswith("#!"):
                code = template_to_insert.text
                module = imp.new_module(_name)
                exec(code, module.__dict__)
                template_to_insert = module
            else:
                template_to_insert = template_to_insert._cached().execute([], {})
            SpecialTemplate.localcache[(self.theme.id, _name)] = template_to_insert
        return template_to_insert

    def _ssi(self, _env, _name=None, **kwargs):
        try:
            ssi_to_insert = SpecialTemplate.ssi[(self.theme.id, _name)]
        except KeyError:
            ssi_to_insert = models.Template.get(theme=self.theme, title=_name).ssi()
            SpecialTemplate.ssi[(self.theme.id, _name)] = ssi_to_insert
        _env["_stdout"].append(ssi_to_insert)
        return _env

    def execute(self, _stdout, kwargs):
        env = self.defaults.copy()
        env.update(kwargs)
        env.update(
            {
                "_stdout": _stdout,
                "_printlist": _stdout.extend,
                "insert": functools.partial(self._insert, env),
                "ssi": functools.partial(self._ssi, env),
                "include": functools.partial(self._include, env),
                "rebase": functools.partial(self._rebase, env),
                "_rebase": None,
                "_str": self._str,
                "_escape": self._escape,
                "get": env.get,
                "setdefault": env.setdefault,
                "defined": env.__contains__,
                "load": functools.partial(self._load, env),
            }
        )
        try:
            eval(self.co, env)
        except Exception as e:
            lasterr = e.__traceback__.tb_next
            raise TemplateError(e, self, lasterr.tb_lineno)
        if env.get("_rebase"):
            subtpl, rargs = env.pop("_rebase")
            rargs["base"] = "".join(_stdout)  # copy stdout
            _stdout = []  # clear stdout
            return self._include(env, subtpl, **rargs)
        return env
