"""Tests for forms."""

import pytest
import wtforms
from pizza.orders import forms, models
from webob.multidict import MultiDict


@pytest.fixture
def add_pizzas(clean_db, db_session):
    db_session.add(models.Pizza(name="margherita", price=899))
    db_session.add(models.Pizza(name="funghi", price=899))
    db_session.add(models.Topping(name="mushrooms", price=50))
    db_session.add(models.Topping(name="scamorza", price=200))


class TestFormLevelErrorForm:
    # https://github.com/wtforms/wtforms/commit/22636b55eda9300b549c8bbaae6f9ae31595d445

    def test_form_level_errors(self):
        class F(forms.FormLevelErrorForm):
            a = wtforms.IntegerField()
            b = wtforms.IntegerField()

            def validate(self):
                if not super().validate():
                    return False

                if (self.a.data + self.b.data) % 2 != 0:
                    self.form_errors.append("a + b should be even")
                    return False

                return True

        data1 = MultiDict([("a", 1), ("b", 1)])
        f = F(formdata=data1)
        assert f.validate()
        assert not f.form_errors
        assert not f.errors

        data2 = MultiDict([("a", 0), ("b", 1)])
        f = F(formdata=data2)
        assert not f.validate()
        assert ["a + b should be even"] == f.form_errors
        assert ["a + b should be even"] == f.errors[None]


# 1. Test returns a single pizza
# 2. Test returns multiple pizza
# 3. Test handles toppings
# 4. Test filters empty pizzas


@pytest.mark.usefixtures("add_pizzas")
class TestOrderForm:
    def test_orders_one_pizzas(self, db_session):
        formdata = MultiDict(
            [("forms-0-name", "margherita"), ("forms-0-selected", True)]
        )
        form = forms.OrderForm(formdata=formdata)
        margherita = db_session.query(models.Pizza).filter_by(name="margherita").one()

        form.validate()
        order = form.create_obj(db_session)

        assert len(order.items) == 1
        item = order.items[0]
        assert item.pizza is margherita

    def test_orders_one_pizza_with_toppings(self, db_session):
        formdata = MultiDict(
            [
                ("forms-0-name", "margherita"),
                ("forms-0-selected", True),
                ("forms-0-toppings-toppings", "mushrooms"),
            ]
        )
        form = forms.OrderForm(formdata=formdata)
        margherita = db_session.query(models.Pizza).filter_by(name="margherita").one()
        mushrooms = db_session.query(models.Topping).filter_by(name="mushrooms").one()

        form.validate()
        order = form.create_obj(db_session)

        assert len(order.items) == 2
        item = order.items[0]
        assert item.pizza is margherita
        item = order.items[1]
        assert item.pizza is margherita
        assert item.topping is mushrooms

    def test_orders_two_pizzas_with_toppings(self, db_session):
        formdata = MultiDict(
            [
                ("forms-0-name", "margherita"),
                ("forms-0-selected", True),
                ("forms-0-toppings-toppings", "mushrooms"),
                ("forms-1-name", "funghi"),
                ("forms-1-selected", True),
                ("forms-1-toppings-toppings", "scamorza"),
            ]
        )
        form = forms.OrderForm(formdata=formdata)
        margherita = db_session.query(models.Pizza).filter_by(name="margherita").one()
        funghi = db_session.query(models.Pizza).filter_by(name="funghi").one()
        mushrooms = db_session.query(models.Topping).filter_by(name="mushrooms").one()
        scamorza = db_session.query(models.Topping).filter_by(name="scamorza").one()

        form.validate()
        order = form.create_obj(db_session)

        assert len(order.items) == 4
        item = order.items[0]
        assert item.pizza is margherita
        item = order.items[1]
        assert item.pizza is margherita
        assert item.topping is mushrooms
        item = order.items[2]
        assert item.pizza is funghi
        item = order.items[3]
        assert item.pizza is funghi
        assert item.topping is scamorza


@pytest.mark.usefixtures("add_pizzas")
class TestPizzaForm:
    def test_returns_pizza_without_toppings(self, db_session):
        formdata = MultiDict(
            [("name", "margherita"), ("selected", True), ("toppings", [])]
        )
        form = forms.PizzaForm(formdata=formdata)
        margherita = db_session.query(models.Pizza).filter_by(name="margherita").one()

        form.validate()
        items = form.create_obj(db_session)
        item = items[0]

        assert item.pizza is margherita
        assert not item.topping

    def test_returns_pizza_with_toppings(self, db_session):
        formdata = MultiDict(
            [
                ("name", "margherita"),
                ("selected", True),
                ("toppings-toppings", "mushrooms"),
                ("toppings-toppings", "scamorza"),
            ]
        )
        form = forms.PizzaForm(formdata=formdata)
        margherita = db_session.query(models.Pizza).filter_by(name="margherita").one()

        form.validate()
        items = form.create_obj(db_session)

        assert all(i.pizza is margherita for i in items)
        assert not items[0].topping
        assert items[1].topping.name == "mushrooms"
        assert items[2].topping.name == "scamorza"

    def test_returns_empty_items_for_unselected(self, db_session):
        formdata = MultiDict(
            [("name", "margherita"), ("selected", False), ("toppings", [])]
        )
        form = forms.PizzaForm(formdata=formdata)

        form.validate()
        items = form.create_obj(db_session)
        assert not items

    def test_raises_if_toppings_but_no_pizza_selected(self, db_session):
        formdata = MultiDict(
            [
                ("name", "margherita"),
                ("selected", False),
                ("toppings-toppings", "mushrooms"),
            ]
        )
        form = forms.PizzaForm(formdata=formdata)

        assert not form.validate()
        assert form.form_errors == ["You must select a pizza as well as toppings"]

    def test_sets_name_as_readonly(self):
        form = forms.PizzaForm()

        assert form.name.render_kw.get("readonly", False)


@pytest.mark.usefixtures("add_pizzas")
class TestToppingForm:
    def test_returns_one_topping(self, db_session):
        formdata = MultiDict([("toppings", "mushrooms")])
        form = forms.ToppingForm(formdata=formdata)
        mushrooms = db_session.query(models.Topping).filter_by(name="mushrooms").one()

        form.validate()
        toppings = form.create_obj(db_session)
        topping = toppings[0]

        assert topping is mushrooms

    def test_returns_multiple_toppings(self, db_session):
        formdata = MultiDict([("toppings", "mushrooms"), ("toppings", "scamorza")])
        form = forms.ToppingForm(formdata=formdata)
        stored_toppings = (
            db_session.query(models.Topping).order_by(models.Topping.name).all()
        )

        form.validate()
        toppings = form.create_obj(db_session)

        assert toppings == stored_toppings
