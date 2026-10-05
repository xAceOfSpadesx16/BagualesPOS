from django.test import SimpleTestCase
from BagualesPOS.pagination import StandardResultsSetPagination

class PaginationTestCase(SimpleTestCase):
    def test_pagination_properties(self):
        paginator = StandardResultsSetPagination()
        self.assertEqual(paginator.page_size, 20)
        self.assertEqual(paginator.page_size_query_param, 'limit')
        self.assertEqual(paginator.max_page_size, 100)
