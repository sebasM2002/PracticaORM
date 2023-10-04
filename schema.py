import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from db import SessionLocal 
from models import Store as storeModel, Employee as employeeModel, Inventory as inventoryModel

""" class Store(SQLAlchemyObjectType):
    class Meta:
        model = storeModel
        interfaces = (relay.Node, )


class Employee(SQLAlchemyObjectType):
    class Meta:
        model = employeeModel
        interfaces = (relay.Node, )

class Inventory(SQLAlchemyObjectType):
    class Meta:
        model = inventoryModel
        interfaces = (relay.Node, )
        
class Query(graphene.ObjectType):
    node = relay.Node.Field()
     """
     
class Icecream(graphene.ObjectType):
    flavor = graphene.String()
    count = graphene.Int()
    is_season_flavor = graphene.Boolean()

class Store(graphene.ObjectType):
    name = graphene.String()

class Employee(graphene.ObjectType):
    name = graphene.String()
     
class Inventory(graphene.ObjectType):
    store = graphene.Field(Store)
    employee = graphene.Field(Employee)
    icecream = graphene.Field(Icecream)
    date = graphene.String()
# Inventory(out.to_dict())
class IcecreamInput(graphene.InputObjectType):
    flavor = graphene.String()
    count = graphene.Int()
    is_season_flavor = graphene.Boolean()

class StoreInput(graphene.InputObjectType):
    name = graphene.String()

class EmployeeInput(graphene.InputObjectType):
    name = graphene.String()

class InventoryInput(graphene.InputObjectType):
    store = graphene.NonNull(StoreInput)
    employee = graphene.NonNull(EmployeeInput)
    icecream = graphene.NonNull(IcecreamInput)
    date = graphene.String()

class Query(graphene.ObjectType):
    inventory = graphene.List(Inventory, required=True)
    inventoryByFlavor = graphene.List(Inventory, required=True, flavor=graphene.String(required=True))
    inventoryByStore = graphene.List(Inventory, required=True, Store=graphene.String(required=True))
    inventoryByDate = graphene.List(Inventory, required=True, date=graphene.String(required=True))

class Mutation(graphene.ObjectType):
    addInventory = graphene.Field(Inventory, inventory=graphene.Argument(InventoryInput, required=True))

schema = graphene.Schema(query=Query ,  mutation=Mutation)