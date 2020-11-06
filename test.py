import unittest

from parse import (check_ingred, create_filter_prog, create_ingred_filters,
                   filter_naive, lemmatize)


class TestScrape(unittest.TestCase):
    def setUp(self):
        self.filters = create_ingred_filters()

        self.g_filter = self.filters['general']
        self.g_prog = create_filter_prog(self.g_filter)

        self.s_filter = self.filters['special']
        self.s_prog = create_filter_prog(self.s_filter)

    def test_check_ingred(self):
        self.assertEqual(check_ingred('apple', self.g_prog), 'apple')
        self.assertEqual(check_ingred('apples', self.g_prog), 'apple')
        self.assertEqual(check_ingred(
            'Golden Delicious apples', self.g_prog), 'apple')

        self.assertEqual(check_ingred(
            'apple sauce', self.s_prog), 'apple sauce')
        self.assertEqual(check_ingred('apple', self.s_prog), None)

        self.assertEqual(check_ingred('no ingredients', self.s_prog), None)

    def test_filter_naive(self):
        filtered_ingreds = filter_naive(
            ['apple', 'apple sauce', 'no ingredients'], self.filters)
        self.assertCountEqual(filtered_ingreds, ['apple sauce', 'apple'])

        filtered_ingreds = filter_naive(
            ['apple', 'apple', 'apple sauce', 'no ingredients'], self.filters)
        self.assertCountEqual(filtered_ingreds, ['apple sauce', 'apple'])

        filtered_ingreds = filter_naive([''], self.filters)
        self.assertCountEqual(filtered_ingreds, [])

    def test_lemmatize(self):
        self.assertEqual(lemmatize('onions'), 'onion')
        self.assertEqual(lemmatize('apples'), 'apple')
        self.assertEqual(lemmatize('tomatoes'), 'tomato')
        self.assertEqual(lemmatize('anchovies'), 'anchovy')

        self.assertEqual(lemmatize('chiles'), 'chile')
        self.assertEqual(lemmatize('chilis'), 'chile')
        self.assertEqual(lemmatize('chilies'), 'chile')
        self.assertEqual(lemmatize('chillies'), 'chile')

        self.assertEqual(lemmatize('white onions'), 'white onion')
        self.assertEqual(lemmatize('green apples'), 'green apple')
        self.assertEqual(lemmatize('red chillies'), 'red chile')




if __name__ == '__main__':
    unittest.main()
