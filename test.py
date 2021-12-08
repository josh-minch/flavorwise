import unittest

from parse import (check_ingred, generate_ingred_filters,
                   create_filter_prog,
                   filter_naive, lemmatize)


class TestParse(unittest.TestCase):
    def setUp(self):
        with open('approved_ingreds', 'r', encoding="utf8") as f:
            ingreds = set(f.read().splitlines())
        self.filters = generate_ingred_filters(ingreds)
        self.progs = []
        for ingred_filter in self.filters:
            prog = create_filter_prog(ingred_filter)
            self.progs.append(prog)

    def test_generate_filters(self):
        unsorted_ingreds = {'brown rice', 'apple sauce', 'white rice', 'rice',
                            'brown rice flour', 'sweet rice flour', 'apple',
                            'rice flour', 'beans',
                            'black beans', 'black bean paste',
                            'butter', 'unsalted butter'}

        correct_ingred_filters = [{'butter', 'apple', 'rice', 'beans',
                                   'black bean paste'},
                                  {'unsalted butter',
                                   'brown rice', 'white rice',
                                   'apple sauce',
                                   'rice flour', 'black beans'},
                                  {'brown rice flour', 'sweet rice flour'}]

        ingred_filters = generate_ingred_filters(unsorted_ingreds)

        for i, c in zip(ingred_filters, correct_ingred_filters):
            self.assertCountEqual(i, c)

    def test_check_ingred(self):
        self.assertEqual(check_ingred('apple', self.progs[0]), 'apple')
        self.assertEqual(check_ingred('apples', self.progs[0]), 'apple')
        self.assertEqual(check_ingred(
            'Golden Delicious apples', self.progs[0]), 'apple')
        self.assertEqual(check_ingred('jalapeno', self.progs[0]), 'jalapeño')
        ingred = 'jalapenos, seeded, stemmed and diced'
        self.assertEqual(check_ingred(ingred, self.progs[0]), 'jalapeño')
        self.assertEqual(check_ingred('no ingredients', self.progs[0]), None)

        self.assertEqual(check_ingred(
            'apple sauce', self.progs[1]), 'apple sauce')
        self.assertEqual(check_ingred('apple', self.progs[1]), None)

    def test_filter_naive(self):
        filtered_ingreds = filter_naive([''], self.filters)
        self.assertCountEqual(filtered_ingreds, [])

        filtered_ingreds = filter_naive(
            ['apple', 'apple sauce', 'no ingredients'], self.filters)
        self.assertCountEqual(filtered_ingreds, ['apple sauce', 'apple'])

        filtered_ingreds = filter_naive(
            ['apple', 'apple', 'apple sauce', 'no ingredients'], self.filters)
        self.assertCountEqual(filtered_ingreds, ['apple sauce', 'apple'])

        filtered_ingreds = filter_naive(
            ['jalapenos', 'jalapeño'], self.filters)
        self.assertCountEqual(filtered_ingreds, ['jalapeño'])

        filtered_ingreds = filter_naive(
            ['extra-virgin olive oil', 'mahi-mahi'], self.filters)
        self.assertCountEqual(
            filtered_ingreds, ['extra virgin olive oil', 'mahi mahi'])

        filtered_ingreds = filter_naive(
            ['creamy', 'creamed'], self.filters)
        self.assertCountEqual(filtered_ingreds, [])

    def test_lemmatize(self):
        self.assertEqual(lemmatize('prune'), 'prune')
        self.assertEqual(lemmatize('onions'), 'onion')
        self.assertEqual(lemmatize('apples'), 'apple')
        self.assertEqual(lemmatize('tomatoes'), 'tomato')
        self.assertEqual(lemmatize('anchovies'), 'anchovy')
        self.assertEqual(lemmatize('squashes'), 'squash')

        self.assertEqual(lemmatize('chiles'), 'chile')
        self.assertEqual(lemmatize('chilis'), 'chile')
        self.assertEqual(lemmatize('chilies'), 'chile')
        self.assertEqual(lemmatize('chillies'), 'chile')

        self.assertEqual(lemmatize('white onions'), 'white onion')
        self.assertEqual(lemmatize('acorn squashes'), 'acorn squash')
        self.assertEqual(lemmatize('sweet potatoes'), 'sweet potato')
        self.assertEqual(lemmatize('red chillies'), 'red chile')

        self.assertEqual(lemmatize('bay leaves'), 'bay leaf')
        self.assertEqual(lemmatize('lemongrass'), 'lemongrass')
        self.assertEqual(lemmatize('asparagus'), 'asparagus')

        self.assertEqual(lemmatize('jalapeno'), 'jalapeño')
        self.assertEqual(lemmatize('jalapeño'), 'jalapeño')
        self.assertEqual(lemmatize('jalapenos'), 'jalapeño')

        self.assertEqual(lemmatize('clove of garlic'), 'garlic')
        self.assertEqual(lemmatize('cloves of garlic'), 'garlic')
        self.assertEqual(lemmatize('garlic cloves'), 'garlic')
        self.assertEqual(lemmatize('cloves garlic '), 'garlic')
        self.assertEqual(lemmatize('clove garlic '), 'garlic')
        self.assertEqual(lemmatize('cloves'), 'clove')

        self.assertEqual(lemmatize('szechuan peppercorn'), 'szechuan pepper')
        self.assertEqual(lemmatize('sichuan peppercorn'), 'szechuan pepper')
        self.assertEqual(lemmatize('sichuan pepper'), 'szechuan pepper')
        self.assertEqual(lemmatize('sichuan peppercorns'), 'szechuan pepper')

        self.assertEqual(lemmatize('filo'), 'phyllo')
        self.assertEqual(lemmatize('filo dough'), 'phyllo')
        self.assertEqual(lemmatize('phyllo dough'), 'phyllo')

        self.assertNotEqual(lemmatize('sichuan pepper'), 'pepper')


if __name__ == '__main__':
    unittest.main()
