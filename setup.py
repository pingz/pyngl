#
# This script builds PyNGL from source. Some environment variables
# may be required. See the following comments. 
#
# This version of PyNGL must be built against NCL V6.1.0 or later.
# Version 6.0.0 or earlier will not work.
#

#
# To install, type:
# 
#  python setup.py install
#
# To build PyNGL from source, you must have the NCL/NCAR Graphics
# software installed on your system.
#
# The NCARG_ROOT environment variable must be set to the root
# directory of where NCL/NCAR Graphics software was installed.
#
# See http://www.ncl.ucar.edu/Download/ for information on 
# installing NCL/NCAR Graphics (available as one package).
#
# Cairo support is no longer optional. You must build cairo and
# related libraries in order to build PyNGL 1.5.0.
# This means you must link against NCL/NCAR Graphics version 6.1.0.
#
# 
# To build against cairo, you must indicate the locations of the cairo,
# freetype, png, and zlib software with the following environment variables:
#
#  PNG_PREFIX
#  ZLIB_PREFIX
#  CAIRO_PREFIX
#  FREETYPE_PREFIX
#
# If any one of these are the same, then you don't need to set all
# of them.
#
# Finally, you may need to include Fortran system libraries (like
# "-lgfortran" or "-lf95") to resolve undefined symbols.
#
# Use F2CLIBS and F2CLIBS_PREFIX for this. For example, if you
# need to include "-lgfortran", and this library resides in /sw/lib:
#
#  F2CLIBS gfortran
#  F2CLIBS_PREFIX /usr/local/lib
#
import os, sys

# Test to make sure we actually have NumPy.
try:
  import numpy
except ImportError:
  print("Error: Cannot import NumPy. Can't continue.")
  sys.exit(1)

PYNGL_NCARG_DIR = "src/ngl/ncarg"
#
# Tests for environment variables.
#
try:
  ncarg_root = os.environ["NCARG_ROOT"]
except:
  print("NCARG_ROOT is not set; can't continue!")
  sys.exit(1)
try:
  ncarg_lib = os.environ["NCARG_LIB"]
except:
  ncarg_lib = os.path.join(ncarg_root,'lib')


# Depending on what Fortran compiler was used to build, we may need
# additional library paths or libraries.
try:
  F2CLIBS = os.environ["F2CLIBS"].split()
except:
  F2CLIBS = ""

try:
  F2CLIBS_PREFIX = os.environ["F2CLIBS_PREFIX"]
except:
  F2CLIBS_PREFIX = ""

try:
  NCLLIBS_PREFIX = os.environ["NCLLIBS_PREFIX"]
except:
  NCLLIBS_PREFIX = ""

try:
  EXTRA_OBJECTS = [os.environ["EXTRA_OBJECTS"]]
except:
  EXTRA_OBJECTS = ""

# Done with environment variables.

import re, platform, fileinput
from distutils.core import setup, Extension
from distutils.util import get_platform
from distutils.sysconfig import get_python_lib

# Create file containing PyNGL and numpy version.
def create_version_file():
  if os.path.exists(pyngl_vfile):
    os.remove(pyngl_vfile)

  vfile = open(pyngl_vfile,'w')
  vfile.write("version = '%s'\n" % pyngl_version)
  vfile.write("array_module = 'numpy'\n")
  vfile.write("array_module_version = '%s'\n" % array_module_version)
  vfile.write("python_version = '%s'\n" % sys.version[:5])
  vfile.close()

# Copy the pynglex script to same filename w/the python version appended.
# Not used for now.
def copy_pynglex_script():
  pynglex_script = os.path.join(pynglex_dir,"pynglex")
  pynglex_v_file = pynglex_script + sys.version[:3]

  os.system("cp " + pynglex_script + " " + pynglex_v_file)

# Modify the pynglex script to have the correct python invocation.
  for line in fileinput.input(pynglex_v_file,inplace=1):
    if (re.search("/usr/bin/env python",line) != None):
      print(line.replace("python","python"+sys.version[:3]))
    elif(re.search("^py_cmd = 'python'",line) != None):
      print(line.replace("python","python"+sys.version[:3]))
    else:
      print(line)

  return [pynglex_script, pynglex_v_file]

# Copy list of pynglex examples and resource files.
def get_pynglex_files():
  all_pynglex_files = os.listdir(pynglex_dir)

  if not os.path.exists(PYNGL_NCARG_DIR):
    os.mkdir(PYNGL_NCARG_DIR)

  dir_to_copy_to = os.path.join(PYNGL_NCARG_DIR,'pynglex')
  if not os.path.exists(dir_to_copy_to):
    os.mkdir(dir_to_copy_to)

  for file in all_pynglex_files:
    if (file[-3:] == ".py" or file[-4:] == ".res"):
      cmd = "cp " + os.path.join(pynglex_dir,file) + " " + dir_to_copy_to
      os.system(cmd)
      DATA_FILES.append(os.path.join(dir_to_copy_to,file))

  return

# Return list of files we need under $NCARG_ROOT/lib/ncarg.
def get_ncarg_files():
  plat_dir = os.path.join("build","lib."+get_platform()+"-"+sys.version[:3], \
                          "PyNGL")

  ncl_lib       = ncarg_lib
  ncl_ncarg_dir = os.path.join(ncl_lib,'ncarg')
  ncarg_dirs    = ["colormaps","data","database","fontcaps","graphcaps"]

  cwd = os.getcwd()          # Retain current directory.
  if not os.path.exists(PYNGL_NCARG_DIR):
    os.mkdir(PYNGL_NCARG_DIR)          # make a directory to copy files to
  os.chdir(ncl_ncarg_dir)    # cd to $NCARG_ROOT/lib/ncarg

# Walk through each directory and copy some data files. Skip over
# the rangs directory.
  for ncarg_dir in ncarg_dirs:
    for root, dirs, files in os.walk(ncarg_dir):
      dir_to_copy_to = os.path.join(cwd,PYNGL_NCARG_DIR,root)
      if not os.path.exists(dir_to_copy_to):
        os.mkdir(dir_to_copy_to)
      for name in files:
        if root != "database/rangs":
          file_to_copy = os.path.join(ncl_ncarg_dir,root,name)
          cmd = "cp " + file_to_copy + " " + dir_to_copy_to
          os.system(cmd)
          DATA_FILES.append(os.path.join('ncarg',root,name))

  os.chdir(cwd)    # cd back to original directory

# Special 'sysresfile'
  os.system("cp data/sysresfile " + PYNGL_NCARG_DIR)
  DATA_FILES.append(os.path.join('ncarg','sysresfile'))

  return

# Return list of libraries and paths needed for compilation
def set_ncl_libs_and_paths():
  PATHS = [ncarg_lib]

  xdir = "/usr/X11R6/lib"
  if(os.path.exists(xdir)):
      PATHS.append(xdir)

  xdir = "/opt/X11/lib"
  if(os.path.exists(xdir)):
      PATHS.append(xdir)

  if (os.uname()[-1] == "x86_64" or os.uname()[-1] == "ia64"):
    dir = '/usr/X11R6/lib64'
    if(os.path.exists(dir)):
      PATHS.append(dir)

# Libraries needed to compile _hlu.so/fplib.so modules.
  LIBS = ["nfpfort", "hlu", "ncarg", "ncarg_gks", "ncarg_c",
          "ngmath", "X11"]

# Add extra library needed for C/Fortran interfacing.
  if sys.platform == "aix5":
    LIBS.append("xlf90")
  elif sys.platform == "sunos5":
      LIBS.append('f77compat')
      LIBS.append('fsu')
      LIBS.append('sunmath')
  elif sys.platform == "darwin":
      LIBS.append('quadmath')

# Add extra libraries for cairo support. You must link
# against a cairo-enabled version of the NCAR Graphics libraries.
#
# If you get some XML undefined references, then you need to
# build the "expat" library and uncomment it below.
#
  LIBS.append('cairo')
  LIBS.append('fontconfig')
  LIBS.append('pixman-1')
  LIBS.append('freetype')
  LIBS.append('expat')
  LIBS.append('pthread')
  LIBS.append('Xrender')
  LIBS.append('Xext')
  LIBS.append('bz2')
  LIBS.append('gfortran')
  try:
    PATHS.append(os.path.join(os.environ["CAIRO_PREFIX"],"lib"))
  except:
    pass
  try:
    PATHS.append(os.path.join(os.environ["FREETYPE_PREFIX"],"lib"))
  except:
    pass

# Add extra libraries for cairo support.
  LIBS.append('png')
  LIBS.append('z')
  try:
    PATHS.append(os.path.join(os.environ["PNG_PREFIX"],"lib"))
  except:
    pass
  try:
    PATHS.append(os.path.join(os.environ["ZLIB_PREFIX"],"lib"))
  except:
    pass

  if F2CLIBS != "":
    for lib in F2CLIBS:
      LIBS.append(lib)

  if F2CLIBS_PREFIX != "":
    PATHS.append(F2CLIBS_PREFIX)

  if NCLLIBS_PREFIX != "":
    PATHS.append(NCLLIBS_PREFIX)

  return LIBS,PATHS

# Return list of include paths needed for compilation
def set_include_paths():
  ncl_inc = os.path.join(ncarg_root,'include')
  PATHS = [ncl_inc]

# Location of numpy's "arrayobject.h".
  PATHS.insert(0,numpy.get_include())

  try:
    PATHS.append(os.path.join(os.environ["PNG_PREFIX"],"include"))
  except:
    pass
  try:
    PATHS.append(os.path.join(os.environ["ZLIB_PREFIX"],"include"))
  except:
    pass

  try:
    PATHS.append(os.path.join(os.environ["CAIRO_PREFIX"],"include"))
  except:
    pass
  try:
    PATHS.append(os.path.join(os.environ["FREETYPE_PREFIX"],"include"))
    PATHS.append(os.path.join(os.environ["FREETYPE_PREFIX"],"include/freetype2"))
  except:
    pass

  PATHS.append("src/gsun")

  return PATHS

#----------------------------------------------------------------------
# Main section
#----------------------------------------------------------------------

long_description = "PyNGL is a Python language module designed for publication-quality visualization and analysis of scientific data. PyNGL stands for 'Python Interface to the NCL Graphics Libraries,' and it is pronounced 'pingle.'"

# I read somewhere that distutils doesn't update this file properly
# when the contents of directories change.

if os.path.exists('MANIFEST'): os.remove('MANIFEST')

PYNGL_PKG_NAME = 'ngl'                    # Name of package to install.
pkgs_pth       = get_python_lib()

# Construct the version file.
from numpy import __version__ as array_module_version

pyngl_vfile   = "src/ngl/version.py"     # Name of version file.
pyngl_version = open('version','r').readlines()[0].strip('\n')
create_version_file()

# Get directories of installed NCL/NCAR Graphics libraries and include
# files

LIBRARIES,LIB_DIRS = set_ncl_libs_and_paths()
INC_DIRS           = set_include_paths()

# Set some compile options.
if os.uname()[-1] == "x86_64" or \
  (os.uname()[-1] == "Power Macintosh" and os.uname()[2] == "7.9.0"):
  os.environ["CFLAGS"] = "-O2"
DMACROS =  [('NeedFuncProto', None)]
os.environ["CFLAGS"] += " -fopenmp "

# Instructions for compiling the "_hlu.so" and "fplib.so" files.
EXT_MODULES = [Extension('_hlu', 
              ['src/Helper.c','src/hlu/hlu_wrap.c','src/gsun/gsun.c'],
                define_macros   = DMACROS,
                include_dirs    = INC_DIRS,
                library_dirs    = LIB_DIRS,
                libraries       = LIBRARIES,
                extra_objects   = EXTRA_OBJECTS),
               Extension('fplib', 
               [os.path.join('src','paft','fplibmodule.c')],
                define_macros   = DMACROS,
                include_dirs    = INC_DIRS,
                library_dirs    = LIB_DIRS,
                libraries       = LIBRARIES,
                extra_objects   = EXTRA_OBJECTS)]

# Set the directories of where the extra PyNGL data files (fontcaps,
# graphcaps, map databases, example scripts, etc) will be installed.
pyngl_dir       = os.path.join(pkgs_pth, PYNGL_PKG_NAME)
pyngl_ncarg_dir = os.path.join(pyngl_dir, 'ncarg')
pyngl_data_dir  = os.path.join(pyngl_ncarg_dir, 'data')
pynglex_dir     = "examples"
python_bin_dir  = os.path.join(sys.prefix,'bin')

# Create list of supplemental files needed.
DATA_FILES = []
get_pynglex_files()   # Get example files associated
                      # with the "pynglex" script.
#pynglex_scripts = copy_pynglex_script()  # Copy pynglex script to itself with
                                          # python version appended
get_ncarg_files()                        # We need NCARG_ROOT for the lib

setup (name = PYNGL_PKG_NAME,
       version          = pyngl_version,
       license          = 'PyNGL license, similar to University of Illinois/NCSA license',
       platforms         = "Unix, Linux, Windows (Cygwin), MacOSX",
       author           = 'Dave Brown, Fred Clare, and Mary Haley',
       author_email     = 'dbrown@ucar.edu, haley@ucar.edu',
       maintainer       = 'Mary Haley',
       maintainer_email = 'haley@ucar.edu',
       description      = '2D visualization library',
       long_description = long_description,
       url              = 'http://www.pyngl.ucar.edu/',
       package_dir      = { '' : 'src'},
       packages         = [ PYNGL_PKG_NAME ],
       py_modules       = [ 'Ngl' ],
       package_data     = { PYNGL_PKG_NAME : DATA_FILES },
       ext_package      = PYNGL_PKG_NAME,
       ext_modules      = EXT_MODULES
)
