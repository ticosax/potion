from werkzeug.utils import cached_property

from flask_potion.fields import Object, ToOne as GenericToOne
from flask_potion.utils import get_value, route_from


class InlineModel(Object):
    """
    :param dict properties:
    :param model:
    """
    def __init__(self, properties, model, **kwargs):
        super(InlineModel, self).__init__(properties, **kwargs)
        self.model = model

    def converter(self, instance):
        instance = super(InlineModel, self).converter(instance)
        if instance is not None:
            instance = self.model(**instance)
        return instance


class ToOne(GenericToOne):
    """
    Same as flask_potion.fields.ToOne
    except it will use the local id stored on the ForeignKey field to serialize the field.
    This is an optimisation to avoid additional lookups to the database,
    in order to prevent fetching the remote object, just to obtain its id,
    that we already have.
    Limitations:
    - It works only if the foreign key is made of a single field.
    - It works only if the serialization is using the ForeignKey as source of information to Identify the remote resource.
    - `attribute` parameter is ignored.
    """
    def output(self, key, obj):
        column = getattr(obj.__class__, key)
        local_columns = column.property.local_columns
        assert len(local_columns) == 1
        local_column = list(local_columns)[0]
        key = local_column.key
        return self.format(get_value(key, obj, self.default))

    def formatter(self, item):
        return self.formatter_key.format(item, is_local=True)
