import math, random, os, sys, time
from ctypes import *
import pygame

from pygame import sprite
from pygame.locals import *

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


# used for spritegroup
playergroup = []
master = None

"""
[function name, usage, arguments]
#screen.blit( source, dest, area=None );
  usage:  
    draw one image/(source surface) onto another
  argument:
    source - source surface
    dest - dest can be either pairs of coordinates representing the upper left corner of the source or dest.
    area - a small portion of source surface to draw
#surface.convert()
  usage:  
    change the pixel format of an image with corresponding to the monitor. It help fasten the speed whenever SDL requires to do blit-action.
#surface.convert_alpha()
  usage:
    change the pixel format of an image including pixel alpha. Basically speaking, it enable transparency of an image.
"""	

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


### detect collision of circles
### a, b are Surface objects
def detectCC(a, b):
	ax,ay = a.rect.center
	bx,by = b.rect.center
	#return a.rect.colliderect(b.rect)
	return [ True if  math.sqrt ( ((ax - bx )**2) + ((ay - by)**2) ) < ( a.radius+b.radius ) else False ][0]

### calclulate collision of circles
### a, b are Surface objects
def calCC(a, b, v):
	### a: ball, b: player
	ax,ay = a.rect.center
	bx,by = b.rect.center
	
	xdiff = (ax-bx)
	ydiff = (ay-by)

	if ydiff == 0:
		if xdiff > 0:
			angle = math.pi
		else:
			angle = 0
	elif xdiff == 0:
		if ydiff > 0:
			angle = -math.pi*0.5
		else:
			angle = math.pi*0.5
	else:
		theta = math.atan(abs(float(ydiff)/float(xdiff)))
		if ydiff > 0 and xdiff > 0:
			### 4rd
			angle = theta
		elif ydiff > 0 and xdiff < 0:
			### 3rd
			angle = math.pi - theta		
		elif ydiff < 0 and xdiff > 0:
			### 1st 
			angle = -theta
		elif ydiff < 0 and xdiff < 0:
			angle = math.pi + theta

#	print "a({0:d},{1:d})_b({2:d},{3:d})_deg({4:5.2f})".format( ax, ay, bx, by, math.degrees(angle) )
	return angle


	

class Ball(sprite.Sprite):
	def __init__( self, xy, vector, radius = 50 ):
		sprite.Sprite.__init__( self )
		self.origin = xy
		self.vector_o = vector
		self.radius = radius
		self.image, self.rect = load_png( 'ball', radius )
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.vector = vector
		self.rect.topleft = map(int, xy)
		self.lasthit = None
		self.numshit = 0
		self.lasthitangle = None
		self.istatic = True
		
	def update( self ):
		newpos = self.calcNewpos( self.rect, self.vector )
		( angle0,v0 ) = ( angle,v ) = self.vector

		bdl,bdr,bdt,bdb = borders
		if bdt.colliderect(newpos) or bdb.colliderect(newpos):
			if (bdt.colliderect(newpos) and self.lasthit == bdt) or (bdb.colliderect(newpos) and self.lasthit == bdb):
				print "[WARNING] for some reasons, ball may stay in the border for a short while. Here we work around this issume."
				#sys.exit("# of hit:{0:d}".format(self.numshit))
			else:
				self.lasthit = [ bdt if bdt.colliderect(newpos) else bdb ][0]
				self.numshit += 1

				angle = -angle
				x,y = self.rect.center
				#print ' top/ down, ({4:d},{5:d}),({3:6.2f}->{0:6.2f}), ({1:5.2f},{2:5.2f})'.format( 
				#	math.degrees(angle), v*math.cos(angle), v*math.sin(angle), math.degrees(angle0), x, y )

		elif bdl.colliderect(newpos) or bdr.colliderect(newpos):
			if (bdl.colliderect(newpos) and self.lasthit == bdl) or (bdr.colliderect(newpos) and self.lasthit == bdr):
				print "[WARNING] for some reasons, ball may stay in the border for a short while. Here we work around this issume."
				#sys.exit("# of hit:{0:d}".format(self.numshit))
			else:
				self.lasthit = [ bdl if bdl.colliderect(newpos) else bdr ][0]
				self.numshit += 1

				angle = math.pi - angle
				x, y = self.rect.center
				if math.degrees(angle) >= 360.:
					angle -= math.pi*2
				elif math.degrees(angle) < -360.:
					angle += math.pi*2
			
				#print 'left/right, ({4:d},{5:d}),({3:6.2f}->{0:6.2f}), ({1:5.2f},{2:5.2f})'.format( 
				#	math.degrees(angle), v*math.cos(angle), v*math.sin(angle), math.degrees(angle0), x, y )
		else:

			for p in playergroup:

				if self.istatic:
					v = 0

				if detectCC( self,p ):
					self.lasthit = p
					angle = calCC( self,p, v )
					if self.istatic:
						v = p.getMove()
					
		self.rect = newpos
		self.vector = ( angle,v )

	def calcNewpos( self, rect, vector ):
		( angle,v ) = vector
		if self.istatic:
			if v is 0:
				v = (0,0)
			return rect.move(v)
		else:
			return rect.move( v*math.cos(angle),v*math.sin(angle) )

	def reset( self ):
		self.rect.topleft = map(int, self.origin)
		self.vector = self.vector_o
		self.lasthit = None


class Bat(sprite.Sprite):
	def __init__( self, name, xy, radius = 25 ):
		sprite.Sprite.__init__( self )
		self.radius = radius
		self.image, self.rect = load_png( name, radius )
		self.area = screen.get_rect()
		self.name = name
		self.speed = 10
		self.state = "still"
		self.rect.topleft = map(int, xy)
		self.movpos = [0]*2
		self.isfocused = False
		self.mouse_motion = None

	def update( self ):
		focused, p, m = self.mouse_motion
		if focused:
			if not self.isfocused:
				self.isfocused = True
				self.rect.topleft = ( 0,0 )
				self.rect.move_ip( p )
				### modify the cursor's postion to right at the center of Bat.
				self.rect = self.rect.move( map(int,[-self.rect.w*0.5]*2) ) 
			else:
				self.rect = self.rect.move(m)
				#print 'mouse:', p, ', vb:',self.rect.center
		else:
			self.isfocused = False
			self.rect.topleft = ( 2000,2000 )

	def move( self, b, p, m ):
		self.mouse_motion = ( b,p,m )

	def getMove( self ):
		if self.mouse_motion is not None:
			b,p,m = self.mouse_motion
			return m
		return (0,0)
	

def main():
	### fill background
	bg = pygame.Surface( screen.get_size() )
	bg = bg.convert()
	bg.fill( background_colour )

	#bgimg, bgrect = load_png('bg_dark.png')
	bgimg, bgrect = bg, bg.get_rect()
	bgwimg, bgwrect = load_png('bg_wire.png')

	
	### auxiliary line
	nblock = 4
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

	### ball
	global master
	speed = 0
	rand = ( ( 0.1*( random.randint( 5,8 ) ) ) )
	master = ball = Ball( ( width*0.3,height*0.3 ), ( math.radians(0),speed ) )
	


	### player
	global playergroup
	player = Bat( "player", ( 0,0 ) )
	playergroup.append(player)

	### ball sprite
	ballsprite = sprite.RenderPlain( ball )

	### player sprite
	playersprites = sprite.RenderPlain( player )

	### draw background-color
	#screen.blit( bg, (0,0) )
	screen.blit( bgimg, bgrect )
	screen.blit( bgwimg, bgwrect )

	### flip	
	pygame.display.flip()


	clock = pygame.time.Clock()
	t_start = time.time()
	while (1):
		### detect mouse/keyboard event
		if not isRunning():
			break

		clock.tick(30)

		player.move( pygame.mouse.get_focused(), pygame.mouse.get_pos(), pygame.mouse.get_rel() )

		t_measure = [ 1/30. if clock.get_fps() < 30 else 1./clock.get_fps() ][0]

		### blit
		screen.blit( bgimg, ball.rect, ball.rect )
		screen.blit( bgwimg, ball.rect, ball.rect )
		screen.blit( bgimg, player.rect, player.rect )
		screen.blit( bgwimg, player.rect, player.rect )

		### update
		ballsprite.update()
		playersprites.update()

		### draw
		ballsprite.draw( screen )
		playersprites.draw( screen )
		
		pygame.display.set_caption( 'fps: {0:4.2f}'.format(clock.get_fps() ))

		pygame.display.flip()


if __name__  == '__main__':
	main()
