import jsonschema

from flockwave.spec.schema import ref_resolver

__all__ = ("create_schema_validator",)


def create_schema_validator(schema, multi: bool = False):
    resolver = jsonschema.RefResolver.from_schema(
        schema, handlers={"http": ref_resolver}
    )

    def validator(obj):
        if multi and isinstance(obj, list):
            return all(validator(item) for item in obj)
        else:
            try:
                jsonschema.validate(obj, schema, resolver=resolver)
                return True
            except jsonschema.ValidationError:
                return False

    return validator
