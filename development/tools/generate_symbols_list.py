#!/usr/bin/python
import sys,string,re,os,os.path

def get_code(code, font):
    if font != "dontknowwhichfontusesthisstrangeencoding":
        return code
    if code < 10:
	return code+161
    elif code < 32:
	return code+163
    else:
	return code

font_names = {}
symbols = {}
xsymbols = {}

ignore_list = ["not", "braceld", "bracerd", "bracelu", "braceru",
	       "lmoustache", "rmoustache", "lgroup", "rgroup", "bracevert"]

def process(file):
    fh = open(file)
    lines = fh.readlines()
    fh.close()
    package, ext = os.path.splitext(os.path.basename(file))
    if ext != ".sty":
        package = ''

    n = len(lines)
    for i in xrange(n):
	line = lines[i]
        mo =  re.match(r'\s*%.*', line)
        if mo != None:
            continue
	next_line = ""
	if i+1 < n:
	    next_line = lines[i+1]

	# some entries are spread over two lines so we join the next line
	# to the current one, (if current line contains a comment, we remove it)
	line = string.split(line,'%')[0]+next_line

	mo =  re.match(r'.*\\DeclareSymbolFont\s*\{(.*?)\}\s*\{(.*?)\}\s*\{(.*?)\}.*', line)
	if mo != None:
	    font_names[mo.group(1)] = mo.group(3)

	mo =  re.match(r'.*\\DeclareMath(Symbol|Delimiter)\s*\{?\\(\w*?)\}?\s*\{?\\(.*?)\}?\s*\{(.*?)\}\s*\{([\'"]?)(.*?)\}.*', line)
        code = -1
        try:
            if mo != None:
                symbol = mo.group(2)
                type = mo.group(3)
                font = mo.group(4)
                if mo.group(5) == '':
                    code = int(mo.group(6))
                elif mo.group(5) == '"':
                    code = int(mo.group(6), 16)
                else:
                    code = int(mo.group(6), 8)
            else:
                mo = re.match(r'.*\\edef\\(\w*?)\{.*?\{\\hexnumber@\\sym(.*?)\}(.*?)\}', line)
                if mo != None:
                    symbol = mo.group(1)
                    type = "mathord"
                    font = mo.group(2)
                    code = int(mo.group(3), 16)
        except ValueError:
                code = -1

	if mo != None and symbol not in ignore_list:
	    mo2 = re.match(r'\s*\\def\\(.*?)\{', next_line)
	    if mo2 != None and symbol == mo2.group(1)+"op":
		sys.stderr.write("%s -> %s\n" % (symbol, mo2.group(1)))
		symbol = mo2.group(1)

	    if font_names.has_key(font):
		font = font_names[font]

	    code = get_code(code, font)
	    if code < 0:
		continue

	    xcode = 0
	    if xsymbols.has_key(symbol):
		xcode = xsymbols[symbol]
		del xsymbols[symbol]

	    if symbols.has_key(symbol):
		sys.stderr.write(symbol+ " exists\n")
		if code != symbols[symbol]:
		    sys.stderr.write("code is not equal!!!\n")
	    else:
		symbols[symbol] = code
		if package == '':
		    print "%-18s %-4s %3d %3d %-6s" % (symbol,font,code,xcode,type)
		else:
		    print "%-18s %-4s %3d %3d %-9s x  %s" % (symbol,font,code,xcode,type,package)


path = os.path.split(sys.argv[0])[0]
fh = open(os.path.join(path, "x-font"))
lines = fh.readlines()
fh.close()
for line in lines:
    x = string.split(line)
    symbol = x[0]
    code = string.atoi(x[1],16)
    xsymbols[symbol] = code

for file in sys.argv[1:]:
    print "# Generated from " + os.path.basename(file) + "\n"
    process(file)
    print

exceptions = [
    ("neq", "x", 0, 185, "mathrel"),
    ("textdegree", "x", 0, 176, "mathord"),
    ("cong", "x", 0, 64, "mathrel"),
    ("surd", "x", 0, 214, "mathord")
]

if xsymbols.has_key("leq"):
    sys.exit(0)

for x in exceptions:
    print "%-18s %-4s %3d %3d %-6s" % x
    if xsymbols.has_key(x[0]):
	del xsymbols[x[0]]

print """
lyxbar             cmsy 161   0 mathord
lyxeq              cmr   61   0 mathord
lyxdabar           msa   57   0 mathord
lyxright           msa   75   0 mathord
lyxleft            msa   76   0 mathord
"""

for symbol in xsymbols.keys():
    sys.stderr.write(symbol+"\n")
