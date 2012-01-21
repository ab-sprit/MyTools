#!/usr/bin/python
# coding: utf-8

from slice_video import *

import unittest
import types

class SliceTest(unittest.TestCase):
    def test_slice_equal(self):
        self.assertEqual(Slice(1,2), Slice(1,2))

class CommandLineParamsTest(unittest.TestCase):
    def test_parse_input_arguments(self):
        params = CommandLineParams('slicevideo.py test.avi slice-test-{}.avi 0-1213 1521-2992 3286-4601'.split(" "))
        self.assertTrue(params.error() is None);
        self.assertEqual(params.input_file_name, 'test.avi')
        self.assertEqual(params.output_file_tmpl, 'slice-test-{}.avi')
        self.assertEqual(len(params.slices), 3 )
        self.assertEqual(len(params.extra), 0 )
        self.assertEqual([ Slice(0, 1213), Slice(1521, 2992),
            Slice(3286,4601)], params.slices);

    @unittest.skip("Not Implemented")
    def test_parse_input_arguments_the_same_slice(self):
        params = CommandLineParams('py in out 3286-4601 3286-4601'.split(" "))
        self.assertTrue(params.error());

    def test_parse_input_arguments_end_less_begin(self):
        params = CommandLineParams('py in out 3286-123'.split(" "))
        self.assertTrue(params.error());

    def test_parse_input_arguments_with_mencoder(self):
        params = CommandLineParams('slicevideo.py in.avi out{}.avi 0-1213 -loadidx idx'.split(" "))
        self.assertTrue(params.error() is None);
        self.assertEqual(params.input_file_name, 'in.avi')
        self.assertEqual(params.output_file_tmpl, 'out{}.avi')
        self.assertEqual(len(params.slices), 1 )
        self.assertEqual([ Slice(0, 1213) ], params.slices);
        self.assertEqual(len(params.extra), 2 )
        self.assertEqual(params.extra, ["-loadidx","idx"] )

class GenericFuncTest(unittest.TestCase):
	def test_out_filename(self):
		gen = out_filename("test{}.avi")
		self.assertTrue( isinstance( gen, types.GeneratorType ))
		self.assertEqual( next(gen), "test0.avi")
		self.assertEqual( next(gen), "test1.avi")

called=[]

class MencoderTest( unittest.TestCase ):

	def test_run_mencoder(self):
		mencoder = Mencoder("t.in", "t{}.out", "-loadidx idx".split())
		def fake(args):
			global called
			called = args
			return 0
		mencoder._call = fake
		ret = mencoder.slice(0, 123)
		self.assertEqual(called,"mencoder t.in -o t0.out -ss 0 -endpos 123 -loadidx idx -oac copy -ovc copy".split())


if __name__ == "__main__":
	unittest.main()

