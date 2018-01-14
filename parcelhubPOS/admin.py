from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


admin.site.register(UserExtend)
@admin.register(Branch)
class BranchAdmin(ImportExportModelAdmin):
    pass
admin.site.register(UserBranchAccess)
@admin.register(CourierVendor)
class CourierVendorAdmin(ImportExportModelAdmin):
    pass
@admin.register(ZoneDomestic)
class ZoneDomesticAdmin(ImportExportModelAdmin):
    pass
@admin.register(ZoneInternational)
class ZoneInternationalAdmin(ImportExportModelAdmin):
    pass
@admin.register(Tax)
class TaxAdmin(ImportExportModelAdmin):
    pass
@admin.register(SKU)
class SKUAdmin(ImportExportModelAdmin):
    class Meta:
        def get_or_init_instance(instance_loader, row):
            try:
                sku = SKU.objects.get(sku_code=row['sku_code'])
                return sku
            except ObjectDoesNotExist:
                return None
    pass
@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    pass
@admin.register(SKUBranch)
class SKUBranchAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(PaymentType)
admin.site.register(Payment)
admin.site.register(PaymentInvoice)
admin.site.register(VendorReport)
admin.site.register(CashUpReport)
admin.site.register(AccountReport)
admin.site.register(StatementOfAccount)
admin.site.register(StatementOfAccountInvoice)
admin.site.register(ZoneType)
admin.site.register(ProductType)
admin.site.register(CustomerType)
admin.site.register(InvoiceType)
admin.site.register(GlobalParameter)