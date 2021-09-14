"""
Python script for comparing benchmark results of different optimization levels
available on meson.

Examples
========

1. $ python run_bench.py
    Runs all benchmark tests
2. $ python run_bench.py optimize_linprog.KleeMinty
    Runs only "optimize_linprog.KleeMinty" benchmark test
"""

from argparse import ArgumentParser, REMAINDER
import subprocess
import time
import os
import sys


if __doc__ is None:
    __doc__ = "Run without -OO if you want usage info"
else:
    __doc__ = __doc__.format(**globals())

PATH_INSTALLED = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                   'installdir')
PY_PATH = os.path.join(PATH_INSTALLED, "lib/python3.9/site-packages/")
CUR_DIR = sys.path[0]
sys.path.pop(0)

OPTIMIZE_LEVELS = ["0" ]#"1"] # "2", "3", "g", "s"]

env = dict(os.environ)
env['OPENBLAS_NUM_THREADS'] = '1'
env['MKL_NUM_THREADS'] = '1'

def main(argv):
    """
    Builds, runs the benchmark tests and compares the result of different
    optimization levels using meson
    """
    parser = ArgumentParser(usage=__doc__.lstrip())
    parser.add_argument("args", metavar="ARGS", default=[], nargs=REMAINDER,
                        help="Arguments to pass to Nose, Python or shell")
    args = parser.parse_args(argv)
    items = args.args[:]
    default = "optimize_linprog.KleeMinty"
    env['PYTHONPATH'] = PY_PATH
    os.environ['PYTHONPATH'] = PY_PATH
    bench_args = []
    # if not items:
    #      items = [default]
    for a in items:
        bench_args.extend(['--bench', a])
    cmd = ['asv', 'run', '--python=same', '--steps=1'] + bench_args
    build_time = []
    benchmark_time = []
    install_dir_size = []

    for optimization_level in OPTIMIZE_LEVELS:
        sys.path.insert(0, CUR_DIR)
        start = time.time()
        build_scipy(optimization_level)
        end = time.time()
        sys.path.pop(0)
        build_time.append(end - start)
        install_dir_size.append(get_size())
        sys.path.insert(0, PY_PATH)
        start = time.time()
        retval = run_asv(cmd)
        end = time.time()
        sys.path.pop(0)
        if retval:
            print("Error while running benchmarks for optimization level: %s"
                % (optimization_level))
            sys.exit(retval)
        benchmark_time.append(end - start)

    print("*"*80)
    print("-"*35, "Results", "-"*36)
    print("*"*80)
    print("Optimization Level \tBuild Time \t      Benchmarks Time \t\t Size \t")
    for op in range(len(OPTIMIZE_LEVELS)):
        print(OPTIMIZE_LEVELS[op], build_time[op], benchmark_time[op],
                install_dir_size[op], sep="\t\t")


def build_scipy(optimization_level):
    """
    Building SciPy using meson build

    Parameters
    ==========

    optimization_level: str
        Optimization level to be used while setting up meson build
    """
    print("Building scipy with optimization level: %s" % (optimization_level))
    cmd = ["rm", "-rf", "build"]
    ret = subprocess.call(cmd)
    cmd = ["meson", "setup", "--optimization", optimization_level,
            "build", "--prefix", PATH_INSTALLED]
    ret = subprocess.call(cmd)
    if ret != 0:
        print("Meson build failed")
        raise
    cmd = ["ninja", "-C", "build" , "-j", "2"]
    ret = subprocess.call(cmd)
    if ret != 0:
        print("ninja build failed")
        raise
    cmd = ["meson", "install", "-C", "build"]
    subprocess.call(cmd)
    if ret != 0:
        print("Meson installation failed")
        raise

def run_asv(cmd):
    """
    Running the benchmark tests using asv
    """

    import scipy
    print("Running benchmarks for Scipy version %s at %s"
          % (scipy.__version__, scipy.__file__))
    cwd = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       'benchmarks')
    sys.path.insert(0, cwd)
    from benchmarks.common import set_mem_rlimit
    try:
        set_mem_rlimit()
    except (ImportError, RuntimeError):
        pass
    # Run
    try:

        ret = subprocess.call(cmd, env=env, cwd=cwd)
        if ret != 0:
            print("asv run failed")
            raise
        cmd = ["asv", "publish"]
        ret = subprocess.call(cmd, env=env, cwd=cwd)
        if ret != 0:
            print("asv publish failed")
            raise
        sys.path.pop(0)
        return ret
    except OSError as err:
        if err.errno == errno.ENOENT:
            print("Error when running '%s': %s\n" % (" ".join(cmd), str(err),))
            print("You need to install Airspeed Velocity (https://airspeed-velocity.github.io/asv/)")
            print("to run Scipy benchmarks")
            return 1
        raise



def get_size():
    """
    Returns the size of installdir created after the build
    """
    size = subprocess.check_output(['du','-sh', PATH_INSTALLED]).split()[0].decode('utf-8')
    return size

if __name__ == "__main__":
    main(argv=sys.argv[1:])
