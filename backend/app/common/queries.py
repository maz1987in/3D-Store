import uuid
from app.common.error_handling import QueryValidationError
from sqlalchemy_utils.functions import cast_if
import sqlalchemy as sql
from sqlalchemy import or_
import operator

#from sqlalchemy.sql import operators

# https://stackoverflow.com/questions/59392535/flask-multiple-parameters-how-to-avoid-multiple-if-statements-when-querying-mult

class Filter:
    supported_operators = ('eq', 'ne', 'lt', 'gt', 'le', 'ge', 'like')

    def __init__(self, column, operator, value):
        self.model_name, self.columns = self.parse_model_column(column)
        self.operator = operator
        self.value = value
        self.validate()

    def parse_model_column(self, column):
        # Split the column into model name and column names
        parts = column.split('.')
        if len(parts) == 2:
            return parts[0], parts[1].split(',')
        else:
            return None, parts[0].split(',')

    def validate(self):
        if self.operator not in self.supported_operators:
            raise QueryValidationError(
                f"operator `{self.operator}` is not one of supported "
                f"operators `{self.supported_operators}`"
            )

class Sorter:

    def __init__(self, column, direction):
        self.column = column
        self.direction = direction
        self.validate()

    def validate(self):
        if self.direction not in ('asc', 'desc'):
            raise QueryValidationError(
                f"sort direction `{self.direction}` is not 'asc' or 'desc'"
            )


def create_filters(filters):
    filters_processed = []
    if filters is None:
        # No filters given
        return filters_processed
    elif isinstance(filters, str):
        try:
            for _filter in filters.split("&"):
            # if only one filter given
                filter_split = _filter.rsplit(",",2)
                filters_processed.append(
                    Filter(*filter_split)
                )
        except Exception as e:
            raise QueryValidationError("Filter query invalid")
    elif isinstance(filters, list):
        # if more than one filter given
        try:
            filters_processed = [Filter(*_filter.rsplit(",",2)) for _filter in filters]
        except Exception as e:
            raise QueryValidationError("Filter query invalid")
    else:
        # Programer error
        raise TypeError(
            f"filters expected to be `str` or list "
            f"but was of type `{type(filters)}`"
        )

    return filters_processed


def apply_filter(models, model_name, column_names, operator_name, value):
    #print(f"Applying filter: model_name={model_name}, column_names={column_names}, operator_name={operator_name}, value={value}")
    model = None

    if model_name is not None:
        model = next((m for m in models if m.__name__.lower() == model_name.lower()), None)
        if model is None:
            raise QueryValidationError(f"Model `{model_name}` does not exist")
    else:
        for m in models:
            if any(hasattr(m, column_name) for column_name in column_names):
                model = m
                break
        if model is None:
            raise QueryValidationError(f"Columns `{column_names}` do not exist in any of the models")

    conditions = []
    for column_name in column_names:
        # Check if the column_name exists in the model
        if hasattr(model, '__translatable__') and hasattr(model.__translatable__['class'], column_name):
            target_column = getattr(model.__translatable__['class'], column_name)
            is_translated = True
        else:
            target_column = getattr(model, column_name, None)
            is_translated = False

        if target_column is None:
            continue
            #raise QueryValidationError(f"Column `{column_name}` does not exist in model `{model_name}`")

        if operator_name == 'like':
            search = f"%{value}%"
            if target_column.type.python_type is uuid.UUID:
                condition = cast_if(target_column, sql.String).ilike(search.replace('-', ''))
            else:
                condition = target_column.ilike(search)
        else:
            op = getattr(operator, operator_name)
            if target_column.type.python_type is uuid.UUID:
                condition = op(cast_if(target_column, sql.String), value.replace('-', ''))
            else:
                condition = op(target_column, value)

        conditions.append((condition, model, is_translated))

    return conditions

def filter_query(filters, query, models):
    # If models is not a list, make it a list
    if not isinstance(models, list):
        models = [models]

    # Track which models have been joined
    joined_models = set()

    for _filter in filters:
        model_name = None
        for model in models:
            if any(hasattr(model, column_name) for column_name in _filter.columns):
                model_name = model.__name__
                #break
        if model_name is None:
            raise QueryValidationError(f"Columns `{_filter.columns}` do not exist in any of the models")

        conditions = apply_filter(models, model_name, _filter.columns, _filter.operator, _filter.value)
        condition_group = [condition for condition, model, is_translated in conditions]

        # If there is a translated column involved, join the models
        if any(is_translated for _, _, is_translated in conditions):
            for model in models:
                if hasattr(model, '__translatable__') and model not in joined_models:
                    query = query.outerjoin(model.__translatable__['class'])
                    joined_models.add(model)

        query = query.filter(or_(*condition_group))

    return query.distinct()  # Use distinct() to eliminate duplicate rows


def create_filters_and_sorters(filters, sorters):
    filters_processed = create_filters(filters)
    sorters_processed = create_sorters(sorters)
    return filters_processed, sorters_processed

def create_sorters(sorters, sort_order='asc'):
    sorters_processed = []
    if sorters is None:
        return sorters_processed
    elif isinstance(sorters, str):
        try:
            for sorter in sorters.split("&"):
                # Append the sort order to each sorter
                sorter_split = [sorter, sort_order]
                sorters_processed.append(tuple(sorter_split))
        except Exception as e:
            raise QueryValidationError("Sorter query invalid")
    elif isinstance(sorters, list):
        try:
            for sorter in sorters:
                # Append the sort order to each sorter
                sorter_split = [sorter, sort_order]
                sorters_processed.append(tuple(sorter_split))
        except Exception as e:
            raise QueryValidationError("Sorter query invalid")
    else:
        raise TypeError(
            f"sorters expected to be `str` or list "
            f"but was of type `{type(sorters)}`"
        )

    return sorters_processed


def apply_sort(model, column_name, direction):
    """
    Apply sorting to a query.
    :param model: SQLAlchemy model.
    :param column_name: Column to sort by.
    :param direction: Sort direction ('asc' or 'desc').
    """
    if hasattr(model, column_name):
        target_column = getattr(model, column_name)
        return target_column.asc() if direction == 'asc' else target_column.desc()
    else:
        raise QueryValidationError(f"Column `{column_name}` does not exist in model `{model.__name__}`")


def filter_and_sort_query(filters, sorters, query, models):
    # If models is not a list, make it a list
    if not isinstance(models, list):
        models = [models]

    # Apply filters
    if filters:
        query = filter_query(filters, query, models)
    
    # Apply sorters
    if sorters:
        for sorter in sorters:
            column = sorter[0]
            order = sorter[1]
            for model in models:
                if hasattr(model, column):
                    sort_condition = apply_sort(model, column, order)
                    if sort_condition is not None:
                        query = query.order_by(sort_condition)
    
    return query
