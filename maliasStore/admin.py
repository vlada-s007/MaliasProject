from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *

# Register your models here.

admin.site.register(ProductVersion)
admin.site.register(Post)


admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(CartItems)

admin.site.register(Customer)
admin.site.register(OrderProducts)
admin.site.register(Region)
admin.site.register(City)
admin.site.register(Delivery)
admin.site.register(UserRating)
admin.site.register(Contact)


@admin.register(ModelProduct)
class ModelProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

@admin.register(BrandsAndCompanies)
class CompanyProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Color)
class ColorProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ImagesProduct)
class ImagesProductAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'get_image')

    def get_title(self, obj):
        return f'{obj.product.title}'


    def get_image(self, obj):
        if obj.image:
            try:
                return mark_safe(f'<img src="{obj.image.url}" width="100">')
            except:
                return 'none'
        else:
            return 'none'
    get_image.short_description = 'Картинка'
    get_title.short_description = 'Товар'

class ImagesProductInline(admin.TabularInline):
    fk_name = 'product'
    model = ImagesProduct
    extra = 1

class SpecsInline(admin.TabularInline):
    fk_name = 'product'
    model = SpecsProduct
    extra = 1

@admin.register(SpecsProduct)
class SpecsProductAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'specTitle', 'specDef')

    def get_title(self, obj):
        return f'{obj.product.title}'
    save_as = True
    save_as_continue = True
    save_on_top = True
    get_title.short_description = 'Товар'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'brand', 'model', 'version', 'price', 'discount', 'quantity',
                    'get_image', 'created_at', 'bestseller_status', 'new_status', 'discount_end_date']
    list_editable = ['price', 'discount', 'discount_end_date', 'bestseller_status', 'quantity', 'new_status']
    inlines = [SpecsInline, ImagesProductInline]
    list_filter = ('price', 'model', 'version')
    save_as = True
    save_as_continue = True
    save_on_top = True

    def get_image(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.first().image.url}" width="75">')
            except:
                return 'none'
        else:
            return 'none'
    get_image.short_description = 'Картинка'




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'parent', 'slug')

class OrderProductsInline(admin.TabularInline):
    fk_name = 'order'
    model = OrderProducts
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'customer', 'completed',]
    list_editable = ('completed',)
    inlines = [OrderProductsInline]


