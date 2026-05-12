from __future__ import annotations

__all__ = ["TemplatedName", "Interpolation"]

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Interpolation:
    """One ``{...}`` segment in a templated name.

    ``variables`` is either a template global name or a literal list of values.
    ``label`` controls zip/product expansion; ``postfix`` stores text up to the
    next interpolation.
    """

    variables: str | list[str]
    label: int | None
    postfix: str

    def __hash__(self):
        # Create a hash based on immutable attributes
        return hash((tuple(self.variables), self.label, self.postfix))

    def deparse(self):
        """Return this interpolation using templating syntax."""

        if isinstance(self.variables, str):
            if self.label is None:
                return f"{{{self.variables}}}{self.postfix}"
            else:
                return f"{{{self.variables}@{self.label}}}{self.postfix}"
        else:
            if self.label is None:
                return f"{{[{', '.join(self.variables)}]}}{self.postfix}"
            else:
                return f"{{[{', '.join(self.variables)}]@{self.label}}}{self.postfix}"


@dataclass(frozen=True)
class TemplatedName:
    """A name containing zero or more templated ``{...}`` interpolations."""

    prefix: str
    interpolations: list[Interpolation]

    def render(self, index_map: dict[int | str, int]) -> str:
        """Render this name by selecting one value for each interpolation label."""

        rendered_name = self.prefix
        for interpolation in self.interpolations:
            index = index_map[interpolation.label]
            rendered_name += interpolation.variables[index] + interpolation.postfix
        return rendered_name

    def validate(
        self,
        globals: dict[str, list[str]],
        global_variable_implicit_label_map: dict[str, str],
        generated_label: str,
        implicit_label_local_variables_map: dict[str, list[str | int]],
        label_value_list_length_map: dict[int | str, int],
        function_labels: list[int] = [],
    ) -> tuple[
        dict[str, str],
        str,
        dict[str, list[str | int]],
        dict[int | str, int],
        TemplatedName,
    ]:
        """Resolve globals and implicit labels, returning an updated template name."""

        deparsed = self.deparse()
        updated_interpolations = []
        for interpolation in self.interpolations:
            # global
            if isinstance(interpolation.variables, str):
                global_variable = interpolation.variables
                if global_variable not in globals:
                    raise ValueError(f"Global variable {global_variable} has not been defined in {deparsed}")
                # no label, The label is implicit
                if interpolation.label is None:
                    if global_variable in global_variable_implicit_label_map:
                        new_label = global_variable_implicit_label_map[global_variable]
                    else:
                        new_label = f"label_{generated_label}"
                        generated_label += 1
                        global_variable_implicit_label_map[global_variable] = new_label
                    new_interpolation = replace(interpolation, variables=globals[global_variable], label=new_label)
                # label is explicit
                else:
                    new_interpolation = replace(interpolation, variables=globals[global_variable])
            # local
            else:
                new_interpolation = interpolation
                # no label, The label is implicit
                if interpolation.label is None:
                    for key, value in implicit_label_local_variables_map.items():
                        if interpolation.variables in value:
                            new_interpolation = replace(new_interpolation, label=key)
                            break
                    else:
                        new_label = f"label_{generated_label}"
                        generated_label += 1
                        implicit_label_local_variables_map[new_label].append(interpolation.variables)
                        new_interpolation = replace(new_interpolation, label=new_label)
            updated_interpolations.append(new_interpolation)
            if new_interpolation.label in label_value_list_length_map:
                if len(new_interpolation.variables) != label_value_list_length_map[new_interpolation.label]:
                    raise ValueError(f"Inconsistent number of variables in the same label: {deparsed}")
            else:
                # function labels are handles separately
                if new_interpolation.label not in function_labels:
                    label_value_list_length_map[new_interpolation.label] = len(new_interpolation.variables)
        updated_templated_name = replace(self, interpolations=updated_interpolations)
        # This code checks the updated template and the globals replaced with the values. Therefore, interpolation.variables
        # are a list of strings
        deparsed_updated = updated_templated_name.deparse()
        # The empty string case happens for reactions with no species
        if deparsed_updated != "" and deparsed_updated[0].isdigit():
            raise ValueError(f"A template cannot start with a number: {deparsed}")
        return (
            global_variable_implicit_label_map,
            generated_label,
            implicit_label_local_variables_map,
            label_value_list_length_map,
            updated_templated_name,
        )

    def __hash__(self):
        # Create a hash based on immutable attributes
        return hash((self.prefix, tuple(self.interpolations)))

    def deparse(self):
        """Return this name using templating syntax."""

        return self.prefix + "".join(interpolation.deparse() for interpolation in self.interpolations)
