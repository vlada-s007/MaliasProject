from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import QuerySet, Q
from django.urls import reverse


class Category(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название категории')
    slug = models.SlugField(unique=True, verbose_name='Слаг категории')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Родитель (если подкатегория)',
                               related_name='subcategories', null=True, blank=True)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug':self.slug})

    @property
    def get_products(self):
        if self.products:
            return self.products.all()

    @property
    def get_subcats(self):
        if self.subcategories:
            return self.subcategories.all()


    def get_sub_products(self):
        category = Category.objects.get(slug=self.slug)
        subcats = list(category.get_subcats)
        products = self.get_products
        if subcats:
            for subcat in subcats:
                if subcat.get_subcats:
                    for subsubcat in subcat.get_subcats:
                        subcats.append(subsubcat)
            products = Product.objects.filter(category__in=subcats).distinct()
        return products

    def get_all_subcats(self):
        category = Category.objects.get(slug=self.slug)
        subcats = list(category.get_subcats())
        if subcats:
            for subcat in subcats:
                if subcat.get_subcats():
                    for subsubcat in subcat.get_subcats():
                        subcats.append(subsubcat)
        return subcats

    def get_category_brands(self):
        products = self.get_sub_products()
        brands = []
        for product in products:
            if product.brand:
                brands.append(product.brand)
        return set(brands)

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'


class ModelProduct(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название модели')
    slug = models.SlugField(unique=True, verbose_name='Слаг модели')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели товаров'

    def get_absolute_url(self):
        return reverse('compare', kwargs={'slug':self.slug})


class BrandsAndCompanies(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название компании или производителя')
    slug = models.SlugField(unique=True, verbose_name='Слаг компании')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Производителя'
        verbose_name_plural = 'Производители'

    def get_absolute_url(self):
        return reverse('brand', kwargs={'slug':self.slug})


class Color(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название цвета')
    slug = models.SlugField(unique=True, verbose_name='Слаг цвета')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг товара')
    category = models.ManyToManyField(Category, verbose_name='Категория', related_name='products')
    description = models.TextField(verbose_name='Описание товара', null=True, blank=True)
    price = models.IntegerField(default=100, verbose_name='Цена товара')
    discount = models.IntegerField(default=0, verbose_name='Скидка на товар')
    model = models.ForeignKey(ModelProduct, on_delete=models.CASCADE, verbose_name='Модель товара')
    brand = models.ForeignKey(BrandsAndCompanies, on_delete=models.CASCADE, verbose_name='Компания-производитель',
                              related_name='brand_products')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, verbose_name='Цвет',
                              related_name='color_products', null=True)
    version = models.ForeignKey('ProductVersion', on_delete=models.CASCADE, verbose_name='Версия', null=True, blank=True, related_name='product_version')
    quantity = models.IntegerField(default=15, verbose_name='Количество')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    bestseller_status = models.BooleanField(default=False, verbose_name='Бестселлер?')
    new_status = models.BooleanField(default=True, verbose_name='Новинка?')
    discount_end_date = models.DateTimeField(auto_now_add=False, null=True, blank=True, verbose_name='Дата окончания скидки')

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug':self.slug})

    def __str__(self):
        return self.title

    def get_price(self):
        if self.discount:
            return self.price - (self.price // 100 * self.discount)
        else:
            return self.price

    def get_first_image(self):
        if self.images:
            try:
                image = self.images.first().image.url
            except:
                image = ''
            return image
        else:
            return ''

    def get_last_image(self):
        if self.images:
            try:
                image = self.images.last().image.url
            except:
                image = ''
            return image
        else:
            return ''

    def get_average_rating(self):
        avg_rating = 5
        if self.reviews.all():
            ratings = [int(review.rating) for review in self.reviews.all()]
            avg_rating = sum(ratings) / (len(ratings))
        return avg_rating

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class ImagesProduct(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт', related_name='images')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f'Фото товара {self.product.title}'

    class Meta:
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товаров'


# Модель SpecsProduct отвечает за характеристики. Данная модель
# носит информационный характер и служит дополнением к описанию

class SpecsProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='specs')
    specTitle = models.CharField(max_length=100, verbose_name='Параметр', default='RAM')
    specDef = models.CharField(max_length=200, verbose_name='Значение', default='64 GB')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')


    def __str__(self):
        return f'{self.product.title} - {self.specTitle}: {self.specDef}'

    class Meta:
        verbose_name = 'Характеристику товара'
        verbose_name_plural = 'Характеристики товаров'


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название поста')
    author = models.ForeignKey(User, verbose_name='Автор поста', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Содержание поста')
    image = models.ImageField(upload_to='posts/', verbose_name='Изображение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return f'Пост {self.title} автора {self.author.username}'

    class Meta:
        verbose_name = 'Посты'
        verbose_name_plural = 'Посты администраторов'

    def post_image(self):
        if self.image:
            return self.image.url


class ProductVersion(models.Model):


    title = models.CharField(max_length=200,
                             verbose_name='Версия продукта',
        default='128 GB')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')


    def __str__(self):
        return f'Версия {self.title}'

    class Meta:
        verbose_name = 'Версии товаров'
        verbose_name_plural = 'Версии товаров'


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f'Товар {self.product.title} пользователя {self.user.username}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='customer')
    phone = models.CharField(max_length=30, verbose_name='Номер телефона')
    region = models.ForeignKey('Region', null=True, blank=True, on_delete=models.CASCADE, verbose_name='Регион')
    city = models.ForeignKey('City', null=True, blank=True, on_delete=models.CASCADE, verbose_name='Город')
    street = models.CharField(max_length=150, verbose_name='Улица', null=True, blank=True)
    home = models.CharField(max_length=150, verbose_name='Дом', null=True, blank=True)
    flat = models.CharField(max_length=150, verbose_name='Квартира', null=True, blank=True)
    fax = models.CharField(max_length=150, verbose_name='Факс', null=True, blank=True)
    note = models.CharField(max_length=150, verbose_name='Дополнительная информация', null=True, blank=True)
    postal_code = models.CharField(max_length=150, verbose_name='Почтовый код', null=True, blank=True)
    company = models.CharField(max_length=150, verbose_name='Компания', null=True, blank=True)
    newsletter = models.BooleanField(default=False, verbose_name='Подписан(а) на рассылку?')


    def __str__(self):
        return f'Покупатель {self.user.first_name} {self.user.last_name}'

    class Meta:
        verbose_name = 'Покупателя'
        verbose_name_plural = 'Покупатели'


class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, verbose_name='Покупатель', related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    voucher = models.IntegerField(default=0, verbose_name='Ваучер')
    coupon_discount = models.IntegerField(default=0, verbose_name='Скидка с купона')
    delivery_est = models.IntegerField(default=0, null=True, blank=True, verbose_name='Примерная цена доставки')



    def __str__(self):
        return f'Корзина покупателя {self.customer.user.username} на сумму {self.cart_price}$'

    @property
    def cart_price(self):
        price = self.subtotal_cart_price
        if self.coupon_discount:
            price = price - (price // 100 * self.coupon_discount)
        if self.voucher:
            price = price - self.voucher
        return price

    @property
    def subtotal_cart_price(self):
        products = self.products.all()
        price = sum([i.get_total_price for i in products])
        return price


    @property
    def product_cart_quantity(self):
        products = self.products.all()
        quantity = sum([i.quantity for i in products])
        return quantity


    class Meta:
        verbose_name = 'Корзину'
        verbose_name_plural = 'Корзины покупателей'


class CartItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='Корзина', related_name='products')
    gift = models.BooleanField(default=False, null=True, blank=True, verbose_name='Подарочная упаковка для товара')
    quantity = models.IntegerField(default=0, verbose_name='В количестве')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return f'Товар {self.product.title} корзины пользователя {self.cart.customer.user.username} в количестве {self.quantity}'

    class Meta:
        verbose_name = 'Товар корзины'
        verbose_name_plural = 'Товары корзин'

    @property
    def get_total_price(self):
        product_price = self.product.get_price()
        if self.gift:
            product_price += 20
        return product_price * self.quantity


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название региона')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы доставок'


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название города')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион города', related_name='cities')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города доставок'


class Order(models.Model):
    delivery = models.OneToOneField('Delivery', on_delete=models.CASCADE, verbose_name='Доставка', null=True, related_name='order')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Покупатель', related_name='orders')
    price = models.IntegerField(default=0, verbose_name='Сумма заказа')
    subtotal = models.IntegerField(default=0, verbose_name='Сумма заказа (без учета доставки и скидок) ')
    voucher = models.IntegerField(default=0, verbose_name='Ваучер')
    coupon_discount = models.IntegerField(default=0, verbose_name='Скидка с купона')
    delivery_cost = models.IntegerField(default=0, verbose_name='Цена доставки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения заказа')
    completed = models.BooleanField(default=False, verbose_name='Статус заказа')

    @property
    def get_total_price(self):
        price = self.customer.cart.cart_price
        delivery_cost = self.delivery_cost
        if delivery_cost and self.price < 500:
            price += delivery_cost
        return price

    @property
    def get_order_product_slugs(self):
        slugs = []
        if self.completed is True:
            slugs = [str(item.slug) for item in self.products.all()]
        return slugs

    def __str__(self):
        return f'Заказ №: {self.pk} покупателя {self.customer.user} на сумму {self.price}$'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы покупателей'

class OrderProducts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ', related_name='products')
    title = models.CharField(max_length=150, verbose_name='Название товара')
    slug = models.CharField(max_length=150, verbose_name='Слаг товара')
    model = models.CharField(max_length=150, verbose_name='Модель товара', null=True, blank=True)
    version = models.CharField(max_length=150, verbose_name='Версия товара', null=True, blank=True)
    quantity = models.IntegerField(default=0, verbose_name='В количестве')
    price = models.IntegerField(default=0, verbose_name='Цена товара')
    total_price = models.IntegerField(default=0, verbose_name='На сумму')
    image = models.ImageField(upload_to='products/', verbose_name='Фото')

    def __str__(self):
        return f'Товар {self.title} заказа #{self.order.pk} в количестве {self.quantity} на сумму {self.total_price}$'

    def get_image(self):
        if self.image:
            return self.image
        else:
            return ''


    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'

class Delivery(models.Model):

    BOOL_CHOICES = ((True, 'Online payment'), (False, 'Cash (In person)'))
    BOOL_CHOICES2 = ((True, 'Door-to-door delivery'), (False, 'Self-pickup/Post Office delivery'))

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Покупатель')
    phone = models.CharField(max_length=30, verbose_name='Номер получателя')
    comment_delivery = models.CharField(max_length=300, verbose_name='Комментарий к заказу', null=True, blank=True)
    comment_payment = models.CharField(max_length=300, verbose_name='Комментарий к заказу', null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    street = models.CharField(max_length=150, verbose_name='Улица', null=True, blank=True)
    home = models.CharField(max_length=150, verbose_name='Дом/Корпус', null=True, blank=True)
    flat = models.CharField(max_length=150, verbose_name='Номер квартиры', null=True, blank=True)
    postal_code = models.CharField(max_length=150, verbose_name='Почтовый код', null=True, blank=True)
    company = models.CharField(max_length=150, verbose_name='Компания', null=True, blank=True)
    fax = models.CharField(max_length=150, verbose_name='Факс', null=True, blank=True)
    online_payment = models.BooleanField(choices=BOOL_CHOICES, default=True, verbose_name='Оплата онлайн?')
    door_to_door = models.BooleanField(choices=BOOL_CHOICES2, default=True, verbose_name='Доставка до двери?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оформления доставки')
    status = models.BooleanField(default=False, verbose_name='Статус доставки')

    def __str__(self):
        return f'Доставка покупателя {self.customer.user}'

    class Meta:
        verbose_name = 'Доставку'
        verbose_name_plural = 'Доставки пользователя'

    @property
    def get_delivery_cost(self):
        if self.region.pk == 1:
            if self.city.pk != 1:
                delivery_cost = 10
            else:
                delivery_cost = 5
        if self.customer.cart.cart_price > 500 or self.door_to_door is False:
            delivery_cost = 0
        else:
            delivery_cost = 15
        return delivery_cost


class UserRating(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(default=5, verbose_name='Рейтинг')
    content = models.TextField(verbose_name='Содержание обзора', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return f'Обзор {self.product.title} покупатля {self.customer.user} с оценкой {self.rating}'

    def get_rating_list(self):
        if self.rating:
            rating = {
            }
            for i in range(1, 6):
                if i in range(1, self.rating+1):
                    rating[i]= True
                else:
                    rating[i]=False
            return rating

    class Meta:
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры покупателей'


class Contact(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    phone = models.CharField(max_length=50, verbose_name='Номер телефона')
    email = models.EmailField(max_length=150,verbose_name='E-mail', null=True, blank=True)
    text = models.CharField(max_length=500, verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата запроса')

    def __str__(self):
        return f'Запрос от покупателя {self.name} номер {self.phone} дата {self.created_at}'


    class Meta:
        verbose_name = 'Запросы'
        verbose_name_plural = 'Запросы от покупателей'

