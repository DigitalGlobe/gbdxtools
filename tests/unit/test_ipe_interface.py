"""
Unit tests for the gbdxtools.ipe.interface module
"""

import unittest

from gbdxtools.ipe.interface import Ipe, Op, ContentHashedDict

class IpeInterfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ipe = Ipe()

    def test_content_hashed_dict(self):
        a = {"one": 1, "two": 2, "three": 3}
        b = {"one": 1, "two": 2, "three": 4}

        try:
            ca = ContentHashedDict(a)
            self.assertTrue(hasattr(ca, "_id"))
        except Exception as e:
            self.fail("Exception while instantiating ContentHashedDict: {}".format(e))

        dup = ContentHashedDict(a)
        self.assertEqual(a, dup)
        self.assertNotEqual(id(a), id(dup))
        self.assertEqual(ca._id, dup._id)

        alt = ContentHashedDict(b)

        self.assertNotEqual(ca, alt)

        ca["three"] = 4
        self.assertEqual(ca._id, alt._id)

        self.assertNotIn("id", ca)
        ca.populate_id()
        self.assertIn("id", ca)

    def test_ipe_produces_ops(self):
        op = self.ipe.TestOperator(param1="one", param2="two")
        self.assertIsInstance(op, Op)
        self.assertEqual(op._operator, "TestOperator")

        self.assertEqual(len(op._nodes), 1)
        self.assertEqual(len(op._edges), 0)
