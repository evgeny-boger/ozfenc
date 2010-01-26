#import ozf2
import globalmaptiles,urllib,os,StringIO
from ozf2 import OzfFile, Scale,OZF_TILE_WIDTH,OZF_TILE_HEIGHT
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 20)

def generate_map(fname, width, height, south,north, west, east):
    filename, ext = fname.rsplit('.',1) 
    
    opts = { 'filename' : filename,
             'ext'      :   ext,
             'width'    :   width,
             'width_m1' :   width - 1,
             'height'    :   height,
             'height_m1' :   height - 1,
             'south'    :   south,
             'north'    :   north,
             'west' :   west,
             'east' :   east,
             'MM1B' :  36000/360*1000*(north-south)/ width ,
             }
             
    data = """OziExplorer Map Data File Version 2.2
%(filename)s
%(filename)s.%(ext)s
1 ,Map Code,
WGS 84,WGS 84,   0.0000,   0.0000,WGS 84
Reserved 1
Reserved 2
Magnetic Variation,,,E
Map Projection,Mercator,PolyCal,No,AutoCalOnly,No,BSBUseWPX,No
Point01,xy,    0,    0,                 in, deg,  %(north)s,0.0,N,  %(west)s,0.0,E, grid,   , , ,N
Point02,xy, %(width_m1)s, %(height_m1)s, in, deg,  %(south)s,0.0,N,  %(east)s,0.0,E, grid,   , , ,N
Point03,xy, %(width_m1)s,0,             in, deg,  %(north)s,0.0,N,  %(east)s,0.0,E, grid,   , , ,N
Point04,xy, 0, %(height_m1)s,            in, deg,  %(south)s,0.0,N,  %(west)s,0.0,E, grid,   , , ,N
Projection Setup,,,,,,,,,,
Map Feature = MF ; Map Comment = MC     These follow if they exist
Track File = TF      These follow if they exist
Moving Map Parameters = MM?    These follow if they exist
MM0,Yes
MMPNUM,4
MMPXY,1,0,0
MMPXY,2,%(width)s,0
MMPXY,3,%(width)s,%(height)s
MMPXY,4,0,%(height)s
MMPLL,1,  %(west)s,  %(north)s
MMPLL,2,  %(east)s,  %(north)s
MMPLL,3,  %(east)s,  %(south)s
MMPLL,4,  %(west)s,  %(south)s
MM1B,%(MM1B)f
LL Grid Setup
LLGRID,No,No Grid,Yes,255,16711680,0,No Labels,0,16777215,7,1,Yes,x
Other Grid Setup
GRGRID,No,No Grid,Yes,255,16711680,No Labels,0,16777215,8,1,Yes,No,No,x
MOP,Map Open Position,0,0
IWH,Map Image Width/Height,%(width)s,%(height)s
"""
    return data%opts


def map_from_ozf(ozf_file, south,north, west, east):
    return generate_map( ozf_file.fname, ozf_file.width, ozf_file.height, south,north, west, east)

#print generate_map("blah.ozf2",1024, 1024, 47.9898536384467,48.4582836093693,11.25,11.953125)


SW = (39.89907,116.368046)
NE = (39.935539,116.423492)


fname = "test.ozf2"

TILE_WIDTH = 256
TILE_HEIGHT = 256




zoom_levels = map(lambda f: f*0.01,(40,20,10,5,2.5,1.25))
ozf_file = OzfFile(fname, 8000,8000 , len(zoom_levels))

for zoom in zoom_levels:
    scale = Scale(ozf_file, int(ozf_file.width*zoom), int(ozf_file.height*zoom))
    im = Image.new("P", (64,64))
    ImageDraw.Draw(im).text((0,0),str(zoom) ,font = font, fill = 255)
    data = im.transpose(Image.FLIP_TOP_BOTTOM).tostring()
    
    for i in xrange(scale.xtiles):
        for j in xrange(scale.ytiles):
                scale.write_tile(data)
            
            
    scale.set_palette(im.getpalette())
    scale.write()
    
ozf_file.finalize()
open("test.map","w").write(  map_from_ozf(ozf_file, SW[0], NE[0], SW[1], NE[1] ))
