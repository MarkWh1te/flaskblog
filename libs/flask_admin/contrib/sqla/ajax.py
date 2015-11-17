from sqlalchemy import or_

from flask.ext.admin._compat import as_unicode, string_types
from flask.ext.admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE


class QueryAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, session, model, **options):
        """
            Constructor.

            :param fields:
                Fields to run query against
        """
        super(QueryAjaxModelLoader, self).__init__(name, options)

        self.session = session
        self.model = model
        self.fields = options.get('fields')

        if not self.fields:
            raise ValueError('AJAX loading requires `fields` to be specified for %s.%s' % (model, self.name))

        self._cached_fields = self._process_fields()

        primary_keys = model._sa_class_manager.mapper.primary_key
        if len(primary_keys) > 1:
            raise NotImplementedError('Flask-Admin does not support multi-pk AJAX model loading.')

        self.pk = primary_keys[0].name

    def _process_fields(self):
        remote_fields = []

        for field in self.fields:
            if isinstance(field, string_types):
                attr = getattr(self.model, field, None)

                if not attr:
                    raise ValueError('%s.%s does not exist.' % (self.model, field))

                remote_fields.append(attr)
            else:
                # TODO: Figure out if it is valid SQLAlchemy property?
                remote_fields.append(field)

        return remote_fields

    def format(self, model):
        if not model:
            return None

        return (getattr(model, self.pk), as_unicode(model))

    def get_one(self, pk):
        return self.session.query(self.model).get(pk)

    def get_list(self, term, offset=0, limit=DEFAULT_PAGE_SIZE):
        query = self.session.query(self.model)

        filters = (field.ilike(u'%%%s%%' % term) for field in self._cached_fields)
        query = query.filter(or_(*filters))

        return query.offset(offset).limit(limit).all()


def create_ajax_loader(model, session, name, field_name, options):
    attr = getattr(model, field_name, None)

    if attr is None:
        raise ValueError('Model %s does not have field %s.' % (model, field_name))

    if not hasattr(attr, 'property') or not hasattr(attr.property, 'direction'):
        raise ValueError('%s.%s is not a relation.' % (model, field_name))

    remote_model = attr.prop.mapper.class_
    return QueryAjaxModelLoader(name, session, remote_model, **options)
