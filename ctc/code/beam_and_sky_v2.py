## NAME: 
#         beam_and_sky_v2.py
## PURPOSE: 
#         Plots 2D sky*fixed beam pattern*fringe pattern that rotates around RA
#         Simulates visibility using 3D data

#------------------------------------------------------------------------------------------------

import aipy
import numpy
import pylab
import pyfits
import matplotlib.pyplot as plt

#plot set-up

plt.figure(figsize = (10,7))
plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.4, hspace=0.3)

pylab.ion() #interactive mode on

plt1 = None

lsts = numpy.arange(numpy.pi/2,3*numpy.pi/2,0.01) #LST is RA of object at meridian

#get antenna array

filename = 'psa898_v003' #needs to be in local directory?? how to set python path to /opt/local/bin/capo/arp/calfiles/ ??
freqs = [0.150] #GHz
freqs = numpy.asarray(freqs) #needs to be in array form, not list form
aa = aipy.cal.get_aa(filename, freqs) #returns antenna array (length is 32)

#get 3D image and change nside

rawimg3d = aipy.map.Map(fromfits = '/Users/carinacheng/Desktop/Carina/UCBResearch/images/lambda_haslam408_dsds_eq.fits') #reads in 3D image; default is nside=512 (3145728 pixels)

img3d = aipy.map.Map(nside=256)
img3d.from_map(rawimg3d)

#rescaling frequency (Haslam map is 408GHz)

r = 150.0/408
f = r**-2.5 #synchrotron emission (spectral index -2.5)

img3d.map.map *= f #3D image data rescaled

"""
###2D IMAGE SIMULATION###

#get sky (taken from THREEDtoTWOD.py) coordinates

size = 300 #number of wavelengths when starting in uv domain

img2d = aipy.img.Img(size=size, res=0.5)

crdtop = img2d.get_top() #topocentric coordinates
tx,ty,tz = crdtop
sh = tx.shape #remember 2D shape
mask = tx.mask #remember mask
tx,ty,tz = tx.flatten(), ty.flatten(), tz.flatten() #1D array of coordinates

#fill 3D map with 1 pixel value of value 1

value = 1
img3d.map.map = numpy.zeros_like(img3d.map.map)
img3d.put((numpy.array([-1]),numpy.array([0]),numpy.array([0])),numpy.array([1]),numpy.array([value]))
   #location, weight, value
   #location = (1,0,0) which is RA=0 (east),dec=0

#get beam response using 2D img

bm = aa[0].bm_response((tx,ty,tz)) #get beam response for particular topocentric coordinates
bm.shape = sh
bm = numpy.ma.array(bm, mask=mask)
sum_bm = numpy.sum(bm) #used later when computing sky temp

#simulate sky temp

tskies = numpy.zeros_like(lsts)

#get fringe pattern using 2D img

baseline = 3000/aipy.const.len_ns #ns
shat = numpy.array(tx) #east/west baseline (east is positive if using e^-2*pi*i...)
shat.shape = sh
shat = numpy.ma.array(shat, mask=mask)
fringe = numpy.exp(-2j*numpy.pi*shat*baseline*freqs)
"""

###3D IMAGE SIMULATION###

baseline = 3000/aipy.const.len_ns #ns
px = numpy.arange(img3d.npix()) #number of pixels in map
crd3d = numpy.array(img3d.px2crd(px,ncrd=3)) #aipy.healpix.HealpixMap.px2crd?
x3d,y3d,z3d = crd3d[0], crd3d[1], crd3d[2] #1D arrays of eq coordinates of 3Dimg (can define to be whatever coordinate system, but eq is most useful here)

#simulate only 1 pixel value on sky (comment this out if using Haslam map)

value=1
img3d.map.map = numpy.zeros_like(img3d.map.map)
img3d.put((numpy.array([-1]),numpy.array([0]),numpy.array([0])),numpy.array([1]),numpy.array([value]))
     #RA=12, dec=0

vis3d = numpy.zeros(lsts.shape,dtype=numpy.complex) #visibility

for ii,lst in enumerate(lsts): #ii in index, lst is value

    t3d = aipy.coord.eq2top_m(lst,aa.lat) #topocentric conversion matrix (3x3)
    tx3d, ty3d, tz3d = numpy.dot(t3d,crd3d) #topocentric coordinates
    #bm3d = aa[0].bm_response((tx3d,ty3d,tz3d)) #beam response (makes code slow)
    #bm3d = numpy.where(tz3d < 0, 0, bm3d) #gets rid of beam values below horizon
    #sum_bm3d = numpy.sum(bm3d)
 
    #XXX east-west baseline only
    fringe3d = numpy.exp(-2j*numpy.pi*tx3d*baseline*freqs) #fringe pattern

    fluxes3d = img3d.map.map #fluxes

    p13d = fluxes3d*fringe3d#*bm3d
    toplot3d = numpy.real(p13d)
    print numpy.sum(p13d) #print visibility
    
    vis3d[ii] = numpy.sum(p13d)

    if plt1 == None:

        plt1 = pylab.plot(lsts,vis3d.real,'b-') #this is a visibility simulator now
        plt.ylim(-1,1) #manually adjust y range
        plt.ylabel("Visibility")
        plt.xlabel("RA (rad)")
        pylab.show()

    else:

        plt1[0].set_ydata(vis3d.real)
        pylab.draw()



"""
###2D Rotating Image###

for ii,lst in enumerate(lsts): #ii in index, lst is value

    
    crd = img2d.get_eq(ra=lst,dec=0) #equatorial coordinates (index RA for interactive rotation)
    x,y,z = crd #each are 2D arrays
    x,y,z = x.flatten(), y.flatten(), z.flatten()

    fluxes = img3d[x,y,z] #gets fluxes already weighted (1D array)

    fluxes.shape = sh
 
    fluxes = numpy.ma.array(fluxes, mask=mask)

    #plot beam response and sky and fringe pattern

    p1 = numpy.fft.fftshift(fluxes*fringe)
    toplot = numpy.real(p1) #plot phase/real/imaginary
    print numpy.sum(p1)
    
    tskies[ii] = numpy.sum(p1)#/sum_bm #Tsky = integral of (fluxes*bm*fringe) / integral of bm

    if plt1 == None:

        pylab.subplot(1,2,1)
        plt1 = pylab.imshow(toplot,interpolation='nearest',origin='lower',extent=(1,-1,-1,1),vmax=1,vmin=-1)
        cbar = pylab.colorbar(shrink=0.5)
        cbar.set_label("Temperature (K)")
        pylab.subplot(1,2,2)
        plt2 = pylab.plot(lsts,tskies.real,'b.') #this is a visibility simulator now
        plt.ylim(-1,1) #manually adjust y range
        plt.ylabel("Temperature (K)")
        plt.xlabel("RA (rad)")
        pylab.show()

    else:

        plt1.set_data(toplot)
        plt2[0].set_ydata(tskies.real)
        pylab.draw()

 """
