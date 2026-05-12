from collections import defaultdict
from dataclasses import replace

from ...templated_expressions import free_variable_names
from ...templated_expressions.ast import BaseTemplatedFunction, TemplatedVariable
from ...templated_expressions.deparser import deparse_expression
from ...templated_expressions.templated_name import TemplatedName


def validate_and_update_templates(
    templated_objects: TemplatedName
    | TemplatedVariable
    | BaseTemplatedFunction
    | list[TemplatedName | TemplatedVariable | BaseTemplatedFunction],
    globals: dict[str, list[str]],
) -> tuple[
    dict[TemplatedName, TemplatedName]
    | dict[TemplatedVariable, TemplatedVariable]
    | dict[BaseTemplatedFunction, BaseTemplatedFunction],
    dict[int | str, int],
]:
    if not isinstance(templated_objects, list):
        templated_objects = [templated_objects]

    global_variable_implicit_label_map: dict[str, str] = {}  # This is a map of global variable to its label
    # This is a map of implicit label to its local variables definition
    implicit_label_local_variables_map: dict[str, list[str | int]] = defaultdict(list)
    # This is a map of label to the count of the variables with that label:  [c, p, t, d] belongs to label 0 -> {0: 4}.
    label_value_list_length_map: dict[int | str, int] = {}
    templated_objects_map = {}
    generated_label: int = 0

    # order maters, functions need to check last
    for templated_object in templated_objects:
        match templated_object:
            case TemplatedName() | TemplatedVariable():
                (
                    global_variable_implicit_label_map,
                    generated_label,
                    implicit_label_local_variables_map,
                    label_value_list_length_map,
                    updated_templated_name,
                ) = templated_object.validate(
                    globals,
                    global_variable_implicit_label_map,
                    generated_label,
                    implicit_label_local_variables_map,
                    label_value_list_length_map,
                )
                templated_objects_map[templated_object] = updated_templated_name

    for templated_object in templated_objects:
        match templated_object:
            case BaseTemplatedFunction(labels=labels):
                for label in labels:
                    if label in label_value_list_length_map:
                        raise ValueError(
                            f"Label {label} has been used in a function template {deparse_expression(templated_object)}"
                            " and cannot be used outside."
                        )
                (
                    global_variable_implicit_label_map,
                    generated_label,
                    implicit_label_local_variables_map,
                    label_value_list_length_map,
                    updated_templated_name,
                ) = templated_object.validate(
                    globals,
                    global_variable_implicit_label_map,
                    generated_label,
                    implicit_label_local_variables_map,
                    label_value_list_length_map,
                )
                templated_objects_map[templated_object] = updated_templated_name

    return templated_objects_map, label_value_list_length_map
