# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Helper to use duecredit as a "runnable" module with  -m duecredit"""

import sys
from . import due, __version__
from .log import lgr

def usage(outfile):
    executable = sys.argv[0]
    if '__main__.py' in executable:
        # That was -m duecredit way to launch
        executable = "%s -m duecredit" % sys.executable
    outfile.write("""Usage: %s [OPTIONS] <file> [ARGS]

Meta-options:
--help                Display this help then exit.
--version             Output version information then exit.
""" % executable)


def runctx(cmd, globals=None, locals=None):
    if globals is None:
        globals = {}
    if locals is None:
        locals = {}

    try:
        exec(cmd, globals, locals)
    finally:
        # good opportunity to avoid atexit I guess. pass for now
        pass

def main(argv=None):
    import os
    import getopt

    if argv is None:
        argv = sys.argv

    try:
        opts, prog_argv = getopt.getopt(argv[1:], "", ["help", "version"])
        # TODO: support options for whatever we would support ;)
    except getopt.error as msg:
        sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
        sys.stderr.write("Try `%s --help' for more information\n"
                         % sys.argv[0])
        sys.exit(1)


    # and now we need to execute target script "manually"
    # Borrowing up on from trace.py
    for opt, val in opts:
        if opt == "--help":
            usage(sys.stdout)
            sys.exit(0)

        if opt == "--version":
            sys.stdout.write("duecredit %s\n" % __version__)
            sys.exit(0)

    sys.argv = prog_argv
    progname = prog_argv[0]
    sys.path[0] = os.path.split(progname)[0]

    try:
        with open(progname) as fp:
            code = compile(fp.read(), progname, 'exec')
        # try to emulate __main__ namespace as much as possible
        globs = {
            '__file__': progname,
            '__name__': '__main__',
            '__package__': None,
            '__cached__': None,
        }
        # Since used explicitly -- activate the beast
        due.activate(True)
        runctx(code, globs, globs)
        # TODO: see if we could hide our presence from the final tracebacks if execution fails
    except IOError as err:
        lgr.error("Cannot run file %r because: %s" % (sys.argv[0], err))
    except SystemExit:
        pass

if __name__ == '__main__':
    main()