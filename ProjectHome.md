## About ##
ozfenc - python module to create raster maps in popular .ozf2 format. The main goal of the project is to create raster maps from online tile maps sources like OpenStreetMap, Google Maps, MSN, etc.

The raster maps produced could be very large since .ozf2 provides random tiles access and ozf2enc doesn't need to maintain the entire map in memory like official Img2Ozf tool.

To fill .ozf2 prerendered scaled versions of the map the different source zoom levels are used. So the map created looks excellent at any zoom level.

The maps produced are readable by OziExplorer CE and opensource ozex as well.

## Limitations ##
Only power of two scale levels are supported and this scale levels is produced from source zoom levels without any changes  in scale.

That is, the produced file could contains for instance prerendered scales of 100%,50%,25%,12.5% and so on.

Auxilairy scale levels with fixed width 130px and 300px are embedded as claimed by .ozf2 format but are blank.

### OziExplorer CE ###

Unfourtunately, OziExplorer CE has a really weird behaviour. First of all, it only handles prerendered scales below 25% and above 2.5%. Secondly, if the scales 2.5%, 5%, 10% did not exist, the OziCE will not handle neighbour scales. Although when the scale 20% presents, OziCE will handle it instead of 25% scale.
So, the trick is to use low scales by artificially extend the claimed size of image. Another trick is to not present 100% scale at all using 20% instead. All above will give us 4 scale levels, each is twice a bigger than the previous one.

## ozex ##
Ozex contains hardcoded scale levels table. It is easy to patch this table to fit power-of-two requirements as described above.

## Dependences and Platforms ##
Since ozf2enc is the pure python script it works on any platform. However it depends on following python modules:

  * globalmaptiles.py from http://www.maptiler.org/google-maps-coordinates-tile-bounds-projection/ to perform a number of Mercator projection calculations

  * PIL - Python Imaging Library
  * standard ones, such as zlib,math,StringIO

## Installation ##
Browse or checkout SVN repository. Use 'Source' tab in menu.