# """
# Unit tests for the gbdxtools.rda.interface module
# """
#
# import unittest
# import types
#
# from gbdxtools import Interface
# from gbdxtools.rda.interface import RDA, Op
#
# from auth_mock import get_mock_gbdx_session
#
# class RdaInterfaceTest(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.rda = RDA()
#         mock_gbdx_session = get_mock_gbdx_session(token='dummytoken')
#         cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
#
#     def test_content_hashed_dict(self):
#         a = {"one": 1, "two": 2, "three": 3}
#         b = {"one": 1, "two": 2, "three": 4}
#
#         try:
#             ca = ContentHashedDict(a)
#             self.assertTrue(hasattr(ca, "_id"))
#         except Exception as e:
#             self.fail("Exception while instantiating ContentHashedDict: {}".format(e))
#
#         dup = ContentHashedDict(a)
#         self.assertEqual(a, dup)
#         self.assertNotEqual(id(a), id(dup))
#         self.assertEqual(ca._id, dup._id)
#
#         alt = ContentHashedDict(b)
#
#         self.assertNotEqual(ca, alt)
#
#         ca["three"] = 4
#         self.assertEqual(ca._id, alt._id)
#
#         self.assertNotIn("id", ca)
#         ca.populate_id()
#         self.assertIn("id", ca)
#
#     def test_rda_produces_ops(self):
#         op = Op("TestOperator")(param1="one", param2="two")
#         self.assertIsInstance(op, Op)
#         self.assertEqual(op._operator, "TestOperator")
#
#         self.assertEqual(len(op._nodes), 1)
#         self.assertEqual(len(op._edges), 0)
#
#         g = op.graph(conn=None)
#         self.assertIn("edges", g)
#         self.assertIn("nodes", g)
#         self.assertEqual(len(g["nodes"]), 1)
#         self.assertEqual(len(g["edges"]), 0)
