from .base import Resource

class Tenant(Resource):
    path = 'tenants'
    fields = ['name', 'key']
    related_fields = ['applications', 'directories']
