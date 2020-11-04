import unittest

from scrape import check_ingred, create_ingred_filters, create_filter_prog, filter_naive


class TestScrape(unittest.TestCase):
    def setUp(self):
        self.filters = create_ingred_filters()

        self.g_filter = self.filters['general']
        self.g_prog = create_filter_prog(self.g_filter)

        self.s_filter = self.filters['special']
        self.s_prog = create_filter_prog(self.s_filter)

    def test_check_ingred(self):
        self.assertEqual(check_ingred('apple', self.g_prog), 'apple')
        self.assertEqual(check_ingred('apples', self.g_prog), 'apples')
        self.assertEqual(check_ingred('Golden Delicious apples', self.g_prog), 'apples')

        self.assertEqual(check_ingred('apple sauce', self.s_prog), 'apple sauce')
        self.assertEqual(check_ingred('apple', self.s_prog), None)

        self.assertEqual(check_ingred('no ingredients', self.s_prog), None)

    def test_filter_naive(self):
        filtered_ingreds = filter_naive(['apple', 'apple sauce', 'no ingredients'], self.filters)
        self.assertCountEqual(filtered_ingreds, ['apple sauce', 'apple'])

        filtered_ingreds = filter_naive(
            ['apple', 'apple', 'apple sauce', 'no ingredients'], self.filters)
        self.assertCountEqual(filtered_ingreds, ['apple sauce', 'apple'])

        filtered_ingreds = filter_naive([''], self.filters)
        self.assertCountEqual(filtered_ingreds, [])

if __name__ == '__main__':
    unittest.main()
