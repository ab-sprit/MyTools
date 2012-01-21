#!/usr/bin/python
# coding: utf-8

import unittest

class Slice:
    def __init__(self,begin,end):
        self.begin = begin
        self.end = end

    def __eq__(self, other):
        return isinstance(other,Slice) and \
                self.begin == other.begin and self.end == other.end

    @staticmethod
    def parse(slice_):
        try:
            if not slice_[0] == "-":
                begin, end = slice_.split('-')
                if begin.isnumeric() and end.isnumeric():
                    return Slice(int(begin),int(end));
        except TypeError or IndexError or ValueError:
            pass
        return None

class CommandLineParams:

    def __init__(self, args):
        self.slices = [];
        self._error = None;
        self._parse(args)

    def _fill_slices(self, args):
        for str_ in args:
            slice_ = Slice.parse(str_)
            if not slice_:
                return args[args.index(str_):]
            else:
                self.slices.append(slice_)

    def _parse( self, args ):
        if not args or len(args) < 4:
            self._error =  "Not enough parameters"
            return
        else:
            self.input_file_name = args[1]
            self.output_file_tmpl = args[2]
            self.extra = self._fill_slices(args[3:]) or []

    def error(self):
        return self._error

    def help(self):
        return
        """
Please, use:
slicevideo.py <input_file> <output_file_template> <slices> <any mencoder arguments>
        """
class SliceTest(unittest.TestCase):
    def test_slice_equal(self):
        self.assertEqual(Slice(1,2), Slice(1,2))

class CommandLineParamsTest(unittest.TestCase):
    def test_parse_input_arguments(self):
        params = CommandLineParams('slicevideo.py test.avi slice-test-{}.avi 0-1213 1521-2992 3286-4601 3286-4601'.split(" "))
        self.assertTrue(params.error() is None);
        self.assertEqual(params.input_file_name, 'test.avi')
        self.assertEqual(params.output_file_tmpl, 'slice-test-{}.avi')
        self.assertEqual(len(params.slices), 4 )
        self.assertEqual(len(params.extra), 0 )
        self.assertEqual([ Slice(0, 1213), Slice(1521, 2992),
            Slice(3286,4601), Slice(3286,4601)], params.slices);

    def test_parse_input_arguments_with_mencoder(self):
        params = CommandLineParams('slicevideo.py in.avi out{}.avi 0-1213 -loadidx idx'.split(" "))
        self.assertTrue(params.error() is None);
        self.assertEqual(params.input_file_name, 'in.avi')
        self.assertEqual(params.output_file_tmpl, 'out{}.avi')
        self.assertEqual(len(params.slices), 1 )
        self.assertEqual([ Slice(0, 1213) ], params.slices);
        self.assertEqual(len(params.extra), 2 )
        self.assertEqual(params.extra, ["-loadidx","idx"] )

def out_filename(template):
	counter = 0
	while True:
		yield template.format(counter)
		counter += 1

import types

class GenericFuncTest(unittest.TestCase):
	def test_out_filename(self):
		gen = out_filename("test{}.avi")
		self.assertTrue( isinstance( gen, types.GeneratorType ))
		self.assertEqual( next(gen), "test0.avi")
		self.assertEqual( next(gen), "test1.avi")



import subprocess

class Mencoder:
	def __init__(self, in_file, out_tmpl, extra):
		self.out_file = out_filename(out_tmpl)
		self.in_file = in_file
		self.extra = self.analyze_extra_params(extra)

	def analyze_extra_params( self, extra):
		if not "-oac" in extra:
			extra += "-oac copy".split()
		if not "-ovc" in extra:
			extra += "-ovc copy".split()
		return extra

	def slice(self, begin, end):
		length = end - begin
		ret = self._call(("mencoder  {} -o {} -ss {} -endpos {}"\
				.format(self.in_file, next(self.out_file),\
					begin, length)).split() \
				+ self.extra), 
		return ret
		
	def _call(self, args):
		return subprocess.call( args )

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

	

# for i in 0 1 2 3; do ss=${el[i*2]}; end=$((${el[i*2+1]} - ${ss})); mencoder tvrec-1.avi -oac copy -ovc copy -o part-${i}.avi -ss $ss -endpos $end; done;
# el=( 0-1213 1521-2992 3286-4601 3286-4601 )
# http://www.mplayerhq.hu/DOCS/HTML/en/menc-feat-x264.html

if __name__ == "__main__":
	unittest.main()

