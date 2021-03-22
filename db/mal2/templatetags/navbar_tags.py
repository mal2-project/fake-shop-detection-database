from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import mark_safe
from django.utils.text import slugify

from mal2.utils import has_perms


register = template.Library()


################################################################################
# HELPERS

@register.filter
def include(html_file, path):
    return "%s%s.html" % (path, html_file,)


@register.simple_tag
def django_navbar_expand():
    return settings.DJANGO_NAVBAR_EXPAND


################################################################################
# DJANGO NAVBAR

@register.simple_tag
def django_navbar(request, navbar=None, *args, **kwargs):
    def _get_nav_classes(nav_item, navbar_is_right):
        align = nav_item.get("align", "left")
        nav_classes = nav_item.get("classes", [])

        if align == "left" or navbar_is_right:
            nav_classes.append(
                "ml-%s-1" % settings.DJANGO_NAVBAR_EXPAND
            )
        elif align == "right" and not navbar_is_right:
            nav_classes.append(
                "ml-%s-auto" % settings.DJANGO_NAVBAR_EXPAND
            )

            navbar_is_right = True

        return nav_classes, navbar_is_right

    def _render_dropdown_menu(dropdown_items, nav_item_title):
        dropdown_menu = ""
        dropdown_links = ""

        for dropdown_item in dropdown_items:
            permissions = dropdown_item.get("permissions", None)

            if has_perms(request.user, permissions):
                divider = dropdown_item.get("divider", None)

                if divider:
                    dropdown_link = render_to_string(
                        "navbar/dropdown_divider.html",
                    )
                else:
                    dropdown_item_href = dropdown_item.get("href", "#")

                    dropdown_link = render_to_string(
                        "navbar/dropdown_item.html", {
                            "attrs": dropdown_item.get("attrs"),
                            "href": dropdown_item_href,
                            "is_active": str(dropdown_item_href) in request.path,
                            "title": dropdown_item.get("title"),
                        },
                        request,
                    )

                dropdown_links += dropdown_link

        if dropdown_links:
            dropdown_menu = render_to_string(
                "navbar/dropdown_menu.html", {
                    "dropdown_items": mark_safe(dropdown_links),
                    "id": slugify(nav_item_title),
                },
                request,
            )

        return dropdown_menu

    def _render_nav_links(navbar):
        nav_item_links = ""
        navbar_is_right = False

        if navbar is None:
            navbar = settings.DJANGO_NAVBAR

        navbar_left = [item for item in navbar if not item.get("align") or item["align"] == "left"]
        navbar_right = [item for item in navbar if item["align"] == "right"]

        navbar = navbar_left + navbar_right

        for nav_item in navbar:
            permissions = nav_item.get("permissions", None)

            if has_perms(request.user, permissions):
                dropdown_items = nav_item.get("dropdown_items", [])
                nav_item_title = nav_item.get("title")
                nav_item_href = nav_item.get("href", "#")

                nav_item_title = nav_item_title.replace(
                    "%USERNAME%", request.user.username
                )

                dropdown_menu = _render_dropdown_menu(dropdown_items, nav_item_title)

                if dropdown_menu or len(dropdown_items) == 0:
                    navbar_classes, navbar_is_right = _get_nav_classes(nav_item, navbar_is_right)

                    nav_item_link = render_to_string(
                        "navbar/nav_item.html", {
                            "attrs": nav_item.get("attrs"),
                            "classes": " ".join(navbar_classes),
                            "dropdown_menu": dropdown_menu,
                            "href": nav_item_href,
                            "icon": nav_item.get("icon"),
                            "id": slugify(nav_item_title),
                            "is_active": str(nav_item_href) in request.path,
                            "is_dropdown": dropdown_items and True or False,
                            "title": nav_item_title,
                        },
                        request,
                    )

                    nav_item_links += nav_item_link

        return nav_item_links

    navbar_nav = render_to_string(
        "navbar/navbar_nav.html", {
            "nav_links": mark_safe(_render_nav_links(navbar)),
        },
        request,
    )

    return mark_safe(navbar_nav)
