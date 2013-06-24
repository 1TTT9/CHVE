import math, random, os, sys, time
from ctypes import *
import pygame

from pygame import sprite
from pygame.locals import *

import threading
import urllib3

"""
Tmeplate:
  This file is used as a template for pygame programing.
  Do not pollute this file with appending other codes.
"""
(width, height) =(720,720)
background_colour = (255,255,255)
ball_colour = (255,0,0)
elasticity = 0.80
pygame.init()
pygame.display.set_caption('Template')
#pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((width, height))

# used for spritegroup (both players and ball)
vpgroup = []



end_httpc_flag = False
def runHTTPC():
	global end_httpc_flag

	http = urllib3.HTTPConnectionPool('127.0.0.1', port=7788)

	t_start = time.time()
	while not end_httpc_flag:
		try:
			r = http.request('GET', '/', headers={'connection':'keep-alive', 'user-agent':'ggcln/1.0'})
			print r.headers
		except:
			print '[HTTPC]connect fail'
			end_httpc_flag = True





def drawDemo(bg):
	font = pygame.font.Font(None, 36)
	text = font.render("This is a template.", 1, (10,10,10))
	textpos = text.get_rect()	

	textpos.center = bg.get_rect().center
	bg.blit( text, textpos )
	( x, y ) = ( textpos.x, textpos.y )
	for i in range(1,5):
		textpos = ( x, y-20*i )
		bg.blit( text, textpos )
		textpos = ( x, y+20*i )
		bg.blit( text, textpos )

def isRunning():
	is_running = True
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			is_running = False
		elif event.type == pygame.KEYDOWN:	
			if event.key == pygame.K_ESCAPE:
				is_running = False
			elif event.key == pygame.K_DOWN:
				if master is not None:
					master.reset()
			elif event.key == pygame.K_UP:
				pass		
	return is_running


def load_png( fname, radius = 50 ):
	if fname.endswith('png'):
		w,h = [ (width, height) if fname.startswith('bg') else (102,77) ][0]
		try:
			image = pygame.image.load(fname)
			image = pygame.transform.scale( image, (w, h) ) 
			image = [ image.convert() if image.get_alpha() is None else image.convert_alpha() ][0]
		except pygame.error, msg:
			print 'Cannot load image', bg_fname
			raise SystemExist, msg
		return image, image.get_rect()
	else:
		color =  [ (50,50,250,200) if not fname.startswith("ball") else ball_colour ][0]
		circle = pygame.Surface( [radius*2]*2, SRCALPHA, 32  )
		circle = circle.convert_alpha()
		circle_rect = pygame.draw.circle( circle, color, [radius]*2, radius )
		return circle, circle_rect	

class VPlayer(sprite.Sprite):
	def __init__( self, name, xy, radius = 50 ):
		sprite.Sprite.__init__( self )
		self.origin = xy
		self.radius = radius
		self.image, self.rect = load_png( name, radius )
		self.area = screen.get_rect()
                self.name = name
		self.rect.topleft = map(int, xy)
                self.movpos = [0]*2
                self.pos = [0]*2

        def update( self ):
                self.rect.topleft = ( 0,0 )
                self.rect = self.rect.move( self.pos )

        def move( self, p ):
                self.pos = p
	

def main():

	### http client
	thr = threading.Thread( target=runHTTPC )
	thr.start()

	### fill background
	bg = pygame.Surface( screen.get_size() )
	bg = bg.convert()
	bg.fill( background_colour )

	#bgimg, bgrect = load_png('bg_dark.png')
	bgimg, bgrect = bg, bg.get_rect()
	bgwimg, bgwrect = load_png('bg_wire.png')

	
	### auxiliary line
	nblock = width/30
	for i in range(1,nblock):
		pygame.draw.line( bgimg, (55, 55, 55), (0, height*i/nblock), (width, height*i/nblock), 2 )
		pygame.draw.line( bgimg, (55, 55, 55), (width*i/nblock, 0), (width*i/nblock, height), 2 )


	### border
	global borders
	thickness = height*0.05
	BDL = pygame.draw.rect( bgimg, (35,0,0), pygame.Rect( 0, 0, thickness, height ) )
	BDR = pygame.draw.rect( bgimg, (35,0,0), pygame.Rect( width-thickness,0,thickness, height ) )
	BDT = pygame.draw.rect( bgimg, (35,0,0), pygame.Rect( 0, 0, width, thickness ) )
	BDB = pygame.draw.rect( bgimg, (35,0,0), pygame.Rect( 0, height-thickness, width, thickness ) )
	borders = [BDL, BDR, BDT, BDB]


	### demo 
	#drawDemo(bg)


        global vpgroup
	### ball
        ball = VPlayer('ball', ( width*0.3,height*0.3 ), 50 )
        vpgroup.append(ball)

	### player
	player = VPlayer( "player", ( width*0.5,height*0.5 ), 25 )
	vpgroup.append(player)
        

        vpsprite = []
        for vp in vpgroup:
                vpsprite.append( sprite.RenderPlain(vp) )

	### draw background-color
	#screen.blit( bg, (0,0) )
	screen.blit( bgimg, bgrect )
	screen.blit( bgwimg, bgwrect )

	### flip
	pygame.display.flip()


	clock = pygame.time.Clock()
	t_start = time.time()
	while (1):

                t_bc = time.time()
		### detect mouse/keyboard event
		if not isRunning():
			global end_httpc_flag
			end_httpc_flag = True
			break

		clock.tick(30)

                for vp in vpgroup:
                        vp.move( vp.origin )

                time.sleep(1./30)

		t_measure = [ 1/30. if clock.get_fps() < 30 else 1./clock.get_fps() ][0]

		### blit
                for vp in vpgroup:
                        screen.blit(  bgimg, vp.rect, vp.rect )
                        screen.blit( bgwimg, vp.rect, vp.rect )

                ### update
                for vps in vpsprite:
                        vps.update()

		### draw
                for vps in vpsprite:
                        vps.draw( screen )
		
		pygame.display.set_caption( 'fps: {0:4.2f}'.format(clock.get_fps()) )

		pygame.display.flip()

                t_ec = time.time()
#                print 'execution interval: {0:5.2f}, ({1:5.2f}, {2:5.2f})'.format( 1/(t_ec-t_bc), t_bc, t_ec )


if __name__  == '__main__':
	main()
