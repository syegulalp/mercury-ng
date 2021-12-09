menus = {
    "system_menu": {
        "type": "dropdown",
        "text": lambda x: "Main menu",
        "path": lambda x: "/",
        "contents": (
            "system_all_blogs",
            None,
            "system_users",
            "system_metadata",
            "system_dashboard",
            "system_about",
            "system_activity_log",
            "system_themes",
        ),
        "parent": None,
        "parent_context": lambda x: None,
    },
    "system_users": {
        "type": "label",
        "text": lambda x: f"Users",
        "path": lambda x: f"/users",
        "parent": "system_menu",
        "parent_context": lambda x: x,
    },
    "user_me": {
        "type": "label",
        "text": lambda x: f"{x.name} (#{x.id})",
        "path": lambda x: f"/me",
        "parent": "system_menu",
        "parent_context": lambda x: None,
    },
    "unlock_menu": {
        "type": "label",
        "text": lambda x: f"Unlock posts",
        "path": lambda x: f"/me/unlock",
        "parent": "user_me",
        "parent_context": lambda x: x,
    },
    "system_user": {
        "type": "label",
        "text": lambda x: f"{x.name} (#{x.id})",
        "path": lambda x: f"/user/{x.id}",
        "parent": "system_users",
        "parent_context": lambda x: x,
    },
    "system_metadata": {
        "type": "label",
        "text": lambda x: f"Metadata",
        "path": lambda x: f"/metadata",
        "parent": "system_menu",
        "parent_context": lambda x: x,
    },
    "system_metadata_edit": {
        "type": "text",
        "text": lambda x: f"Edit #{x[0].id}",
        "parent": "system_metadata",
        "parent_context": lambda x: x[1],
    },
    "system_metadata_new": {
        "type": "text",
        "text": lambda x: f"Create new metadata",
        "parent": "system_metadata",
        "parent_context": lambda x: x,
    },
    "system_themes": {
        "type": "label",
        "text": lambda x: f"Themes",
        "path": lambda x: f"/themes",
        "parent": "system_menu",
        "parent_context": lambda x: x,
    },
    "system_theme": {
        "type": "text",
        "text": lambda x: x.title,
        "path": lambda x: f"/theme/{x.id}",
        "parent": "system_themes",
        "parent_context": lambda x: x,
    },
    "blogs_menu": {
        "type": "dropdown",
        "text": lambda x: "Blogs",
        "path": lambda x: "/blogs",
        "contents": ("blogs_manage", "blogs_create"),
        "parent": "system_menu",
        "parent_context": lambda x: None,
    },
    "blog_menu": {
        "type": "dropdown",
        "text": lambda x: x.title,
        "path": lambda x: f"/blog/{x.id}",
        "contents": (
            "blog_posts",
            "blog_media",
            "blog_categories",
            "blog_tags",
            None,
            "blog_templates",
            "blog_themes",
            None,
            "blog_queue",
            "blog_republish",
            None,
            "blog_metadata",
            "blog_settings",
        ),
        "parent": "blogs_menu",
        "parent_context": lambda x: None,
    },
    "all_blog_posts": {
        "type": "label",
        "text": lambda x: f"Posts",
        "path": lambda x: f"/blog/{x.id}",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
    "all_blog_posts_search": {
        "type": "text",
        "text": lambda x: f"Search: {x[1]}",
        "parent": "all_blog_posts",
        "parent_context": lambda x: x[0],
    },
    "blog_media_search": {
        "type": "text",
        "text": lambda x: f"Search: {x[1]}",
        "parent": "blog_media",
        "parent_context": lambda x: x[0],
    },
    "blog_categories": {
        "type": "label",
        "text": lambda x: f"Categories",
        "path": lambda x: f"/blog/{x.id}/categories",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
    "new_blog_category": {
        "type": "text",
        "text": lambda x: f"New category for blog #{x.id}",
        "parent": "blog_categories",
        "parent_context": lambda x: x,
    },    
    "blog_category": {
        "type": "label",
        "text": lambda x: unsafe(x.title),
        "path": lambda x: x.edit_link,
        "parent": "blog_categories",
        "parent_context": lambda x: x.blog,
    },
    "blog_category_edit": {
        "type": "text",
        "text": lambda x: "Edit",
        "parent": "blog_category",
        "parent_context": lambda x: x,
    },
    "blog_category_delete": {
        "type": "text",
        "text": lambda x: "Delete",
        "parent": "blog_category",
        "parent_context": lambda x: x,
    },    
    "blog_category_in_posts": {
        "type": "text",
        "text": lambda x: f"Posts for category {x.title}",
        "parent": "blog_categories",
        "parent_context": lambda x: x.blog,
    },
    "blog_media": {
        "type": "label",
        "text": lambda x: f"Media",
        "path": lambda x: f"/blog/{x.id}/media",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
    "post_media_menu": {
        "type": "text",
        "text": lambda x: f"For post {x.id}",
        "parent": "blog_media",
        "parent_context": lambda x: x.blog,
    },
    "blog_media_item": {
        "type": "text",
        "text": lambda x: f"#{x.id}",
        "parent": "blog_media",
        "parent_context": lambda x: x.blog,
    },
    "blog_media_item_button": {
        "type": "label",
        "text": lambda x: f"#{x.id}",
        "path": lambda x: f"/blog/{x.blog.id}/media/{x.id}/edit",
        "parent": "blog_media",
        "parent_context": lambda x: x.blog,
    },
    "blog_media_item_in": {
        "type": "text",
        "text": lambda x: f"Posts using",
        "parent": "blog_media_item_button",
        "parent_context": lambda x: x,
    },
    "new_post": {
        "type": "text",
        "text": lambda x: f"Create new post",
        "parent": "blog_menu",
        "parent_context": lambda x: x.blog,
    },
    "blog_themes": {
        "type": "label",
        "text": lambda x: f"Themes",
        "path": lambda x: f"/blog/{x.id}/themes",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
    "blog_tags": {
        "type": "label",
        "text": lambda x: f"Tags",
        "path": lambda x: f"/blog/{x.id}/tags",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
    "blog_tag": {
        "type": "text",
        "text": lambda x: unsafe(x.title),
        "parent": "blog_tags",
        "parent_context": lambda x: x.blog,
    },
    "blog_tags_search": {
        "type": "text",
        "text": lambda x: f"Search: {x[1]}",
        "parent": "blog_tags",
        "parent_context": lambda x: x[0],
    },
    "blog_tag_in_posts": {
        "type": "label",
        "text": lambda x: f"Posts for tag: {x.title}",
        "path": lambda x: f"/blog/{x.blog.id}/tag/{x.id}/posts",
        "parent": "blog_tags",
        "parent_context": lambda x: x.blog,
    },
    "blog_tag_in_posts_search": {
        "type": "text",
        "text": lambda x: f"Search: {x[1]}",
        "parent": "blog_tag_in_posts",
        "parent_context": lambda x: x[0],
    },
    "edit_post": {
        "type": "text",
        "text": lambda x: f"Edit post #{x.id}",
        "parent": "blog_menu",
        "parent_context": lambda x: x.blog,
    },
    "templates_menu": {
        "type": "label",
        "text": lambda x: f"Templates",
        "path": lambda x: f"/blog/{x.id}/templates",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
    "templates_category": {
        "type": "text",
        "text": lambda x: x[1],
        # "path": lambda x: f"/blog/{x[0].id}/templates",
        "parent": "templates_menu",
        "parent_context": lambda x: x[0],
    },
    "template_menu": {
        "type": "text",
        "text": lambda x: f"Edit template #{x.id}",
        # "path": lambda x: f"/blog/{x.blog.id}/template/{x.id}/edit",
        "parent": "templates_menu",
        "parent_context": lambda x: x.blog,
    },
    "blog_settings": {
        "type": "label",
        "text": lambda x: f"Settings",
        "path": lambda x: f"/blog/{x.id}/settings",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
    "blog_settings_category": {
        "type": "text",
        "text": lambda x: x[1],
        "parent": "blog_settings",
        "parent_context": lambda x: x[0],
    },
    "blog_metadata": {
        "type": "label",
        "text": lambda x: "Metadata",
        "path": lambda x: f"/blog/{x}/metadata",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
    "blog_metadata_edit": {
        "type": "text",
        "text": lambda x: f"Edit #{x[0].id}",
        "parent": "blog_metadata",
        "parent_context": lambda x: x[1],
    },
    "new_template": {
        "type": "text",
        "text": lambda x: f"Create new template",
        "parent": "templates_menu",
        "parent_context": lambda x: x,
    },
    "blog_queue": {
        "type": "text",
        "text": lambda x: "Queue",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
    "blog_republish": {
        "type": "text",
        "text": lambda x: "Republishing",
        "parent": "blog_menu",
        "parent_context": lambda x: x,
    },
}

submenus = {
    "system_metadata": {
        "type": "link",
        "text": lambda x: "Metadata",
        "path": lambda x: "/metadata",
    },
    "system_themes": {
        "type": "link",
        "text": lambda x: "Blog themes",
        "path": lambda x: "/themes",
    },
    "system_users": {
        "type": "link",
        "text": lambda x: "Users",
        "path": lambda x: "/users",
    },
    "system_dashboard": {
        "type": "link",
        "text": lambda x: "Main menu",
        "path": lambda x: "/",
    },
    "system_about": {
        "type": "link",
        "text": lambda x: "System information",
        "path": lambda x: "/system/info",
    },
    "system_activity_log": {
        "type": "link",
        "text": lambda x: "Activity log",
        "path": lambda x: "/system/log",
    },
    "system_all_blogs": {
        "type": "link",
        "text": lambda x: "All blogs",
        "path": lambda x: "/blogs",
    },
    "blogs_manage": {
        "type": "link",
        "text": lambda x: "Manage blogs",
        "path": lambda x: "/blogs",
    },
    "blogs_create": {
        "type": "link",
        "text": lambda x: "Create blog",
        "path": lambda x: "/new-blog",
    },
    "blog_posts": {
        "type": "link",
        "text": lambda x: "Posts",
        "path": lambda x: f"/blog/{x.id}",
    },
    "blog_media": {
        "type": "link",
        "text": lambda x: "Media",
        "path": lambda x: f"/blog/{x.id}/media",
    },
    "blog_templates": {
        "type": "link",
        "text": lambda x: "Templates",
        "path": lambda x: f"/blog/{x.id}/templates",
    },
    "blog_settings": {
        "type": "link",
        "text": lambda x: "Settings",
        "path": lambda x: f"/blog/{x.id}/settings",
    },
    "blog_categories": {
        "type": "link",
        "text": lambda x: "Categories",
        "path": lambda x: f"/blog/{x.id}/categories",
    },
    "blog_tags": {
        "type": "link",
        "text": lambda x: "Tags",
        "path": lambda x: f"/blog/{x.id}/tags",
    },
    "blog_themes": {
        "type": "link",
        "text": lambda x: "Themes",
        "path": lambda x: f"/blog/{x.id}/themes",
    },
    "blog_metadata": {
        "type": "link",
        "text": lambda x: "Metadata",
        "path": lambda x: f"/blog/{x.id}/metadata",
    },
    "blog_queue": {
        "type": "link",
        "text": lambda x: "Queue",
        "path": lambda x: f"/blog/{x.id}/queue",
    },
    "blog_republish": {
        "type": "link",
        "text": lambda x: "Republishing",
        "path": lambda x: f"/blog/{x.id}/republish-options",
    },
}

from cms.models.utils import unsafe


def make_menu(start, context=None):

    menu_item = start
    menu_string = []

    while True:
        current_menu = menus[menu_item]
        submenu_string = []

        menu_type = current_menu["type"]

        if menu_type == "text":
            submenu_string.append(
                f'<span class="crumb-label">{unsafe(current_menu["text"](context))}</span>'
            )

        elif menu_type == "label":
            submenu_string.append(
                f'<a class="btn btn-sm btn-light crumb-label" href="{current_menu["path"](context)}">{unsafe(current_menu["text"](context))}</a>'
            )

        elif menu_type == "dropdown":
            submenu_string.append('<div class="btn-group">')
            submenu_string.append(
                f"""
<a class="btn btn-sm btn-light" href="{current_menu["path"](context)}">{unsafe(current_menu["text"](context))}</a>
<a class="btn btn-sm btn-light dropdown-toggle dropdown-toggle-split" id="{menu_item}_dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
<span class="sr-only">Toggle Dropdown</span>
</a>
</button>
"""
            )
            submenu_string.append(
                f'<div class="dropdown-menu" aria-labelledby="{menu_item}_dropdownMenuButton">'
            )
            for submenu_item in current_menu["contents"]:

                if submenu_item is None:
                    submenu_string.append('<div class="dropdown-divider"></div>')
                    continue

                submenu_obj = submenus[submenu_item]

                if submenu_obj["type"] == "link":
                    submenu_string.append(
                        f'<a class="dropdown-item" href="{submenu_obj["path"](context)}">{unsafe(submenu_obj["text"](context))}</a>'
                    )

            submenu_string.append("</div></div>")

        menu_string.append("".join(submenu_string))
        menu_item = current_menu["parent"]
        if menu_item is None:
            break

        context = current_menu["parent_context"](context)
    return "".join(reversed(menu_string))
