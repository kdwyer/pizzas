from typing import Dict, List

import wtforms
from wtforms import widgets

from . import models

# TODO
# Ideally we want to build a structure of forms that present the user with
# something like this:
#
# pizza-name    (price) [ ]
#  topping-name (price) [ ]
#  ...
# ...
#
# We want to build this structure dynamically from the available pizzas and
# toppings in the database.


class FormLevelErrorForm(wtforms.Form):
    """
    A form that exposes form level errors.

    Based on this commit, though they modify the base form class
    https://github.com/wtforms/wtforms/commit/22636b55eda9300b549c8bbaae6f9ae31595d445
    """

    # Redundant if we upgrade to wtforms 3

    def __init__(
        self, formdata=None, obj=None, prefix="", data=None, meta=None, **kwargs
    ):
        super().__init__(
            formdata=formdata, obj=obj, prefix=prefix, data=data, meta=meta, **kwargs
        )
        self.form_errors: List[str] = []

    @property
    def errors(self) -> Dict:
        errors = super().errors
        if self.form_errors:
            errors[None] = self.form_errors
        return errors


def get_toppings() -> List[models.Topping]:
    session = models.Session()  # type: ignore
    return session.query(models.Topping.name).order_by(models.Topping.name).all()


class MultiCheckboxField(wtforms.SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ToppingForm(wtforms.Form):
    # TODO better choices
    toppings = MultiCheckboxField(label="", choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        names = get_toppings()
        choices = [(name, name) for name, in names]
        self.toppings.choices = choices

    def create_obj(self, session) -> List[models.Topping]:
        """Creates a list of toppings instances based on form data."""
        names = self.data["toppings"]
        return (
            session.query(models.Topping)
            .filter(models.Topping.name.in_(names))
            .order_by(models.Topping.name)
            .all()
        )


class PizzaForm(FormLevelErrorForm):

    name = wtforms.StringField(render_kw={"readonly": True})
    selected = wtforms.BooleanField(default=False)
    toppings = wtforms.FormField(ToppingForm)

    def create_obj(self, session) -> List[models.Item]:
        """Creates a list of order items based on form data."""
        # Should we validate first?
        if not self.data["selected"]:
            return []
        pizza = (
            session.query(models.Pizza)
            .filter(models.Pizza.name == self.data["name"])
            .one()
        )
        toppings = self.toppings.create_obj(session)
        item = models.Item(pizza=pizza)
        items = [item]
        toppings_items = [models.Item(pizza=pizza, topping=t) for t in toppings]
        items.extend(toppings_items)
        return items

    def validate(self) -> bool:
        if not super().validate():
            return False
        if self.toppings.data["toppings"] and not self.selected.data:
            self.form_errors.append("You must select a pizza as well as toppings")
            return False
        return True


class OrderForm(wtforms.Form):
    forms = wtforms.FieldList(wtforms.FormField(PizzaForm), min_entries=1)

    def __init__(self, *args, **kwargs):
        label = kwargs.pop("label", None)
        super().__init__(*args, **kwargs)
        if label is not None:
            self.selected.label = wtforms.Label(self.selected.id, label)

    def create_obj(self, session) -> models.Order:
        """Creates an order based on form data."""
        items = [
            obj for objs in [f.create_obj(session) for f in self.forms] for obj in objs
        ]
        order = models.Order(items=items)
        session.add(order)
        return order
