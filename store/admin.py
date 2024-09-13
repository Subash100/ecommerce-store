
from django.contrib import admin,messages
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.contenttypes.admin import GenericTabularInline

from tags.models import TaggedItem
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
            ('>10', 'High'),

        ]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        if self.value() == '>10':
            return queryset.filter(inventory__gt=10)




@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    search_fields = ['title']
    prepopulated_fields = {'slug': ['title']}
    actions=['clear_inventory']
    list_display = ('title', 'unit_price','inventory_status','collection')
    list_editable = ('unit_price',)
    list_per_page = 10
    list_select_related = ('collection',)
    list_filter = ('collection', 'last_update', InventoryFilter)

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description='clear inventory')
    def clear_inventory(self, request, queryset):
        update_count= queryset.update(inventory=0)
        self.message_user(request,f"Cleared {update_count} products ",messages.ERROR)

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'membership')
    list_editable = ('membership',)
    ordering = ['first_name', 'last_name']
    list_per_page = 10
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    extra = 0
    min_num = 1
    max_num = 10
    model = models.OrderItem

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'placed_at', 'customer')
    inlines = [OrderItemInline]
    list_select_related = ('customer',)
    autocomplete_fields = ['customer']


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'products_count')
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = reverse('admin:store_product_changelist')+'?'+'collection__id__exact=%d' % collection.id
        return format_html('<a href={}>{}</a>',url,collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('product'))
