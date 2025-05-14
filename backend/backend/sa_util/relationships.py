from typing import Any, Callable, get_args, get_origin
import sqlalchemy as sa
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from sqlalchemy.orm import DeclarativeBase, Load


def select_relationships_deep(
    sa_class: type[DeclarativeBase],
    mask_class: type[BaseModel],
    sa_load_method: Callable[[Any, Any], Load],
):
    """
    this functions creates a hirarchy of selectinload statements of a given sqlalchemy orm class filtered by a pydantic mask class
    """
    assert issubclass(sa_class, DeclarativeBase)
    assert issubclass(mask_class, BaseModel)

    mask_struct: dict[str, FieldInfo] = mask_class.model_fields

    mapper = sa.inspect(sa_class, raiseerr=True)
    relationships = mapper.relationships
    loads: list[Load] = []
    for k in mask_struct:
        if not k in relationships:
            continue

        query = sa_load_method(getattr(sa_class, k))

        rel = relationships[k]
        rel_sa_class = rel.mapper.class_

        resolved_type = resolve_field_type(mask_class, field_name=k)

        child_loads = select_relationships_deep(
            rel_sa_class, resolved_type, sa_load_method
        )

        query = query.options(*child_loads)

        loads.append(query)

    return loads


def resolve_field_type(class_: type[BaseModel], field_name: str):
    mask_struct: dict[str, FieldInfo] = class_.model_fields
    
    child_field_info = mask_struct[field_name]
    child_field_type = get_args(child_field_info.annotation)
    child_field_type = [_ for _ in child_field_type if _ is not type(None)]

    assert (
        len(child_field_type) <= 1
    ), f"Expected child_field_type contain only 1 type: {child_field_type}"

    resolved_type = (
        child_field_type[0]
        if len(child_field_type)
        else get_origin(child_field_type)
    )
    
    return resolved_type