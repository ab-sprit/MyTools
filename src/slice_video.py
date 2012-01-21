#!/usr/bin/python
# coding: utf-8

import subprocess
import sys

class Error(Exception):
    def __init__(self, message):
        self.message = message

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
                if not begin.isnumeric():
                    raise Error("{} is not number('{}')".format(begin,slice_))
                if not end.isnumeric():
                    raise Error("{} is not number('{}')".format(end,slice_))
                if end <= begin:
                    raise Error("the begin pos({}) of slice is more than end pos({})"\
                            .format(begin,end))
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
        try:
            if not args or len(args) < 4:
                self._error =  "Not enough parameters"
                return
            else:
                self.input_file_name = args[1]
                self.output_file_tmpl = args[2]
                self.extra = self._fill_slices(args[3:]) or []
        except Error as e:
            self._error = e.message

    def error(self):
        return self._error

    def help(self):
        return """
Please, use:
slicevideo.py <input_file> <output_file_template> <slices> <any mencoder arguments>
        """

def out_filename(template):
	counter = 0
	while True:
		yield template.format(counter)
		counter += 1


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

def main(argv):
    params = CommandLineParams(argv)
    if params.error():
        print(params.error())
        print(params.help())
        return 1
    mencoder = Mencoder(params.input_file_name, params.output_file_tmpl, params.extra)
    for slice in params.slices:
        mencoder.slice(slice.begin,slice.end)

# http://www.mplayerhq.hu/DOCS/HTML/en/menc-feat-x264.html

if __name__ == "__main__":
    main(sys.argv)

