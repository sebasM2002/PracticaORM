import graphene
from graphene import relay
from db import SessionLocal
from models import Store as storeModel, Employee as employeeModel, Inventory as inventoryModel


class Store(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    class Meta:
        model = storeModel
        interfaces = (relay.Node, )

class Employee(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    class Meta:
        model = employeeModel
        interfaces = (relay.Node,)

class Inventory(graphene.ObjectType):
    id = graphene.ID(required=True)
    flavor = graphene.String()
    store_id = graphene.String()
    employee_id = graphene.String()
    date = graphene.String()
    is_season_flavor = graphene.Boolean()
    quantity = graphene.Int()
    class Meta:
        model = inventoryModel
        interfaces = (relay.Node,)
        
class FlavorInput(graphene.InputObjectType):
    flavor = graphene.String()
    quantity = graphene.Int()
    is_season_flavor = graphene.Boolean()

class StoreInput(graphene.InputObjectType):
    name = graphene.String()
    id = graphene.ID()

class EmployeeInput(graphene.InputObjectType):
    name = graphene.String()
    id = graphene.ID()

class InventoryInput(graphene.InputObjectType):
    store_id = graphene.NonNull(StoreInput)
    employee_id = graphene.NonNull(EmployeeInput)
    flavor = graphene.NonNull(FlavorInput)
    date = graphene.String()
        
class Query(graphene.ObjectType):
    node = relay.Node.Field()
    inventory = graphene.List(Inventory, required=True)
    inventoryByFlavor = graphene.List(Inventory, required=True, flavor=graphene.String(required=True))
    inventoryByStore = graphene.List(Inventory, required=True, Store=graphene.String(required=True))
    inventoryByDate = graphene.List(Inventory, required=True, date=graphene.String(required=True))
    
    def resolve_inventory(self, info):
        session = SessionLocal()
        try:

            inventory_data = session.query(inventoryModel).all()

            inventory_list = [
                Inventory(
                    id=item.id,
                    flavor=item.flavor,
                    store_id=item.store_id,
                    employee_id=item.employee_id,
                    date=item.date,
                    is_season_flavor=item.is_season_flavor,
                    quantity = item.quantity,
                )
                for item in inventory_data
            ]
            return inventory_list
        finally:
            session.close()

    def resolve_inventoryByFlavor(self, info, flavor):
        session = SessionLocal()
        try:
            inventory_data = session.query(inventoryModel).filter(inventoryModel.flavor == flavor).all()
            inventory_list = [
                Inventory(
                    id=item.id,
                    flavor=item.flavor,
                    store_id=item.store_id,
                    employee_id=item.employee_id,
                    date=item.date,
                    is_season_flavor=item.is_season_flavor,
                    quantity = item.quantity,
                )
                for item in inventory_data
            ]
            return inventory_list
        finally:
            session.close()

    def resolve_inventoryByStore(self, info, store):
        session = SessionLocal()
        try:
            inventory_data = session.query(inventoryModel).filter(inventoryModel.store_id == store).all()
            
            inventory_list = [
                Inventory(
                    id=item.id,
                    flavor=item.flavor,
                    store_id=item.store_id,
                    employee_id=item.employee_id,
                    date=item.date,
                    is_season_flavor=item.is_season_flavor,
                    quantity = item.quantity,
                )
                for item in inventory_data
            ]
            return inventory_list
        finally:
            session.close()

    def resolve_inventoryByDate(self, info, date):
        session = SessionLocal()
        try:
            inventory_data = session.query(inventoryModel).filter(inventoryModel.date == date).all()
            
            inventory_list = [
                Inventory(
                    id=item.id,
                    flavor=item.flavor,
                    store_id=item.store_id,
                    employee_id=item.employee_id,
                    date=item.date,
                    is_season_flavor=item.is_season_flavor,
                    quantity = item.quantity,
                )
                for item in inventory_data
            ]
            return inventory_list
        finally:
            session.close()

class Mutation(graphene.ObjectType):
    addInventory = graphene.Field(Inventory, inventory=graphene.Argument(InventoryInput, required=True))
    
    def resolve_addInventory(self, info, inventory):
        try:
            store_data = inventory.store_id.id
            employee_data = inventory.employee_id.id
            flavor_data = inventory.flavor.flavor
            date_data = inventory.date
            season_data = inventory.flavor.is_season_flavor
            quantity_data = inventory.flavor.quantity
            
            session = SessionLocal()

            new_inventory = inventoryModel(
                store_id=store_data,
                employee_id=employee_data,
                flavor=flavor_data,
                date=date_data,
                is_season_flavor = season_data,
                quantity = quantity_data,
            )

            session.add(new_inventory)
            session.commit()

            return new_inventory
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

schema = graphene.Schema(query=Query ,  mutation=Mutation) 