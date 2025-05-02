from django.db.models.manager import Manager
from django.db.models.query import QuerySet

class InventoryQueryset(QuerySet):
    
    def sr_product(self):
        return self.select_related('product')
    
    def sr_product_brand(self):
        return self.select_related('product__brand')
    
    def sr_product_category(self):
        return self.select_related('product__category')
    
    def sr_product_gender(self):
        return self.select_related('product__gender')
    
    def sr_product_color(self):
        return self.select_related('product__color')
    
    def sr_product_letter_size(self):
        return self.select_related('product__letter_size')
    
    def sr_product_relateds(self):
        return self.sr_product().sr_product_brand().sr_product_category().sr_product_gender().sr_product_color().sr_product_letter_size()
    
    

class InventoryManager(Manager):
    def get_queryset(self):
        return InventoryQueryset(self.model, using=self._db)
    
    def sr_product_relateds(self):
        return self.get_queryset().sr_product_relateds()