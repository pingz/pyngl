#
#  File:
#    chkbay.py
#
#  Synopsis:
#    Draws contours on a triangular mesh.
#
#  Category:
#    Contouring
#
#  Author:
#    Mary Haley
#  
#  Date of initial publication:
#    September, 2004
#
#  Description:
#    This example reads data defined on a triangular
#    mesh and creates colored contour visualizations of 
#    the depth of water in the Chesapeake Bay.
#
#  Effects illustrated:
#    o  Reading from a NetCDF file using Nio.
#    o  Using a named color table.
#    o  How to spread colors evenly over a
#         subset of a color table.
#    o  Using a cylindrical equidistant map projection.
#    o  How to select a map database resolution.
#    o  How to use function codes in text strings.
#    o  How to use a ".res" file to set resources
#         such as foreground/background color and font.
# 
#  Output:
#    Two visualizations are produced, the first
#    is a simple contour of the depth field and the
#    second overlays that contour on a map of the
#    Chesapeake Bay.
#
#  Notes:
#    1.)  This example requires the resource file
#         chkbay.res.
#
#    2.)  The grid definition and data came from the 
#         Chesapeake Community Model Program Quoddy model:
#  
#            http://ccmp.chesapeake.org
#    
#         using the NOAA/NOS standardized hydrodynamic 
#         model NetCDF format:
#
#            https://sourceforge.net/projects/oceanmodelfiles
#

#
#  Import NumPy.
#
import Numeric

#
#  Import Ngl support functions.
#
import Ngl

#
#  Import Nio for reading netCDF files.
#
import Nio

dirc  = Ngl.pynglpath("data")
cfile = Nio.open_file(dirc + "/cdf/ctcbay.nc","r")

#
#  Read the lat/lon/ele/depth arrays to Numeric arrays.
#
lat   = cfile.variables["lat"][:]
lon   = cfile.variables["lon"][:]
ele   = cfile.variables["ele"][:]
depth = cfile.variables["depth"][:]

#
#  Select a colormap and open a PostScript workstation.
#
rlist            = Ngl.Resources()
rlist.wkColorMap = "rainbow+gray"
wks_type = "ps"
wks = Ngl.open_wks(wks_type,"chkbay",rlist)

#
#  The next set of resources will apply to the contour plot.
#
resources = Ngl.Resources()

resources.nglSpreadColorStart = 15
resources.nglSpreadColorEnd   = -2 

resources.sfXArray         = lon  # Portion of map on which to overlay
resources.sfYArray         = lat  # contour plot.
resources.sfElementNodes   = ele
resources.sfFirstNodeIndex = 1

resources.cnFillOn         = True 
resources.cnLinesOn        = False
resources.cnLineLabelsOn   = False

#
# This plot isn't very interesting because it isn't overlaid on a map.
# We are only creating it so we can retrieve information that we need
# to overlay it on a map plot later. You can turn off this plot
# by setting the nglDraw and nglFrame resources to False.
#
contour = Ngl.contour(wks,depth,resources)

#
#  The next set of resources will apply to the map plot.
#
resources.mpProjection = "CylindricalEquidistant"

#
# If you want high resolution map coastlines, download the RANGS/GSHHS
# files from:
#
#     http://www.io-warnemuende.de/homepages/rfeistel/index.html
#
# The files you need are:
#
#   rangs(0).zip    gshhs(0).zip
#   rangs(1).zip    gshhs(1).zip
#   rangs(2).zip    gshhs(2).zip
#   rangs(3).zip    gshhs(3).zip
#   rangs(4).zip    gshhs(4).zip
#
# Once you unzip these files, put them in the directory
# $python_prefx/pythonx.y/site-packages/PyNGL/ncarg/database/rangs
#
# Now you can change the following resource to "HighRes".
#
resources.mpDataBaseVersion = "MediumRes"

#
# Retrieve the actual lat/lon end points of the scalar array so
# we know where to overlay on map.
#
xs = Ngl.get_float(contour.sffield,"sfXCActualStartF")
xe = Ngl.get_float(contour.sffield,"sfXCActualEndF")
ys = Ngl.get_float(contour.sffield,"sfYCActualStartF")
ye = Ngl.get_float(contour.sffield,"sfYCActualEndF")

resources.mpLimitMode           = "LatLon"
resources.mpMinLonF             = xs     # -77.3244
resources.mpMaxLonF             = xe     # -75.5304
resources.mpMinLatF             = ys     #  36.6342
resources.mpMaxLatF             = ye     #  39.6212

#
# In the chkbay.res file, a resource is being set to indicate the "~"
# character is to represent a function code. A function code signals an
# operation you want to apply to the following text.  In this case,
# ~H10Q~ inserts 10 horizontal spaces before the text, and ~C~ causes
# a line feed (carriage return.
#

resources.tiMainString       = "~H10Q~Chesapeake Bay~C~Bathymetry~H16Q~meters"
resources.lbLabelFontHeightF = 0.02

map = Ngl.contour_map(wks,depth,resources)

Ngl.end()
