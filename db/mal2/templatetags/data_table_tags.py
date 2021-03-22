import logging

from django import template

from mal2.constants import ANNOTATION_FIELD_SUFFIX


register = template.Library()

################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# TABLE

@register.filter
def columns_counter(data_table, has_permission):
    labels_counter = len(get_labels(data_table))
    items_counter = len(get_items(data_table, has_permission))

    return labels_counter + items_counter + 1  # +1 for the add button


@register.filter
def get_items(data_table, has_permission):
    urls = []

    for url in data_table["urls"].get("item", []):
        if has_permission.get(url["field_name"]):
            urls.append(url)

    return urls


################################################################################
# LABEL

@register.filter
def get_labels(data_table):
    labels = []

    for field in data_table["field_names"]:
        labels.append(data_table["field_labels"].get(field))

    return labels


@register.filter
def get_label(data_table, field):
    return data_table["field_labels"].get(field)


################################################################################
# INPUT/SELECT

@register.filter
def get_input_type(data_table, field_name):
    field_name = field_name.replace(ANNOTATION_FIELD_SUFFIX, "")

    field_filters = data_table.get("field_filters", {})
    filters = field_filters.get("custom", {})
    field_filter = filters.get(field_name, {})

    return field_filter.get("type", "text")


@register.filter
def is_filter_excluded(data_table, field_name):
    excluded_filters = data_table.get("field_filters", {}).get("exclude", None)

    if excluded_filters and len(excluded_filters) > 0:
        if field_name in excluded_filters:
            return True

    return False


@register.filter
def get_select_options(data_table, field_name):
    field_name = field_name.replace(ANNOTATION_FIELD_SUFFIX, "")

    field_filters = data_table.get("field_filters", {})
    filters = field_filters.get("custom", {})
    field_filter = filters.get(field_name, {})

    return field_filter.get("options", (("", ""),))


@register.filter
def get_field_class(data_table, field_name):
    field_name = field_name.replace(ANNOTATION_FIELD_SUFFIX, "")

    field_filters = data_table.get("field_filters", {})
    filters = field_filters.get("custom", {})
    field_filter = filters.get(field_name, {})

    return field_filter.get(
        "classes",
        field_filters.get("default_classes", "col-12 col-md-3")
    )


################################################################################
# REGEX

@register.filter
def has_regex_enabled(data_table, field_name):
    field_filters = data_table.get("field_filters", {})
    regex_enabled = field_filters.get("regex_enabled", {})
    field_name = field_name.replace(ANNOTATION_FIELD_SUFFIX, "")
    return field_name in regex_enabled
