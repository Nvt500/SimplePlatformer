import pygame, sys, random, time
import asyncio, threading

pygame.init()

L = 1 # WHICH LEVEL STARTS THE GAME SHOULD BE 1

screen = pygame.display.set_mode((1280, 720))
screen.fill("white")
pygame.display.set_caption("Platformer")

font = pygame.font.SysFont("Verdana", 80)
go_right = font.render("GO RIGHT!", True, "black")
font_cords = (screen.get_width()/2-random.randint(0, 600), 200)

clock = pygame.time.Clock()

goal = pygame.USEREVENT + 1
wait = pygame.USEREVENT + 2


class Player(pygame.sprite.Sprite):

  def __init__(self):
    super().__init__()
    self.rect = pygame.Rect(10, 10, 40, 40)
    self.rect.bottomleft = (0, screen.get_height())
    self.vel = pygame.Vector2(0, 0)
    self.direction = [False, False, False, False] # North, East, South, West
    self.right = True
    
  def move(self):
    # Checks for collision with object on each edge of the Player's rectangle
    # P.S It's changed so the line that's getting checked is outside of the rectangle and also for example the top line doesn't go all the way to the right so it doesn't detect the right direction (this could be redundant btw)
    
    for deadly_obj in Levels[L-1].get_deadly_objects():
      if self.rect.colliderect(pygame.Rect(deadly_obj.rect.left-1, deadly_obj.rect.top-1, deadly_obj.rect.width+2, deadly_obj.rect.height+2)):
        self.__init__()
        return
      
    for timed_obj in Levels[L-1].get_timed_objects():
      if self.rect.colliderect(pygame.Rect(timed_obj.rect.left-1, timed_obj.rect.top-1, timed_obj.rect.width+2, timed_obj.rect.height+2)):
        if timed_obj.ready:
          timed_obj.run()
          
    

    obj_sides = [0, 0, 0, 0] # North, East, South, West
    cont = [True, True, True, True] # North, East, South, West
    for obj in Levels[L-1].get_objects():
      if obj.rect.clipline((self.rect.left+1, self.rect.top-1), (self.rect.right-2, self.rect.top-1)):
        self.direction[0] = True
        cont[0] = False
        obj_sides[2] = -(self.rect.top - obj.rect.bottom)
      if obj.rect.clipline((self.rect.left+1, self.rect.bottom), (self.rect.right-2, self.rect.bottom)):
        self.direction[2] = True
        cont[2] = False
        obj_sides[0] = self.rect.bottom - obj.rect.top
      if obj.rect.clipline((self.rect.right, self.rect.top+1), (self.rect.right, self.rect.bottom-2)):
        self.direction[1] = True
        cont[1] = False
        obj_sides[3] = self.rect.right - obj.rect.left
      if obj.rect.clipline((self.rect.left-1, self.rect.top+1), (self.rect.left-1, self.rect.bottom-2)):
        self.direction[3] = True
        cont[3] = False
        obj_sides[1] = (obj.rect.right) - (self.rect.left)
    for i, bool in enumerate(cont):
      if bool:
        self.direction[i] = False
    
    
    if self.direction[2]:
      tmp1 = [i for i in obj_sides[1:] if i != 0]
      tmp2 = [obj_sides[0] for i in range(len(tmp1))]
      can = 0
      for i in range(len(tmp1)):
        if tmp2[i] < tmp1[i]:
          can += 1
      if can == len(tmp1):
        if obj_sides[0] != 0:
          self.vel.y = 0
          self.rect.move_ip(0, -(obj_sides[0]))
          self.direction[0], self.direction[1], self.direction[3] = False, False, False
    
    
    if self.direction[0]:
      tmp1 = [x for i, x in enumerate(obj_sides) if x != 0 and i != 2]
      tmp2 = [obj_sides[2] for i in range(len(tmp1))]
      can = 0
      for i in range(len(tmp1)):
        if tmp2[i] < tmp1[i]:
          can += 1
      if can == len(tmp1):
        if obj_sides[2] != 0:
          self.vel.y = 0
          self.rect.move_ip(0, (obj_sides[0]))
          self.direction[1], self.direction[3] = False, False
    

    if self.direction[1]:
      tmp1 = [i for i in obj_sides[:3] if i != 0]
      tmp2 = [obj_sides[3] for i in range(len(tmp1))]
      can = 0
      for i in range(len(tmp1)):
        if tmp2[i] < tmp1[i]:
          can += 1
      if can == len(tmp1):
        if obj_sides[3] != 0:
          self.vel.x = 0
          self.rect.move_ip(-(obj_sides[3]), 0)
          self.direction[1], self.direction[3] = True, False
    
    
    if self.direction[3]:
      tmp1 = [x for i, x in enumerate(obj_sides) if x != 0 and i != 1]
      tmp2 = [obj_sides[1] for i in range(len(tmp1))]
      can = 0
      for i in range(len(tmp1)):
        if tmp2[i] < tmp1[i]:
          can += 1
      if can == len(tmp1):
        if obj_sides[1] != 0:
          self.vel.x = 0
          self.rect.move_ip((obj_sides[1], 0))
          self.direction[1], self.direction[3] = False, True

    
    self.vel.x = abs(self.vel.x)
    if self.vel.x < 5:
      self.right = True
    # Get keys being pressed
    keys = pygame.key.get_pressed() 
    # Detection of horizontal movement and clears collision detection
    if keys[pygame.K_d] and keys[pygame.K_a]:
      self.vel.x = 0
    elif keys[pygame.K_d] and not self.direction[1]:
      if self.vel.x < 5:
        self.vel.x += 1
        self.right = True
      else:
        self.vel.x -= 1
    elif keys[pygame.K_a] and not self.direction[3]:
      if self.vel.x < 5:
        self.vel.x += 1
        self.right = False
      else:
        self.vel.x -= 1
    else:
      if self.vel.x <= 3:
        self.vel.x = 0
      else:
        self.vel.x -= 1


    # If on south ground velocity is zero. Otherwise it will be negative(except that in this case it is positive because y goes down in pygame)
    if not self.direction[2]:
      if self.vel.y < 10:
        self.vel.y += 1

    # Detection of vertical movement and clears collision detection
    if (keys[pygame.K_w] or keys[pygame.K_SPACE]):
      if self.direction[2]:
        self.vel.y = -10
      elif self.direction[1]:
        self.vel.y = -10
        self.vel.x = 10
        self.right = False
      elif self.direction[3]:
        self.vel.y = -10
        self.vel.x = 10
        self.right = True

    if self.direction[0]:
      if self.vel.y < 0:
        self.vel.y = 0
    
    if not self.right:
      self.vel.x = -self.vel.x
    # Moves Player by velocity
    self.rect.move_ip(self.vel)
    
  def draw(self):
    pygame.draw.rect(screen, "black", self.rect)

class Goal(pygame.sprite.Sprite):

  def __init__(self):
    super().__init__()
    self.rect = pygame.Rect(screen.get_width(), 0, 100, screen.get_height())

class Object(pygame.sprite.Sprite):

  def __init__(self, name, rect, color=None):
    super().__init__()
    self.name = name
    self.rect = rect
    self.color = color
    self.vel = pygame.Vector2(0 ,0)
  
  def draw(self):
    if self.color is not None:
      self.rect.move_ip(self.vel)
      if self.vel.y > 0:
        self.vel.y -= 1
      pygame.draw.rect(screen, self.color, self.rect)

class Deadly_Object(Object):
  
  def __init__(self, name, rect, color):
    self.deadly = True
    Object.__init__(self, name, rect, color)

class Timed_Object(Object):

  def __init__(self, name, rect, color, t):
    self.time = t
    self.ready = True
    Object.__init__(self, name, rect, color)
  
  def run(self):
    self.ready = False
    self.vel.y = 15
    

def create_line_of_death(start, times):
  l = []
  l.append(Object("Red_Square1", pygame.Rect(start, screen.get_height()-20, 20, 20), "red"))
  l.append(Object("Black_Square1", pygame.Rect(start+20, screen.get_height()-20, 80, 20), "black"))
  for i in range(1, times):
      l.append(Object(f"Black_Square{i+1}", pygame.Rect(start+20+i*100, screen.get_height()-20, 80, 20), "black"))
      l.append(Deadly_Object(f"Red_Square{i+1}", pygame.Rect(start+i*100, screen.get_height()-20, 20, 20), "red"))
  l.append(Deadly_Object(f"Red_Square{i+2}", pygame.Rect(start+(i+1)*100, screen.get_height()-20, 20, 20), "red"))
  return l

def create_window():
  return [
    Object("Floor", pygame.Rect(0, screen.get_height(), screen.get_width(), 100)),
    Object("Ceiling", pygame.Rect(0, -100, screen.get_width(), 100)),
    Object("Left_Wall", pygame.Rect(-100, 0, 100, screen.get_height())),
  ]

Levels = []
class Level(pygame.sprite.Sprite):
  
  def __init__(self, obj):
    super().__init__()
    Levels.append(self)
    self.Objects = pygame.sprite.Group()
    self.Objects.add(obj)

  def display(self):
    for obj in self.Objects:
      obj.draw()
  
  def get_objects(self):
    return self.Objects
  
  def get_deadly_objects(self):
    deadly_objects = [i for i in self.Objects if isinstance(i, (Deadly_Object)) and i.deadly]
    return deadly_objects
  
  def get_timed_objects(self):
    timed_objects = [i for i in self.Objects if hasattr(i, "time") and i.color is not None]
    return timed_objects

Player = Player()

Goal = Goal()

Level_Objects = [
  [ #LEVEL 1
    create_window(),
    Object("Right_Wall", pygame.Rect(screen.get_width()-100, 100, 100, screen.get_height()-100), "black"),

    [Object(f"Box{i+1}", pygame.Rect(200 + i*100, screen.get_height()-(25 + i*25), 100, 25 + i*25), "black") for i in range(3)],

    [Object(f"Island{i+1}", pygame.Rect(600 + i*200, screen.get_height()-(75+i*25), 100, 25), "black") for i in range(3)],
  ],
    
  [ #LEVEL 2
    create_window(),

    create_line_of_death(150, 10),
  ],

  [ #LEVEL 3
    create_window(),

    Object("Wall1", pygame.Rect(250, 200, 100, screen.get_height()-200), "black"),
    Object("Wall2", pygame.Rect(0, 0, 125, screen.get_height()-100), "black"),

    [Deadly_Object(f"Wall1_Red_Strip{i+1}", pygame.Rect(0, 555 - 90*i, 125, 20), "red") for i in range(7)],
    [Deadly_Object(f"Wall2_Red_Strip{i+1}", pygame.Rect(250, 600 - 90*i, 100, 20), "red") for i in range(5)],

    Deadly_Object("Red_Square1", pygame.Rect(1000, screen.get_height()-20, 20, 20), "red"),
    Object("Red_Square2", pygame.Rect(1080, screen.get_height()-20, 20, 20), "red"),
  ],

  [ #LEVEL 4
    create_window(),
    
    Object("Pillar1", pygame.Rect(100, 100, 100, screen.get_height()), "black"),
    Object("Pillar2", pygame.Rect(300, 180, 100, screen.get_height()), "black"),
    Object("Pillar3", pygame.Rect(500, 300, 100, screen.get_height()), "black"),
    Object("Pillar4", pygame.Rect(700, 150, 100, screen.get_height()), "black"),
    
    Deadly_Object("Death_Pillar1", pygame.Rect(1000, 550, 50, 170), "red"),
    Deadly_Object("Death_Pillar2", pygame.Rect(1100, 0, 50, screen.get_height()-60), "red"),
    Deadly_Object("Red_Square1", pygame.Rect(1240, 685, 40, 40), "red"),
    
    Deadly_Object("Death_Floor", pygame.Rect(100, 695, 900, 25), "red"),

    [Deadly_Object(f"Pillar1_Red_Strip{i+1}", pygame.Rect(100, 590 - 110*i, 100, 20), "red") for i in range(5)],
    [Deadly_Object(f"Pillar2_Red_Strip{i+1}", pygame.Rect(300, 635 - 110*i, 100, 20), "red") for i in range(5)],
    [Deadly_Object(f"Pillar3_Red_Strip{i+1}", pygame.Rect(500, 590 - 110*i, 100, 20), "red") for i in range(3)],
    [Deadly_Object(f"Pillar4_Red_Strip{i+1}", pygame.Rect(700, 635 - 110*i, 100, 20), "red") for i in range(4)],
  ],

  [ #LEVEL 5
    create_window(),

    Object("Pillar1", pygame.Rect(100, 100, 100, screen.get_height()), "black"),

    Timed_Object("Floating_Rect", pygame.Rect(300, 100, 100, 25), "black", 5),
  ],
]

for lvl in Level_Objects:
  Level(lvl)

running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
    if event.type == goal:
      if L == len(Levels):
        pygame.quit()
        sys.exit()
      else:
        L += 1
        font_cords = (screen.get_width()/2-random.randint(0, 600), 200)
    
  screen.fill("white")

  screen.blit(go_right, font_cords)

  Player.move()
  Player.draw()

  Levels[L-1].display()

  if pygame.sprite.collide_rect(Player, Goal):
    pygame.event.post(pygame.event.Event(goal))
    Player.__init__()

  pygame.display.flip()
  clock.tick(60)
