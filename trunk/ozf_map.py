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

def get_tile(x,y,z):
    fname = "cache/%d_%d_%d.png"%(z,x,y)
    if os.path.exists(fname):
#        print "cache hit"
        return open(fname).read()
    else:
        url =  "http://mt3.google.com/vt/v=ap.105&hl=ru&x=%d&s=&y=%d&z=%d&s=Gali"%(x,y,z)
        print "fetching %s..."%url
        data = urllib.urlopen(url).read()
        open(fname,"wb").write(data)
        return data
    


#NE = ( 55.954390,37.5329)
#SW = (55.9226,  37.4829)

#~ SW = (39.819085,116.208572)
#~ NE = (40.028666,116.538849)
#~ zoom = 12
#~ zoom_end =  17

SW = (39.89907,116.368046)
NE = (39.935539,116.423492)

zoom = 14
zoom_end = 17


fname = "gmap.ozf2"

mercator = globalmaptiles.GlobalMercator()

# initial
NE_m = mercator.LatLonToMeters(*NE)
SW_m = mercator.LatLonToMeters(*SW)

#tile coordinates
NE_t = mercator.MetersToTile( NE_m[0], NE_m[1], zoom)
SW_t = mercator.MetersToTile( SW_m[0], SW_m[1], zoom)


# extend bounds and fix them
SW_m = mercator.TileBounds(SW_t[0],SW_t[1],zoom)[:2] # min lat,lng
NE_m = mercator.TileBounds(NE_t[0],NE_t[1],zoom)[2:4] #max lat,lng

print "Bounds: SW,NE"
SW = mercator.MetersToLatLon(*SW_m)
NE = mercator.MetersToLatLon(*NE_m)
print SW, NE


SW_m = map(lambda f: f + 1E-2, SW_m)     # 1cm shift to leave dangerous corner point
NE_m = map(lambda f: f - 1E-2, NE_m)     

TILE_WIDTH = 256
TILE_HEIGHT = 256

ozi_ce_hack = True



#compute tiles coordinates for higher zoom levels

for z in xrange(zoom_end,zoom-1,-1):
    SW_t = mercator.MetersToTile(SW_m[0],SW_m[1],z)
    NE_t = mercator.MetersToTile(NE_m[0],NE_m[1],z)
    
    sx, sy =  mercator.GoogleTile(SW_t[0],SW_t[1],z)
    url =  "http://mt3.google.com/vt/v=ap.105&hl=ru&x=%d&s=&y=%d&z=%d&s=Gali"%(sx,sy,z)
    print url
    
    nx,ny =  mercator.GoogleTile(NE_t[0],NE_t[1],z)
    url =  "http://mt3.google.com/vt/v=ap.105&hl=ru&x=%d&s=&y=%d&z=%d&s=Gali"%(nx,ny,z)
    print url

    print  "count:",(nx-sx+1)*(sy-ny+1)
    
    if z == zoom_end:
        #largest zoom level,initialize
        width = (nx - sx + 1) * TILE_WIDTH
        height =  (sy-ny+1) * TILE_HEIGHT
        
        if ozi_ce_hack:
            # Ozi CE has a really weird behaviour. First of all 
            # it only handles prerendered scales below 25% and above 2.5%.
            # Secondly, if the scales 2.5%, 5%, 10% did not exist, the app
            # will not handle neighbour scales.
            # Although when the scale 20% presents, OziCE will handle it
            # instead of 25% scale.
            # So, the trick is to use low scales by artificially extend
            # the claimed size of image.
            # Another trick is to not present 100% scale at all using 40%
            # instead. All above will give us 5 scale levels, each is twice
            # a bigger than previvious.
            
            if   zoom_end - zoom + 1> 5:
                print "WARNING: Ozi CE will IGNORE 6th and consequent zoom levels"
            
            width = int( width / 0.20)
            height = int(height  / 0.20)
            
            
        ozf_file = OzfFile(fname, width,height,  zoom_end - zoom + 1  )
    
    scale = Scale(ozf_file, (nx - sx + 1) * TILE_WIDTH  , (sy-ny+1) * TILE_HEIGHT)
    print scale.tiles_number
    palette = None
    ref_im = None
    tiles = 0
    
    # the weird ozf behaviour: one should write tiles by columns from bottom to top, columns from left to right
    # At the other hand, google 'y' is increasing from top to bottom, 'x' is increasing from left to right
    
    # wrong?  lets start iterating by columns from left to right, i.e. by increasing x 
    for y in xrange(ny,sy+1,1):
 #   for x in xrange(sx,nx+1):
        #~ print "x",x
        cached_tiles =   [ [None,] * scale.xtiles, [None,] * scale.xtiles, [None,] * scale.xtiles,[None,] * scale.xtiles]
        
#        for y in xrange(sy,ny-1,-1):
        for x in xrange(sx,nx+1):
            #~ print "y",y
            data = get_tile(x,y,z)
            #~ print "http://mt3.google.com/vt/v=ap.105&hl=ru&x=%d&s=&y=%d&z=%d&s=Gali"%(x,y,z)
            im = Image.open( StringIO.StringIO(  data) )
            #~ im = Image.new("RGB",(256,256))
            #ImageDraw.Draw(im).text((0,0),"%d, %d"%(x,y) ,font = font, fill = (255,255,255))
            #~ ImageDraw.Draw(im).text((0,0),"%d, %d"%(x,y) ,font = font, fill = 255)
            #~ im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE,colors=256)
            #im = im.convert('RGB').convert('P', palette=Image.WEB)
            if im.size[0] != TILE_WIDTH:
                raise Exception, "wrong tile size"

            if im.size[1] != TILE_HEIGHT:
                raise Exception, "wrong tile size"
            
            # the palette is same for entire scale
            # TODO: so we need to convert each tile to this palette
            
            if palette is None:
                palette = im.getpalette()
                ref_im = im
            else:
                #~ im = im.convert('RGB').convert('P', palette=palette)
                im = im.convert("RGB").quantize(palette = ref_im)
                pass

            # we split each foreign tile to 16 ozi tiles
            # TODO: handle tilesizes different that 64 * k 
            
            # the idea is to write ozf tiles at the end of one foreign tiles line, 
            # i.e. we have to cache xtiles * 256 / 64 = 4*xtiles tiles 
            for i in xrange(4):
                for j in xrange(4):
                    box = (   i * OZF_TILE_WIDTH, j*OZF_TILE_HEIGHT, (i +1) * OZF_TILE_WIDTH,(j+1)*OZF_TILE_HEIGHT)
                    data = im.crop(box).transpose(Image.FLIP_TOP_BOTTOM).tostring()
                    
                    #print len(cached_tiles),scale.xtiles * j + i + y*4
                    #~ data = "%d,%d: %d, %d"%(x,y,i,j)
                    #~ print i
                    
                    cached_tiles[j][(x-sx)*4+i] =    data   
                    #~ print i, data
                    
        for i in xrange(4):
            #~ print i,cached_tiles[i]
            for data in cached_tiles[i]:
                #~ print i, datae
                scale.write_tile(data)
                tiles+=1
                
            
            # test
            
            
    scale.set_palette(palette)
    scale.write()
    print "Scale was wrote."
    print "Scale xtiles: ",scale.xtiles
    print "Scale ytiles: ",scale.ytiles
    print "Wrote tiles: ",tiles
    
ozf_file.finalize()
open("gmap.map","w").write(  map_from_ozf(ozf_file, SW[0], NE[0], SW[1], NE[1] ))



            #im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE,colors=256)
            

            
            
            
            #pass
        





#~ #google tiles
#~ NE_x, NE_y = mercator.GoogleTile(NE_t[0],NE_t[1],zoom)
#~ SW_x, SW_y = mercator.GoogleTile(SW_t[0],SW_t[1],zoom)
#~ 
#~ print NE_x, NE_y
#~ print SW_x, SW_y
#~ 
#~ print "need tiles: ",(SW_y-NE_y+1)*(SW_x-NE_x+1)



