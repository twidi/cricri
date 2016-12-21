import unittest
from gentest import MultiDict, walk, previous, Path, Newer


class TestWalk(unittest.TestCase):

    simple_graph = {
        'A': ['B'],
        'B': ['C', 'G'],
        'C': ['D', 'E', 'G'],
        'D': ['G'],
        'E': ['F', 'G'],
        'F': ['G'],
        'G': []
    }

    graph_with_loop = {
        'A': ['B'],
        'B': ['C'],
        'C': ['D', 'E'],
        'D': ['B'],
        'E': ['F', 'G'],
        'F': ['D'],
        'G': []
    }

    def test_walk_simple_graph(self):
        paths = walk(self.simple_graph, 'A')
        expected = (
            ('A', 'B', 'C', 'D', 'G'),
            ('A', 'B', 'C', 'E', 'F', 'G'),
            ('A', 'B', 'C', 'E', 'G'),
            ('A', 'B', 'C', 'G'),
            ('A', 'B', 'G'),
        )

        self.assertCountEqual(paths, expected)

    def test_walk_graph_with_1_loop(self):
        paths = walk(self.graph_with_loop, 'A')
        expected = (
            ('A', 'B', 'C', 'D', 'B'),
            ('A', 'B', 'C', 'E', 'F', 'D', 'B'),
            ('A', 'B', 'C', 'E', 'G'),
        )

        self.assertCountEqual(paths, expected)

    def test_walk_graph_with_2_loop(self):
        paths = walk(self.graph_with_loop, 'A', 2)
        expected = (
            ('A', 'B', 'C', 'D', 'B', 'C', 'D', 'B'),
            ('A', 'B', 'C', 'D', 'B', 'C', 'E', 'F', 'D', 'B'),
            ('A', 'B', 'C', 'E', 'F', 'D', 'B', 'C', 'D', 'B'),
            ('A', 'B', 'C', 'E', 'F', 'D', 'B', 'C', 'E', 'F', 'D', 'B'),
            ('A', 'B', 'C', 'E', 'G'),
        )

        self.assertCountEqual(paths, expected)


class TestPrevious(unittest.TestCase):

    def test_decorate_function(self):

        @previous(['A', 'B'])
        def foo():
            ...

        self.assertEqual(foo.previous_steps, ['A', 'B'])


class TestMultiDict(unittest.TestCase):

    def setUp(self):
        self.multidict = MultiDict(dict(input='inputs'))

    def test_add_multi_value(self):
        self.multidict['input'] = 1
        self.multidict['input'] = 2
        self.assertEqual(self.multidict, dict(inputs=[1, 2]))

    def test_add_simple_value(self):
        self.multidict['a'] = 1
        self.multidict['a'] = 2
        self.assertEqual(self.multidict, dict(inputs=[], a=2))


class TestPath(unittest.TestCase):

    def test_call(self):
        p = Path("A", "B")
        self.assertTrue(p(["A", "B"]))
        self.assertTrue(p(["A", "B", "C"]))
        self.assertTrue(p(["Z", "A", "B"]))
        self.assertTrue(p(["Z", "A", "B", "C"]))
        self.assertFalse(p(["A"]))
        self.assertFalse(p(["A", "C"]))
        self.assertFalse(p(["A", "C", "B"]))

    def test_not_call(self):
        p = - Path("A", "B")
        self.assertFalse(p(["A", "B"]))
        self.assertFalse(p(["A", "B", "C"]))
        self.assertFalse(p(["Z", "A", "B"]))
        self.assertFalse(p(["Z", "A", "B", "C"]))
        self.assertTrue(p(["A"]))
        self.assertTrue(p(["A", "C"]))
        self.assertTrue(p(["A", "C", "B"]))

    def test_and_call(self):
        p = Path("A", "B") & Path("C", "D")
        self.assertTrue(p(["A", "B", "C", "D"]))
        self.assertTrue(p(["Z", "A", "B", "M", "C", "D", "N"]))
        self.assertFalse(p(["A", "B"]))
        self.assertFalse(p(["C", "D"]))

    def test_or_call(self):
        p = Path("A", "B") | Path("C", "D")
        self.assertTrue(p(["A", "B", "C", "D"]))
        self.assertTrue(p(["Z", "A", "B", "M", "C", "D", "N"]))
        self.assertTrue(p(["A", "B"]))
        self.assertTrue(p(["C", "D"]))
        self.assertFalse(p(["B", "C"]))


class TestNewer(unittest.TestCase):

    def test_call(self):
        n = Newer("A", "B")
        self.assertTrue(n(["A", "B"]))
        self.assertTrue(n(["A", "Z", "B"]))
        self.assertTrue(n(["B", "A", "Z", "B"]))
        self.assertTrue(n(["X", "B"]))
        self.assertTrue(n(["B"]))
        self.assertFalse(n([]))
        self.assertFalse(n(["A"]))
        self.assertFalse(n(["A", "Z", "B", "J", "A"]))

    def test_not_call(self):
        n = - Newer("A", "B")
        self.assertFalse(n(["A", "B"]))
        self.assertFalse(n(["A", "Z", "B"]))
        self.assertFalse(n(["B", "A", "Z", "B"]))
        self.assertFalse(n(["X", "B"]))
        self.assertFalse(n(["B"]))
        self.assertTrue(n([]))
        self.assertTrue(n(["A"]))
        self.assertTrue(n(["A", "Z", "B", "J", "A"]))

