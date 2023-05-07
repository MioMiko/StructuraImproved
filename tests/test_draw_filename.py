import re
import sys
import unittest

sys.path.append("../structura")
from api import Structura

draw_packname = Structura.draw_packname


class Test(unittest.TestCase):
    def test_1(self):
        file_name = "test.mcstructure"
        self.assertEqual(draw_packname(file_name),"test")
        file_name = "/ksbsb/ksjsb/test.mcstructure"
        self.assertEqual(draw_packname(file_name),"test")
        file_name = "a/test.mcstructure"
        self.assertEqual(draw_packname(file_name),"test")
        file_name = "/test.mcstructure"
        self.assertEqual(draw_packname(file_name),"test")
        file_name = "keh\\kdn\\test.mcstructure"
        self.assertEqual(draw_packname(file_name),"test")
        file_name = "\\test.mcstructure"
        self.assertEqual(draw_packname(file_name),"test")
        file_name = "/mystructure_test.mcstructure"
        self.assertEqual(draw_packname(file_name),"test")
        file_name = "mystructure_test.mcstructure"
        self.assertEqual(draw_packname(file_name),"test")
        file_name = "a.mcstructure"
        self.assertEqual(draw_packname(file_name),"a")
        file_name = "/a.mcstructure"
        self.assertEqual(draw_packname(file_name),"a")
        file_name = "owhsh/a.mcstructure"
        self.assertEqual(draw_packname(file_name),"a")
        file_name = ".mcstructure"
        self.assertEqual(draw_packname(file_name),"")
        file_name = "kejhw/.mcstructure"
        self.assertEqual(draw_packname(file_name),"")
        file_name = "/sdcard/Download/Structura-main/test_structures/BigHatter/1.mcstructure"
        self.assertEqual(draw_packname(file_name),"1")
