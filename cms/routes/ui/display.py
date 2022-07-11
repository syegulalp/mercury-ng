from bottle import template, request
from math import ceil


class Tab:
    def __init__(self, title, link, active=False):
        self.title = title
        self.link = link


# TODO: search query should be made part of filter: options, not a standalone item


def format_grid(
    listing, buttons="", search_query=None, sort_model=None, listing_fmt={}
):

    qdict = {}
    if search_query:
        qdict["query"] = search_query

    sorting = []
    filtering = []

    for _ in request.query.keys():
        if _.startswith("sort:"):
            sort_field = _[5:]
            sort_value = request.query[_]
            sorting.append([getattr(sort_model, f"sortby_{sort_field}"), sort_value])
            qdict[_] = sort_value
        elif _.startswith("filter:"):
            filter_field = _[7:]
            filter_value = request.query[_]
            filtering.append(
                [getattr(sort_model, f"filterby_{filter_field}"), filter_value]
            )
            qdict[_] = filter_value

    for sort, sort_value in sorting:
        listing = sort(listing, sort_value)
    for filter, filter_value in filtering:
        listing = filter(listing, filter_value)

    params = {"total": listing.count(), "listing_model": listing.model()}

    params.update(
        last=int(ceil(params["total"] / 20)),
        page=int(request.query.get("page", 1)),
    )

    params.update(
        current_position=params["page"] * 20,
        prev_page=max(1, params["page"] - 1),
        next_page=min(params["page"] + 1, params["last"]),
    )

    listing2 = listing.paginate(params["page"], 20)

    params.update(
        local_count=listing2.count(), start_of_page=params["current_position"] - 19
    )
    params.update(
        end_of_page=params["start_of_page"] + params["local_count"] - 1,
    )

    return template(
        "include/grid.tpl",
        buttons=buttons,
        qdict=qdict,
        listing_fmt=listing_fmt,
        listing=listing2.iterator(),
        **params,
    )


def make_buttons(listing):
    return " ".join([str(_) for _ in listing])


class Button:
    def __init__(self, text: str, link: str, type_: str = "primary"):
        self.text = text
        self.link = link
        self.type = type_

    def __str__(self):
        return f'<a role="button" href="{self.link}" class="btn btn-sm btn-{self.type}">{self.text}</a>'


class Form:
    def __init__(self, target, key, abort):
        self.target = target
        self.key = key
        self.abort = abort

    def __str__(self):
        return f"""
<form action="{self.target}" method="POST" class="container-margins">
<input type="hidden" name="action_key" value="{self.key}">
<button type="submit" class="btn btn-success">Yes, I want to do this.</button>
<a href="{self.abort}" role="button" class="btn btn-danger">No, I don't want to do this.</a>
</form>
"""


class Notice:
    def __init__(self, type_="success"):
        self.type = type_
        self.msgs = []
        self.form = None

    def is_ok(self):
        return self.type == "success"

    def ok(self, msg):
        self.msgs.append(msg)

    def fail(self, msg):
        self.type = "danger"
        self.msgs.append(msg)

    def notice(self, msg):
        self.type = "warning"
        self.msgs.append(msg)

    def warning(self, notice, target, key, abort):
        self.type = "warning"
        self.msgs.append(notice)
        self.form = Form(target, key, abort)
