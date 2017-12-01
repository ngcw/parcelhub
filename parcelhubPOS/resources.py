from import_export import resources
from .models import *

class BranchResource(resources.ModelResource):
    class Meta:
        model = Branch

class UserBranchAccessResource(resources.ModelResource):
    class Meta:
        model = UserBranchAccess
 
        
class CourierVendorResource(resources.ModelResource):
    class Meta:
        model = CourierVendor

class ZoneDomesticResource(resources.ModelResource):
    class Meta:
        model = ZoneDomestic
class ZoneInternationalResource(resources.ModelResource):
    class Meta:
        model = ZoneInternational

class TaxResource(resources.ModelResource):
    class Meta:
        model = Tax
        
class SKUResource(resources.ModelResource):
    class Meta:
        model = SKU 
             
class CustomerResource(resources.ModelResource):
    class Meta:
        model = Customer
    
class SKUBranchResource(resources.ModelResource):
    class Meta:
        model = SKUBranch


