# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0.5
ang_vel = 0.1
FRICTION = 0.98
ACCEL = 0.1111
LIFESPAN = 70
collisions = 0
started = False
class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_thrust_info = ImageInfo([135, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

def process_sprite_group(group, canvas):
    copy_group = set(group)
    for element in copy_group:
        if element.update() == True:
            group.remove(element)
        else:
            element.draw(canvas)
        
        
def group_collide(group, other_object):
    global collisions, lives, started
    copy_group = set(group)  #to iterate over    
    for element in copy_group:
        if element.collide(other_object):
            group.remove(element)
            other_object.pos = [WIDTH/2, HEIGHT/2]
            other_object.vel = [0,0]
            lives -= 1
            if lives < 0:
                restart_game()
                
def restart_game():
    global started, rock_group, my_ship, lives
    started = False
    rock_group = set()
    lives = 3
    my_ship.pos = [WIDTH/2,HEIGHT/2]
    my_ship.vel = [0,0]
    soundtrack.rewind()
    soundtrack.pause()
               
            
def group_group_collide(group, other_group):
    global collisions
    copy_group = set(group)
    copy_other_group = set(other_group)
    
    for rock in copy_group:
        for missile in copy_other_group:
            if rock.collide(missile):
                group.remove(rock)
                other_group.remove(missile)
                collisions += 1


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
        
    def shoot(self):
        global missile_group
        a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-1,1], 0, 0, missile_image, missile_info, missile_sound)
        a_missile.pos = [self.pos[0] + 45*self.direction[0], self.pos[1] + 45*self.direction[1]]
        a_missile.vel[0] = self.vel[0] + 8*angle_to_vector(self.angle)[0]
        a_missile.vel[1] = self.vel[1] + 8*angle_to_vector(self.angle)[1]
        missile_sound.play()
        missile_group.add(a_missile)
        
    def draw(self,canvas):        
        if self.thrust == False:
            canvas.draw_image(ship_image, ship_info.get_center(), ship_info.get_size(), 
                              self.pos, ship_info.get_size(), self.angle)
        else:
            canvas.draw_image(ship_image, ship_thrust_info.get_center(), ship_thrust_info.get_size(), 
                          self.pos, ship_thrust_info.get_size(), self.angle)
            
    def update(self):
        self.angle += self.angle_vel
        if self.thrust == True:
            self.vel[0] += .5 * angle_to_vector(self.angle)[0]
            self.vel[1] += .5 * angle_to_vector(self.angle)[1]
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.rewind()
            
        self.direction = angle_to_vector(self.angle)
        
        self.pos[0] += self.vel[0] 
        self.pos[1] += self.vel[1] 
        
        self.pos[0] %= 800 
        self.pos[1] %= 600         
        
        
        self.vel[0] *= FRICTION
        self.vel[1] *= FRICTION  
        
    def get_pos(self):
        return self.pos
    def get_radius(self):
        return self.radius
    

    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, 
                          self.pos, self.image_size, self.angle)
                 
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]        

        self.pos[0] %= 800 
        self.pos[1] %= 600   
        self.age += 1
        if self.age > LIFESPAN:
            return True
        else:
            return False
        
    def get_pos(self):
        return self.pos
    def get_radius(self):
        return self.radius
        
        
        
    def collide(self, other_object):
        pos = other_object.get_pos()
        radius = other_object.get_radius()        
        distance = dist(pos, self.pos)
        if distance < self.radius + radius:
            return True
        
        else:
            return False
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, collisions
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True             
        soundtrack.play()
        collisions = 0  
        
def draw(canvas):
    global time, my_ship, started
    
    # animiate background
    time += 1
    center = debris_info.get_center()
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, [center[0] - wtime, center[1]], [size[0] - 2 * wtime, size[1]], 
                                [WIDTH / 2 + 1.25 * wtime, HEIGHT / 2], [WIDTH - 2.5 * wtime, HEIGHT])
    canvas.draw_image(debris_image, [size[0] - wtime, center[1]], [2 * wtime, size[1]], 
                                [1.25 * wtime, HEIGHT / 2], [2.5 * wtime, HEIGHT])

    # draw ship and sprites
    my_ship.draw(canvas)
    
    # update ship and sprites
    my_ship.update()

    #draw lives and score
    
    canvas.draw_text("Lives: " + str(lives), (50, 50), 20, "Red")
    canvas.draw_text("Score: " + str(collisions), (50, 80), 20, "Red")

    process_sprite_group(rock_group, canvas)   
    process_sprite_group(missile_group, canvas)
    
    group_collide(rock_group, my_ship)
    group_group_collide(rock_group, missile_group)
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())    
    
    
#handler for keys
def keydown(key):
    global my_ship
    if key == simplegui.KEY_MAP["right"]:
        my_ship.angle_vel = ang_vel
    elif key == simplegui.KEY_MAP["left"]:
        my_ship.angle_vel = - ang_vel
    elif key == simplegui.KEY_MAP["up"]:
        my_ship.vel[0] += angle_to_vector(my_ship.angle)[0]       
        my_ship.vel[1] += angle_to_vector(my_ship.angle)[1] 
        my_ship.thrust = True
    elif key == simplegui.KEY_MAP["space"]:
        my_ship.shoot()

        
def keyup(key):
    global my_ship
    if key == simplegui.KEY_MAP["right"]:
        my_ship.angle_vel = 0
    elif key == simplegui.KEY_MAP["left"]:
        my_ship.angle_vel = 0
    elif key == simplegui.KEY_MAP["up"]:
        my_ship.thrust = False


# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, started
    a_rock = Sprite([0, 0], [1, 1], 0, 0.1, asteroid_image, asteroid_info)
    
    a_rock.pos[0]  = random.randint(0, WIDTH)
    a_rock.pos[1]  = random.randint(0, HEIGHT)            
    a_rock.vel[0] = random.randint(-4, 4) * collisions / 10 
    a_rock.vel[1] = random.randint(-4, 4) * collisions / 10   
    a_rock.angle_vel = random.randint(-10, 10) / 30
    distance = dist(a_rock.pos, my_ship.pos) #distance from new rock to the ship
    
    if len(rock_group) < 12 and distance > a_rock.radius + my_ship.radius and started == 1:
        rock_group.add(a_rock)


    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)


# initialize ship and two sprites
rock_group = set()
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
missile_group = set()

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
