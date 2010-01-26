import struct, zlib,math

OZF_TILE_WIDTH  =   64
OZF_TILE_HEIGHT =   64


from PIL import Image

class Scale:
    def __init__(self, ozf_file, width, height):
        self.width = width
        self.height = height
        self.xtiles = int(math.ceil(width*1.0 / OZF_TILE_WIDTH ))
        self.ytiles = int(math.ceil(height *1.0/ OZF_TILE_HEIGHT ))

        self.palette = []
        
        self.ozf_file = ozf_file
        self.tiles_number = (self.xtiles ) * (self.ytiles )  + 1

        self.tiles_addr_table = []# 0,]*self.tiles_number
        
        self.last_tile_id = -1
        
        self.addr = None
        self.counter = 0
        
    def set_palette(self,palette):
        
        for i in xrange(256):
            self.palette+=chr(palette[i*3 +  2])
            self.palette+=chr(palette[i*3 +  1])
            self.palette+=chr(palette[i*3 +  0])
            self.palette+='\0'
        print "pallete:",len(self.palette)
    
    def write_tile(self, data,level = 0):
        self.counter += 1
        #~ print "level: %d; counter: %d"%(level,self.counter)
        tile_addr = self.ozf_file.fd.tell()
        self.tiles_addr_table.append(tile_addr)
        data_z = zlib.compress(data,9)
        self.ozf_file.fd.write(data_z)
        #~ 
        #~ if self.counter == (self.xtiles + 1) * self.ytiles:
            #~ print "add dummy tile in last_line"
            #~ for i in xrange(self.ytiles ):
                #~ self.write_tile("S"*64*64, level + 1)
            #~ 
        #~ elif self.counter % (self.xtiles+1) ==  self.xtiles  :
            #~ print "add dummy tile"
            #~ self.write_tile("S"*64*64,level + 1)
            #~ 
    def write(self):
        if self.addr is None:
            self.tiles_addr_table.append(   self.ozf_file.fd.tell()) # store end tile pointer
            
            self.addr = self.ozf_file.fd.tell()
            self.ozf_file.fd.write( struct.pack("llhh", self.width, self.height, self.xtiles , self.ytiles ) )
            self.ozf_file.fd.write( struct.pack("1024c", *self.palette) )
            
            print len(self.tiles_addr_table)
            self.ozf_file.fd.write( struct.pack("%dl"%self.tiles_number, *self.tiles_addr_table) )
            
            self.ozf_file.scales.append(self)
            
        else:
            print "You must write Scale section only once!"

        return self.addr
        


class OzfFile:    
    def __init__(self, fname,width, height,scales_number):
        self.fname = fname
        self.fd = open(fname,"wb")
        self.width = width
        self.height = height
        self.scales = []
        self.scales_number = scales_number + 2
        
        self.write_header()
        
    def write_header(self):
        out = ""

        magic = 30584
        dummy1, dummy2, dummy3, dummy4,dummy5,dummy6,dummy7,dummy8,dummy9,dummy10 = 0,65600,1078,40,0,0,0,256,2004318071,2004318071
        version = 256
        
        memsiz = 1048576

        depth = 1
        bpp = 8

        scales_addr_table = []

        self.fd.write( struct.pack("h", magic) )
        self.fd.write( struct.pack("llll", dummy1, dummy2, dummy3, dummy4,) )

        self.fd.write( struct.pack("l", self.width) )
        self.fd.write( struct.pack("l", self.height) )

        self.fd.write( struct.pack("h", depth) )
        self.fd.write( struct.pack("h", bpp) )


        self.fd.write( struct.pack("l", dummy5) )
        self.fd.write( struct.pack("l", memsiz) )
        self.fd.write( struct.pack("lll", dummy6, dummy7, dummy8, ) )
        
        self.fd.write( struct.pack("l", version) )
        
        self.fd.write( struct.pack("l", dummy9) )

        self.fd.write( struct.pack("h", self.scales_number - 2) )
        
        #placeholders for scale numbers
        for i in xrange(self.scales_number):
            self.fd.write( struct.pack("l", 0) )
        
        self.fd.write( struct.pack("l", dummy10) )
        
        
        
    

    def finalize(self):
        for size in (130,300):
            sc = Scale(self, size, int(size*1.0/self.width*self.height)  )
            #print size*1.0/self.width*self.height
            for i in xrange(sc.xtiles):
                for j in xrange(sc.ytiles):
                    sc.write_tile("S"*64*64)
            sc.set_palette( (0,)*256*3)
            sc.write()
        
        
                
            
        
        scales_table_addr = self.fd.tell()
        for scale in self.scales:
            self.fd.write(struct.pack("l", scale.addr))

        self.fd.write(struct.pack("l", scales_table_addr))
        
        #jump in header to write scales
        self.fd.seek(60)
        
        if len(self.scales) != self.scales_number:
            print "WARNING: Actual scales number not match previous claimed one. The file will hardly be usable by OziExplorer"
        
        for scale in self.scales[:self.scales_number]:
            percent = scale.width * 100.0 / self.width
            print percent
            self.fd.write( struct.pack("f", percent ) )
        
        self.fd.close()

    def __del__(self):
        self.finalize()
#        return super(OzfFile,self).__del__()
        
        
if __name__ == '__main__':

    ozf_file = OzfFile("output.ozf2",2048,2048)

    imgs = ["map/OSM_z11_y710_x1089_p2048.png", 'map/OSM_z10_y355_x544_p1024.png' ,'map/OSM_z10_y355_x544_p1024.png'  ]
    #imgs = ['map/OSM_z10_y355_x544_p1024.png' ,'map/OSM_z10_y355_x544_p1024.png'  ]
    cnt = 0
    for blah in xrange(len(imgs)):
        img = imgs[blah]
        
        im = Image.open(img)
        im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE,colors=256)
        scale = Scale(ozf_file, im.size[0], im.size[1])
        
        scale.set_palette(im.getpalette())

        for i in xrange( scale.xtiles):
            for j in xrange( scale.ytiles):
                box = (   i * OZF_TILE_WIDTH, j*OZF_TILE_HEIGHT, (i +1) * OZF_TILE_WIDTH,(j+1)*OZF_TILE_HEIGHT)
                img = im.crop(box).transpose(Image.FLIP_TOP_BOTTOM)
                data = img.tostring()
                
                scale.write_tile(data)
                img.save("/tmp/2/file_%d.png"%cnt)
                cnt+=1
                

        scale.write()

    ozf_file.finalize()
