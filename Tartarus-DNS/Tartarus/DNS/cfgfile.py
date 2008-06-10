
from __future__ import with_statement

def parse(filename):
    f = open(filename)
    line = ''
    for pline in f:
        pline = pline.rstrip()

        if len(pline) > 0 and pline[-1]=='\\':
            line += l[:-1]
            continue

        line += pline
        cind = line.find('#')
        if cind >= 0:
            line = line[:cind]

        line = line.strip()

        if len(line) == 0:
            continue

        eq = line.find('=')
        if eq <= 0 or len(line) == eq+1:
            raise ValueError, line

        yield line[:eq], line[eq+1:]
        line = ''

HEADER="""#
# This is configuration file for powerdns server.
#
# It is generated automatically. Note that all your formatting and comments
# will be lost on next regeneration.
#

"""

def gen(filename, pairs):
    with open(filename, 'w') as f:
        f.write(HEADER)
        for p in pairs:
            if len(p[1]) > 0:
                f.write("%s=%s\n" % p)
        f.write("\n## EOF ##\n\n")

