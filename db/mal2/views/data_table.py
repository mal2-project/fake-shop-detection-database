import json
import logging

from django.core.exceptions import (
    FieldDoesNotExist,
    ImproperlyConfigured,
)
from django.db.models import (
    BooleanField,
    Case,
    CharField,
    F,
    ForeignKey,
    Manager,
    ManyToManyField,
    ManyToOneRel,
    Model,
    Q,
    TextField,
    Value,
    When,
)
from django.db.models.functions import (
    Cast,
    Concat,
)
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import (
    TemplateView,
    View,
)

from mal2.constants import ANNOTATION_FIELD_SUFFIX
from mal2.utils import (
    has_perms,
    re_escape,
)


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# DATA TABLE MIXIN

class DataTableMixin(object):
    def init_permissions(self, request, data_table):
        user = request.user

        self.has_autoreload = False
        self.has_add_permission = False
        self.has_permission = {}

        urls = data_table.get("urls")
        urls_item = urls.get("item", [])

        for url in urls_item:
            self.has_permission[url["field_name"]] = has_perms(
                user, url.get("permissions", [])
            )

        add = urls.get("add", None)

        if add:
            self.has_add_permission = has_perms(
                user, add.get("permissions", [])
            )

    @property
    def extra_context(self):
        return {
            "has_autoreload": self.has_autoreload,
            "has_add_permission": self.has_add_permission,
            "has_permission": self.has_permission,
        }

    def init_data_table_fields(self, data_table):
        columns = []

        field_names = data_table.get("field_names", None)

        if not field_names:
            raise ImproperlyConfigured(
                "%s requires 'field_names' in dict from 'get_data_table()'" % self.__class__.__name__
            )

        field_classes = data_table.get("field_classes", {})
        field_hidden = data_table.get("field_hidden", [])
        urls = data_table.get("urls")
        urls_item = urls.get("item", [])

        columns.append({
            "class": "icon-table",
            "data": "add",
            "responsivePriority": 0,
        })

        for index, field_name in enumerate(field_names):
            column = {
                "class": "%s %s" % (
                    field_name.replace("__", "-").replace("_", "-"),
                    " ".join(field_classes.get(field_name, [])),
                ),
                "data": field_name,
                "hide": field_name in field_hidden,
            }

            column = self.get_responsive_priority(
                data_table, column, field_name
            )

            columns.append(column)

        for url in urls_item:
            field_name = url["field_name"]

            if self.has_permission[field_name]:
                column = {
                    "class": "icon-table %s" % (
                        " ".join(field_classes.get(field_name, [])),
                    ),
                    "data": field_name,
                }

                column = self.get_responsive_priority(
                    data_table, column, field_name
                )

                columns.append(column)

        data_table["fields"] = json.dumps(columns)

        return data_table

    def init_data_table_options(self, data_table):
        options = data_table.get("options", {})
        responsive = options.get("responsive", "true")

        if options.get("autoreload"):
            self.has_autoreload = True

        dom_header = "<\"align-self-start col-12 col-sm-auto d-flex d-sm-block flex-column mb-1\"l><\"align-self-start col-12 col-sm-auto mb-2 ml-auto\"p>"
        dom_footer = "<\"align-self-start col-12 col-sm-auto d-flex d-sm-block flex-column mb-1\"l><\"align-self-start col-12 col-sm-auto ml-auto\"p><\"col-12 mb-2\"i>"
        dom_table = "<\"col-12 mb-1\"<\"table-responsive\"Bt>>"
        dom_table_responsive = "<\"col-12 mb-1\"Bt>"

        dom = "<\"align-items-center sm-gutters row\"%(dom_header)s%(dom_table)s%(dom_footer)s>" % {
            "dom_header": dom_header,
            "dom_footer": dom_footer,
            "dom_table": dom_table_responsive if responsive == "true" else dom_table,
        }

        default_options = {
            "export-csv": True,
            "dom": dom,
            "order": "[[1, \"asc\"]]",
            "page-length": "50",
            "responsive": responsive,
            **options,
        }

        data_table["options"] = {
            "data-%s" % key: value for key, value in default_options.items()
        }

        return data_table

    def get_responsive_priority(self, data_table, column, field_name):
        responsive_priorities = data_table.get(
            "responsive_priorities", None
        )

        if responsive_priorities:
            responsive_priority = responsive_priorities.get(field_name, None)

            if responsive_priority is not None:
                column["responsivePriority"] = responsive_priority

        return column

    def get_field_template(self, request, field_name, field_value, item):
        field_templates = self.data_table.get("field_templates", {})
        field_template = field_templates.get(field_name)

        if not field_template:
            return field_value

        context = {
            "field_value": field_value,
        }

        for field_name in self.data_table["field_names"]:
            if isinstance(item, dict):
                context[field_name] = item[field_name]
            else:
                context[field_name] = self._get_field_name(item, field_name)

        return render_to_string(
            field_template,
            context,
            request=request,
        )

    def add_item_actions(self, request, item_values, item):
        urls = self.data_table.get("urls")
        url_items = urls.get("item", [])
        url_defaults = urls.get("defaults", {})

        for url_item in url_items:
            url_item = {**url_defaults, **url_item}
            context = url_item.get("context", {})
            href = url_item.get("href", None)

            context["attrs"] = url_item.get("attrs", {})

            if href:
                url_id = url_item.get("id", "pk")

                if isinstance(item, dict):
                    # if item is a dict (DataTableListView)
                    item_id = item.get(url_id, item.get("id"))
                else:
                    # if item is a model (DataTableView)
                    url_ids = url_id.split("__")
                    last_item_id = None

                    for url_id in url_ids:
                        if last_item_id:
                            last_item_id = getattr(last_item_id, url_id)
                        else:
                            last_item_id = getattr(item, url_id)

                    item_id = last_item_id or getattr(item, "pk")

                context["href"] = reverse(href, kwargs={
                    url_id: item_id,
                })

            # append data of all fields to the url item context
            for field_name in self.data_table["field_names"]:
                if isinstance(item, dict):
                    # if item is a dict (DataTableListView)
                    context[field_name] = item[field_name]
                else:
                    # if item is a model (DataTableView)
                    context[field_name] = self._get_field_name(item, field_name)

            item_values[url_item["field_name"]] = render_to_string(
                url_item["template"],
                context,
                request=request,
            )

        return item_values

    def _get_field_name(self, item, field_name):
        field_names = field_name.split("__")
        last_field_name = getattr(item, field_names[0], None)

        if len(field_names) == 1:
            return last_field_name

        for index, field_name in enumerate(field_names):
            if index > 0:
                last_field_name = getattr(last_field_name, field_name, None)

        return last_field_name


class DataTableModelMixin(DataTableMixin):
    model = None

    def dispatch(self, request, *args, **kwargs):
        try:
            data_table = self.get_data_table()
        except AttributeError:
            raise ImproperlyConfigured(
                "%s requires an implementation of 'get_data_table()'" % self.__class__.__name__
            )

        # Permissions
        self.init_permissions(request, data_table)

        # Init
        self.annotations = data_table.get("annotations", {})
        data_table = self.init_data_table_annotations(data_table)
        data_table = self.init_data_table_fields(data_table)
        data_table = self.init_data_table_options(data_table)

        self.data_table = self.update_field_labels(data_table)

        # Fallback
        self.field_filters = self.data_table.get("field_filters", {})
        self.regex_enabled = self.field_filters.get("regex_enabled", [])
        self.field_outputs = self.data_table.get("field_outputs", {})

        return super().dispatch(request, *args, **kwargs)

    def init_data_table_annotations(self, data_table):
        new_data_table = {}

        relevant_settings = [
            "field_names",
            "field_classes",
            "field_labels",
            "field_filters",
            "field_templates",
            "field_outputs",
            "responsive_priorities"
        ]

        for key, settings in data_table.items():
            if key in relevant_settings:
                if isinstance(settings, list):
                    new_settings = []

                    for field_name in settings:
                        if field_name in self.annotations:
                            field_name = "%s%s" % (
                                field_name, ANNOTATION_FIELD_SUFFIX,
                            )

                        new_settings.append(field_name)
                    new_data_table[key] = new_settings
                elif isinstance(settings, dict):
                    new_settings = {}

                    for field_name, value in settings.items():
                        if field_name in self.annotations:
                            field_name = "%s%s" % (
                                field_name, ANNOTATION_FIELD_SUFFIX,
                            )

                        new_settings[field_name] = value
                    new_data_table[key] = new_settings
            else:
                new_data_table[key] = settings

        return new_data_table

    def get_field_verbose_name(self, field_relation_string, current_model, datatable_fields):
        relation_field_names = field_relation_string.split("__")

        for field_name in relation_field_names:
            for field in current_model._meta.get_fields():
                if field.name == field_name and field.__class__ != ManyToOneRel:
                    if field.__class__ in [ForeignKey, ManyToManyField]:
                        current_model = field.related_model
                        break

                    else:
                        custom_field_name = datatable_fields.get("field_labels", {})

                        field_name_prefix = custom_field_name.get(
                            "%s%s" % (
                                relation_field_names[0],
                                ANNOTATION_FIELD_SUFFIX,
                            ),
                            current_model._meta.verbose_name
                        )

                        if field_name_prefix != self.model._meta.verbose_name:
                            if field_name_prefix != field.verbose_name:
                                return "%s %s" % (
                                    field_name_prefix, field.verbose_name)

                        related_model = getattr(field, "related_model", None)

                        if related_model:
                            return related_model._meta.verbose_name

                        return "%s" % field.verbose_name

        return ""

    def update_field_labels(self, data_table):
        data_field_labels = data_table.get("field_labels", {})
        field_labels = {}

        for field_name in data_table["field_names"]:
            verbose_name = self.get_field_verbose_name(field_name, self.model, data_field_labels)

            if field_name in data_field_labels:
                field_labels[field_name] = data_field_labels[field_name]
            elif verbose_name and field_name:
                field_labels[field_name] = verbose_name

        data_table["field_labels"] = field_labels

        return data_table

    def get_field_type(self, field_name):
        for field in self.model._meta.get_fields():
            if field.name == field_name:
                return field.__class__

    def get_field_value(self, field_name, instance):
        relation_field_names = field_name.split("__")
        num_field_relations = len(relation_field_names)

        current_value = instance

        for relation_index in range(num_field_relations):
            field_name = relation_field_names[relation_index]
            current_value = getattr(current_value, field_name, "?")

            if isinstance(current_value, Manager):
                # if many2many field then take last relation -->
                # f.e. uba_sectors__code means when uba_sectors is m2m then code
                # is our next outputfield

                return ', '.join(
                    [str(i) for i in current_value.all().values_list(
                        relation_field_names[num_field_relations - 1], flat=True
                    )]
                )

            elif not isinstance(current_value, Model):
                # there could only be 3 states: many2many, foreignkey or any
                # other type (str, int, autofield) that could be returned directly
                # case 3: if it is a foreignkey then reset current_value and go
                # to next relation field_name

                return current_value

    def is_field_a_string_or_text_field(self, field_relation_string, model):
        if ANNOTATION_FIELD_SUFFIX in field_relation_string:
            return True

        relation_field_names = field_relation_string.split("__")

        model = self.model

        for field_name in relation_field_names:
            for field in model._meta.get_fields():
                if field.name == field_name and field.__class__ != ManyToOneRel:
                    if field.__class__ in [ForeignKey, ManyToManyField]:
                        model = field.related_model
                        break
                    elif field.__class__ in [TextField, CharField]:
                        return True

        return False

    def add_selected_relations(self, queryset):
        select_relations = self.data_table.get("select_relations", None)

        if select_relations:
            queryset = self.model.objects.all().select_related(
                *select_relations
            )

        return queryset

    def create_annotations(self, queryset):
        if not self.annotations:
            return queryset

        for field_name, annotations_values in self.annotations.items():
            # i want to check if the annotation_name is linked to a real field
            # in self.model if so we can check if the linked object exists for
            # example if object.address doesn't exists then we don't want to
            # annotate the field_names of that object because then it would
            # return ", , ,"

            try:
                linked_field = self.model._meta.get_field(field_name)
            except FieldDoesNotExist:
                linked_field = None

            annotation_field_name = "%s%s" % (
                field_name,
                ANNOTATION_FIELD_SUFFIX,
            )

            if linked_field:
                queryset = queryset.annotate(
                    **{
                        "%s" % annotation_field_name: Case(
                            When(
                                # check if real model FK is empty if not concat
                                **{
                                    "%s__isnull" % field_name: False
                                },
                                then=Concat(
                                    *annotations_values
                                ),
                            ),
                            When(
                                **{
                                    "%s__isnull" % field_name: True
                                },
                                then=Value(""),
                            )
                        )
                    }
                )
            else:
                queryset = queryset.annotate(
                    **{
                        "%s" % annotation_field_name: Concat(
                            *annotations_values
                        )
                    }
                )

        return queryset.distinct()

    def get_annotated_data(self, queryset):
        for field in self.regex_enabled:
            annotated_field_name = "%s%s" % (
                field.replace("__", "_"),
                ANNOTATION_FIELD_SUFFIX,
            )

            # already annotated field should not be overwritten
            # because they are already a charfield and with specific
            # fields/values
            if field in self.annotations:
                continue

            queryset = queryset.annotate(
                **{
                    annotated_field_name: Case(
                        When(
                            **{
                                "%s__isnull" % field: True
                            },
                            then=Cast(Value(""), CharField())
                        ),
                        When(
                            **{
                                "%s__isnull" % field: False
                            },
                            then=Cast(field, CharField())
                        )
                    )
                }
            )

        return queryset

    def get_search_type(self, field_name):
        field_filter = self.field_filters.get(field_name)

        if field_filter:
            search_type = field_filter.get("search_type", "icontains")
        else:
            search_type = "icontains"

        return "__%s" % search_type

    def is_regex_enabled(self, field_name):
        field_name = field_name.replace(ANNOTATION_FIELD_SUFFIX, "")

        return field_name in self.regex_enabled

    def get_filtered_field(self, queryset, field_name, search):
        search = search.strip()

        field_type = self.get_field_type(field_name)

        if field_type == BooleanField:
            queryset = queryset.filter(
                **{
                    "%s" % field_name: int(search) == 1 and True or False
                }
            )
        else:
            search_type = self.get_search_type(field_name)

            queryset = queryset.filter(
                **{
                    "%s%s" % (field_name, search_type,): search
                }
            )

        return queryset

    def get_filtered_regex_field(self, queryset, field_name, search):
        search = search.strip()

        if search == "!":
            queryset = queryset.filter(
                Q(**{
                    "%s" % field_name: ""
                })
                | Q(**{
                    "%s__isnull" % field_name: True
                })
                | Q(**{
                    "%s__regex" % field_name: r"^(\s){1,}$"
                })
            )
        elif search == "*":
            queryset = queryset.exclude(
                Q(**{
                    "%s" % field_name: ""
                })
                | Q(**{
                    "%s__isnull" % field_name: True
                })
                | Q(**{
                    "%s__regex" % field_name: r"^(\s){1,}$"
                })
            )
        elif (search.startswith("![") or search.startswith("[")) and search.endswith("]"):
            search = search.replace(" ", "")
            search_list = None

            if search.startswith("!"):
                char_offset = 2
            else:
                char_offset = 1

            search = search[char_offset:-1]

            if "-" in search:
                search_list_range = search.split("-")

                if len(search_list_range) == 2:
                    start_value = search_list_range[0]
                    end_value = search_list_range[1]

                    if start_value.isdigit() and end_value.isdigit():
                        search_list = list(
                            range(int(start_value), int(end_value) + 1, 1)
                        )
            else:
                search_list = search.split(",")

            if search_list and len(search_list) > 0:
                if char_offset == 1:
                    queryset = queryset.filter(
                        **{
                            "%s__in" % field_name: search_list
                        }
                    )
                else:
                    # !List means exclude
                    queryset = queryset.exclude(
                        **{
                            "%s__in" % field_name: search_list
                        }
                    )
        else:
            if search.startswith("!"):
                search = search.replace("!", "")

                regex_string = "^%s$" % (
                    re_escape(search).replace('\\*', '.*').replace('\\?', '.'),
                )

                queryset = queryset.exclude(
                    **{
                        "%s__iregex" % field_name: regex_string
                    }
                )
            else:
                regex_string = "^%s$" % (
                    re_escape(search).replace('\\*', '.*').replace('\\?', '.'),
                )

                queryset = queryset.filter(
                    **{
                        "%s__iregex" % field_name: regex_string
                    }
                )

        return queryset

    def get_filtered_data(self, request, queryset):
        data = request.POST if request.method == "POST" else request.GET

        col = 0
        field = "columns[%s][data]" % col

        while field in data:
            if field in data:
                field_name = data.get("columns[%s][data]" % col)
                search = data.get("columns[%s][search][value]" % col)

                if search:
                    if self.is_regex_enabled(field_name):
                        queryset = self.get_filtered_regex_field(queryset, field_name, search)
                    else:
                        queryset = self.get_filtered_field(queryset, field_name, search)

            col += 1
            field = "columns[%s][data]" % col

        return queryset

    def get_order_data(self, request, datatable_list):
        data = request.POST if request.method == "POST" else request.GET

        order_col = int(data.get("order[0][column]") or 0)
        order_dir = data.get("order[0][dir]", "asc")
        order = self.data_table["field_names"]

        if order_dir == "asc":
            return datatable_list.order_by(
                F(order[order_col - 1]).asc(nulls_last=True),
                "pk",
            )

        return datatable_list.order_by(
            F(order[order_col - 1]).desc(nulls_last=True),
            "pk",
        )

    def get_data_table_data(self, request, queryset):
        data = request.POST if request.method == "POST" else request.GET

        total_count = queryset.count()
        entries_per_page = int(data.get("length", 10))

        if entries_per_page != -1:
            start = int(data.get("start", 0))
            queryset = queryset[start:start + entries_per_page]

        data_list = []

        for index, item in enumerate(queryset):
            row_id = self.data_table.get("row_id", None)

            item_values = {
                "DT_RowId": "row-%s" % (
                    row_id and getattr(item, row_id) or index + 1
                ),
                "add": "",
            }

            for field_name in self.data_table["field_names"]:
                if field_name in self.field_outputs:
                    output_field_name = self.field_outputs.get(
                        field_name
                    )
                else:
                    output_field_name = field_name

                field_value = self.get_field_value(
                    output_field_name, item
                )

                if field_value is None or field_value == "":
                    field_value = "-"

                item_values.update({
                    field_name: self.get_field_template(
                        request, field_name, field_value, item,
                    )
                })

            item_values = self.add_item_actions(request, item_values, item)

            data_list.append(item_values)

        context = {
            "data": data_list,
            "draw": data.get("draw"),
            "recordsFiltered": total_count,
            "recordsTotal": total_count,
        }

        return context


class DataTableListMixin(DataTableMixin):
    def dispatch(self, request, *args, **kwargs):
        data_table = self.get_data_table()

        # Permissions
        self.init_permissions(request, data_table)

        # Init
        data_table = self.init_data_table_fields(data_table)
        self.data_table = self.init_data_table_options(data_table)

        # Fallback
        self.field_filters = self.data_table.get("field_filters", {})
        self.regex_enabled = self.field_filters.get("regex_enabled", [])

        return super().dispatch(request, *args, **kwargs)

    def get_filtered_regex_field(self, item, field_name, search):
        field_value = str(item[field_name]).lower()

        if search == "!":
            if not field_value:
                return item
        elif search == "*":
            if field_value:
                return item
        else:
            if search in field_value:
                return item

    def get_filtered_data(self, request, items):
        data = request.POST if request.method == "POST" else request.GET

        col = 0
        field = "columns[%s][data]" % col

        while field in data:
            if field in data:
                field_name = data.get("columns[%s][data]" % col)
                search = data.get("columns[%s][search][value]" % col)

                if search:
                    search = search.lower()
                    filtered_items = []

                    for item in items:
                        if field_name in self.regex_enabled:
                            item = self.get_filtered_regex_field(item, field_name, search)

                            if item:
                                filtered_items.append(item)
                        else:
                            if search in str(item[field_name]).lower():
                                filtered_items.append(item)

                    items = filtered_items

            col += 1
            field = "columns[%s][data]" % col

        return items

    def get_order_data(self, request, items):
        data = request.POST if request.method == "POST" else request.GET

        order_col = int(data.get("order[0][column]") or 0)
        order_dir = data.get("order[0][dir]", "asc")
        order = self.data_table["field_names"]

        if order_dir == "asc":
            reverse = False
        else:
            reverse = True

        return sorted(
            items,
            key=lambda item: item[order[order_col - 1]],
            reverse=reverse
        )

    def get_data_table_data(self, request, items):
        data = request.POST if request.method == "POST" else request.GET

        total_count = len(items)
        entries_per_page = int(data.get("length", 10))

        if entries_per_page != -1:
            start = int(data.get("start", 0))
            items = items[start:start + entries_per_page]

        data_list = []

        for index, item in enumerate(items):
            row_id = self.data_table.get("row_id", None)

            item_values = {
                "DT_RowId": "row-%s" % (
                    row_id and item[row_id] or index + 1
                ),
                "add": "",
            }

            for field_name, field_value in item.items():
                if field_name in self.data_table["field_names"]:
                    if field_value is None or field_value == "":
                        field_value = "-"

                    item_values.update({
                        field_name: self.get_field_template(
                            request, field_name, field_value, item,
                        )
                    })

            item_values = self.add_item_actions(request, item_values, item)

            data_list.append(item_values)

        context = {
            "data": data_list,
            "draw": data.get("draw"),
            "recordsFiltered": total_count,
            "recordsTotal": total_count,
        }

        return context


################################################################################
# DATA TABLE VIEW

class DataTableView(DataTableModelMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "data_table": self.data_table,
        })

        return context


@method_decorator(never_cache, name="dispatch")
class DataTableDataView(DataTableModelMixin, View):
    def get_objects(self):
        return self.model.objects.all().distinct()

    def get_context_data(self, **kwargs):
        request = self.request
        queryset = self.get_objects()

        queryset = self.add_selected_relations(queryset)
        queryset = self.create_annotations(queryset)
        queryset = self.get_annotated_data(queryset)
        queryset = self.get_filtered_data(request, queryset)
        queryset = self.get_order_data(request, queryset)
        context = self.get_data_table_data(request, queryset)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)


################################################################################
# DATA TABLE LIST VIEW

class DataTableListView(DataTableListMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "data_table": self.data_table,
        })

        return context


@method_decorator(never_cache, name="dispatch")
class DataTableListDataView(DataTableListMixin, View):
    def get_context_data(self, **kwargs):
        request = self.request
        items = self.get_list_items()

        items = self.get_filtered_data(request, items)
        items = self.get_order_data(request, items)
        context = self.get_data_table_data(request, items)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)
