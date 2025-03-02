from __future__ import annotations
from typing import TYPE_CHECKING
from django.db.models import Manager, QuerySet
from django.utils.timezone import now

if TYPE_CHECKING:
    from users.models import CustomUser

class SalesQueryset(QuerySet):
    def soft_delete(self):
        return self.update(is_deleted=True, deleted_at=now())
    
    def select_rel_seller(self):
        return self.select_related('seller')
    
    def select_rel_client(self):
        return self.select_related('client')
    
    def prefetch_details_products(self):
        return self.prefetch_related('details__product')

    def get_own_actives(self, seller: CustomUser):
        return self.filter(canceled=False, closed=False, seller = seller)
    

class SalesManager(Manager):

    def get_queryset(self):
        return SalesQueryset(self.model, using=self._db)

    def get_table_active_sale(self, seller: CustomUser):
        return self.get_queryset().prefetch_details_products().get_own_actives(seller).first()
    
    def fetch_details(self):
        return self.get_queryset().prefetch_details_products()


