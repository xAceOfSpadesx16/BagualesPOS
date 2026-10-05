from django.test import TestCase
from sales.serializers import SaleSerializer

class RecordsSerializerTestCase(TestCase):
    def test_serializer_import(self):
        # Verify that we can import SaleSerializer from records.serializers
        from records.serializers import SaleSerializer as RecordsSaleSerializer
        self.assertIs(RecordsSaleSerializer, SaleSerializer)
