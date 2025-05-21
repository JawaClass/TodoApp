from typing import Any, Callable, get_args, get_origin, get_type_hints
import sqlalchemy as sa
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from sqlalchemy.orm import DeclarativeBase, Load, selectinload


def select_relationships_deep(
    sa_class: type[DeclarativeBase],
    mask_class: type[BaseModel],
    sa_load_method: Callable[[Any, Any], Load] = selectinload,
):
    """
    this functions creates a hirarchy of selectinload statements of a given sqlalchemy orm class filtered by a pydantic mask class
    """
    print(f"select_relationships_deep... {sa_class=} {mask_class=}")
    assert issubclass(sa_class, DeclarativeBase)
    assert issubclass(mask_class, BaseModel), f"mask_class {mask_class=} :: {type(mask_class)} is not subclass of pydantic.BaseModel"

    mask_struct: dict[str, FieldInfo] = mask_class.model_fields

    mapper = sa.inspect(sa_class, raiseerr=True)
    relationships = mapper.relationships
    loads: list[Load] = []

    field_types = get_type_hints(mask_class)

    for k in mask_struct:
        if not k in relationships:
            continue

        query = sa_load_method(getattr(sa_class, k))

        rel = relationships[k]
        rel_sa_class = rel.mapper.class_

        resolved_type = resolve_type(type_=field_types.get(k))

        child_loads = select_relationships_deep(
            rel_sa_class, resolved_type, sa_load_method
        )

        query = query.options(*child_loads)

        loads.append(query)

    return loads
 

def resolve_type(type_: type[Any]):

    def most_inner_arg(tp):
        args = get_args(tp)
        if not args:
            return tp
        first_ = [a for a in args if a is not type(None)][0]
        return most_inner_arg(first_)
    
    return most_inner_arg(type_)

  