import pygame
import random
import math
from pygame import mixer

# for EXE
# https://stackoverflow.com/a/54926684
import sys, os
def resource_path(relative_path):
  try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
  except Exception:
    base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)

# initialize pygame
pygame.init()
gameClock = pygame.time.Clock()
FPS = 60

cellSize = 64
# create the screen
# note: (0,0) is top left
screenWidth = 13 # measured in # of cells
screenHeight = 13
screenWidthInPixels = screenWidth*cellSize
screenHeightInPixels = screenHeight*cellSize
screen = pygame.display.set_mode((screenWidthInPixels,screenHeightInPixels))

# background and other assets
bg = pygame.image.load(resource_path('assets/img/bg.jpg'))
bg = pygame.transform.scale(bg, (bg.get_width()*0.5, bg.get_height()*0.5))
heartImg = pygame.image.load(resource_path('assets/img/heart.png'))
explosionImg = pygame.image.load(resource_path('assets/img/explosion.png'))
scoreFont = pygame.font.Font(resource_path('assets/fonts/vcr_osd_mono.ttf'), 32)
overFont = pygame.font.Font(resource_path('assets/fonts/vcr_osd_mono.ttf'), 64)
enemyImg = {'A': (pygame.image.load(resource_path('assets/img/enemyA_1.png')),
                  pygame.image.load(resource_path('assets/img/enemyA_2.png'))),
            'B': (pygame.image.load(resource_path('assets/img/enemyB_1.png')),
                  pygame.image.load(resource_path('assets/img/enemyB_2.png'))),
            'C': (pygame.image.load(resource_path('assets/img/enemyC_1.png')),
                  pygame.image.load(resource_path('assets/img/enemyC_2.png')))}
playerImg = pygame.image.load(resource_path('assets/img/player.png'))
bulletImg = pygame.image.load(resource_path('assets/img/bullet.png'))
barrierImg = {'BL': pygame.image.load(resource_path('assets/img/barrierBL.png')),
              'BR': pygame.image.load(resource_path('assets/img/barrierBR.png')),
              'TL': pygame.image.load(resource_path('assets/img/barrierTL.png')),
              'TR': pygame.image.load(resource_path('assets/img/barrierTR.png'))}

# background music and sound effects
#mixer.music.load('background.wav')
#mixer.music.play(-1)
bulletSound = mixer.Sound(resource_path('assets/sounds/laser.wav'))
bulletSound.set_volume(0.25)
explosionSound = mixer.Sound(resource_path('assets/sounds/explosion.wav'))
explosionSound.set_volume(0.1)

# title and icon
pygame.display.set_caption("Alien Intruders")
icon = pygame.image.load(resource_path('assets/img/ufo.png'))
pygame.display.set_icon(icon)

class Player:
  def __init__(self):
    # player icon and coordinates
    self.img = playerImg
    # playerX = 50% of the distance to the screen right side
    self.x = math.floor(screenWidth * 0.5) * cellSize
    # playerY = 1 cell from the screen bottom
    self.y = (screenHeight - 2) * cellSize
    # playerSpeed = # of cells to traverse per second
    self.speed = 8
    # playerDist = number of pixels to move the player per frame when keys pressed
    # = 1sec/60frames * (playerSpeed)cells/1sec * (cellSize)pixels/1cell
    self.dist = (self.speed*cellSize)/FPS
    self.maxHP = 3
    self.HP = self.maxHP
    self.exploding = 0
    self.animClock = 0.0
    self.AFPS = 2.0 # animation frames per second (when exploding)
    self.GFAF = FPS/self.AFPS # game frames per animation frame

  def getLeft(self):
    return self.x

  def getRight(self):
    return self.x + self.img.get_width()

  def getTop(self):
    return self.y

  def getBottom(self):
    return self.y + self.img.get_height()

  def getCenterX(self):
    return self.x + (self.img.get_width()/2)

  def getCenterY(self):
    return self.y + (self.img.get_height()/2)

  def moveLeft(self):
    if (not self.exploding):
      self.x -= self.dist
      # player shouldn't pass screen boundaries
      self.x = max(self.x, 0)

  def moveRight(self):
    if (not self.exploding):
      self.x += self.dist
      self.x = min(self.x, (screenWidth-1)*cellSize)

  def showHP(self):
    x = 0
    y = (screenHeight - 1) * cellSize
    for i in range(self.HP):
      screen.blit(heartImg, (x + (i*cellSize),y))

  def getHP(self):
    return self.HP

  def decrHP(self):
    self.HP -= 1
    self.animClock = 0.0
    self.exploding = 1

  def reset(self):
    self.HP = self.maxHP
    self.animClock = 0.0
    self.exploding = 0

  def isExploding(self):
    return self.exploding == 1

  # return value of player.draw is gameOver
  def draw(self):
    if (not self.exploding and self.HP > 0):
      screen.blit(self.img, (self.x, self.y))
    else:
      if self.animClock >= self.GFAF:
        self.animClock = 0.0
        self.exploding = 0
        # game ends if we run out of health
        if player.getHP() == 0:
          return True
      else:
        self.animClock += 1.0
        screen.blit(explosionImg, (self.x, self.y))
    return False

  # check if an onscreen bullet has collided with the player
  def bulletCollision(self, bullets):
    for bullet in bullets:
      if self.getLeft() < bullet.getCenterX() \
      and bullet.getCenterX() < self.getRight() \
      and self.getTop() < bullet.getCenterY()\
      and bullet.getCenterY() < self.getBottom():
        bullet.hit()
        self.decrHP()
        explosionSound.play()
        return i
    return -1

# create player
player = Player()

# bullets ##################################################################3#

class Bullet:
  def __init__(self, firedAtPlayer = 0):
    self.img = bulletImg
    self.width = self.img.get_width()
    self.height = self.img.get_height()
    self.erase = 0 # remove bullet on successful hits
    self.x = 0
    self.y = 0
    self.firedAtPlayer = firedAtPlayer
    # below attributes are used when bullet "explodes" after colliding with an opposite bullet
    self.exploding = 0
    self.animClock = 0.0 # number of game frames passed since last clock update
    self.AFPS = 2.0 # animation frames per second
    self.GFAF = FPS/self.AFPS # game frames per animation frame

  def locateAtPlayer(self, player):
    self.x = player.getLeft() + (self.width/2)
    self.y = player.getTop()
    
  def locateAtEnemy(self, enemy):
    self.firedAtPlayer = 1
    self.x = enemy.getLeft() + (self.width/2)
    self.y = enemy.getTop()
    # point the bullet at the player
    self.img = pygame.transform.flip(self.img, False, True)

  def fire(self):
    if (not self.firedAtPlayer):
      bulletSound.play()

  def hit(self):
    self.erase = 1

  def move(self):
    if self.exploding: return
    if self.firedAtPlayer:
      self.y += enemyBulletDist
    else:
      self.y -= playerBulletDist

  def shouldRemove(self):
    return self.getBottom() < 0 or self.erase == 1

  def draw(self):
    if not self.exploding:
      screen.blit(self.img, (self.x, self.y))
    else:
      # colliding bullets explode before they die
      if self.animClock >= self.GFAF:
        self.animClock = 0.0
        self.exploding = 0
        self.hit()
      else:
        self.animClock += 1.0
        screen.blit(explosionImg, (self.x, self.y))

  def getCenterX(self):
    return self.x + (self.width/2)

  def getCenterY(self):
    return self.y + (self.height/2)

  def getLeft(self):
    return self.x

  def getRight(self):
    return self.x + self.width

  def getTop(self):
    return self.y

  def getBottom(self):
    return self.y + self.height

  # check if a player bullet collided with an enemy bullet
  def bulletCollision(self, bullets):
    for bullet in bullets:
      if self.getLeft() < bullet.getCenterX() \
      and bullet.getCenterX() < self.getRight() \
      and self.getTop() < bullet.getTop() \
      and bullet.getTop() < self.getCenterY():
        bullet.hit()
        explosionSound.play()
        self.exploding=1
        # the rest of the logic is handled in the draw() method
        break

# keep track of all player-fired bullets on screen
onscreenPlayerBullets = []
playerBulletCooldown = 250 # in ms
playerBulletLastFiredTime = 0
playerBulletSpeed = 12 # # of cells to traverse per second
# num of pixels per frame to move
playerBulletDist = ((playerBulletSpeed*cellSize)/FPS)

# keep track of all enemy-fired bullets on screen
onscreenEnemyBullets = []
enemyBulletCooldown = 1000
enemyBulletLastFiredTime = 0
enemyBulletSpeed = 8
enemyBulletDist = ((enemyBulletSpeed*cellSize)/FPS)

# barriers ############################################################3######

class BarrierPiece:
  def __init__(self,x,y,img):
    self.x = x
    self.y = y
    self.maxHP = 3 # each piece of the barrier can take 3 hits
    self.HP = self.maxHP
    self.img = img
    self.width = self.img.get_width()
    self.height = self.img.get_height()
    # below attributes are used on bullet impacts
    self.exploding = 0
    self.animClock = 0.0 # number of game frames passed since last clock update
    self.AFPS = 2.0 # animation frames per second
    self.GFAF = FPS/self.AFPS # game frames per animation frame

  def draw(self):
    if self.HP > 0:
        screen.blit(self.img, (self.x, self.y))
    if self.exploding:
      if self.animClock >= self.GFAF:
        self.animClock = 0.0
        self.exploding = 0
      else:
        self.animClock += 1.0
        screen.blit(explosionImg, (self.x, self.y))

  def getLeft(self):
    return self.x
  
  def getTop(self):
    return self.y
  
  def getRight(self):
    return self.x + self.width

  def getBottom(self):
    return self.y + self.height

  def getWidth(self):
    return self.width

  def getHeight(self):
    return self.height

  def getImg(self):
    return self.img

  def getHP(self):
    return self.HP

  def isAlive(self):
    return self.HP > 0

  def decrHP(self):
    if self.HP > 0:
      self.HP -= 1
      self.exploding = 1

  def kill(self):
    if self.HP > 0:
      self.HP = 0
      self.exploding = 1

  def reset(self):
    self.HP = self.maxHP
    self.animClock = 0.0
    self.exploding = 0

  # check if an onscreen bullet has collided with this barrier piece
  def bulletCollision(self, bullet):
    return self.getHP()>0 \
    and self.getLeft() < bullet.getCenterX() \
    and bullet.getCenterX() < self.getRight() \
    and self.getTop() < bullet.getCenterY()\
    and bullet.getCenterY() < self.getBottom()

  # check if an enemy has collided with this barrier piece
  def enemyCollision(self, enemy):
    return self.getHP()>0 \
    and enemy.isAlive()\
    and not self.exploding\
    and (self.getLeft() < enemy.getLeft() and enemy.getLeft() < self.getRight() \
    and self.getTop() < enemy.getTop() and enemy.getTop() < self.getBottom()) \
    or (self.getLeft() < enemy.getRight() and enemy.getRight() < self.getRight() \
    and self.getTop() < enemy.getBottom() and enemy.getBottom() < self.getBottom())

class Barrier:
  def __init__(self,left,top):
    self.left = left
    self.top = top
    self.pieces = []
    # a barrier has 4 pieces, each the size of a cell
    TL = BarrierPiece(left,top,barrierImg['TL'])
    TR = BarrierPiece(left+TL.getWidth(),top,barrierImg['TR'])
    BL = BarrierPiece(left,top+TL.getHeight(),barrierImg['BL'])
    BR = BarrierPiece(left+TL.getWidth(),top+TL.getHeight(),barrierImg['BR'])
    self.pieces.append(TL)
    self.pieces.append(TR)
    self.pieces.append(BL)
    self.pieces.append(BR)
    self.width = TL.getWidth() + TR.getWidth()
    self.height = TL.getHeight() + BL.getHeight()
  
  def draw(self):
    for piece in self.pieces:
      piece.draw()

  def getWidth(self):
    return self.width

  def getHeight(self):
    return self.height

  def getLeft(self):
    return self.left

  def getRight(self):
    return self.left + self.width

  def getTop(self):
    return self.top

  def getBottom(self):
    return self.top + self.height

  def isAlive(self):
    for piece in self.pieces:
      if piece.isAlive():
        return True
    return False

  # check if any bullet or enemy has collided with the barrier
  # pb = list of onscreen player-fired bullets
  # eb = list of onscreen enemy-fired bullets
  # e = list of enemies
  def collision(self,pb,eb,e):
    if self.isAlive():
      for piece in self.pieces:
        if piece.isAlive():
          for bullet in pb:
            if piece.bulletCollision(bullet):
              piece.decrHP()
              bullet.hit()
          for bullet in eb:
            if piece.bulletCollision(bullet):
              piece.decrHP()
              bullet.hit()
          for enemy in e:
            if piece.enemyCollision(enemy):
              piece.kill()

  def reset(self):
    for piece in self.pieces:
      piece.reset()

# create 4 barriers near the bottom of the screen
barriers = []
B1 = Barrier(cellSize,(screenHeight - 4) * cellSize)
B2 = Barrier(B1.getRight()+cellSize,B1.getTop())
B3 = Barrier(B2.getRight()+cellSize,B1.getTop())
B4 = Barrier(B3.getRight()+cellSize,B1.getTop())
barriers.append(B1)
barriers.append(B2)
barriers.append(B3)
barriers.append(B4)

# enemies ###################################################3###########33###

# global variables for enemies
enemies = []
enemiesMargin = 2
enemiesRows = 5
numEnemiesPerRow = screenWidth - (enemiesMargin*2)
numEnemies = numEnemiesPerRow * enemiesRows
numEnemiesAlive = numEnemies
# note: enemiesLRSpeed is set in resetEnemies()
enemiesLRSpeed = 0 # num cells to traverse per second in the left-right direction
enemiesDownSpeed = enemiesLRSpeed/2 # downward movement needs to be slower
enemiesDirectionLR = 1 # 1 = move right, -1 = move left
enemiesMovingDown = 0 # 1 = moving down, 0 = stay in same row
enemiesDownDisplacement = 0 # num. pixels moved down so far (downward displacement)
# num of pixels per frame to move enemies left/right:
enemiesDistLR = ((enemiesLRSpeed*cellSize)/FPS)
# num of pixels per frame to move enemies down:
enemiesDistDown = ((enemiesDownSpeed*cellSize)/FPS)
# the Y-val of top-left enemy (regardless of living status) before downward movement started
oldEnemyYVal = -1 
curRow = 0

class Enemy:
  def __init__(self, x, y, row, i, type):
    self.x = x
    self.y = y
    self.alive = 1 # 1 = true, 0 = false
    self.exploding = 0
    self.row = row # which row the enemy is in
    self.i = i # the index of this enemy in the enemy array
    self.type = type
    if (self.type == 3 or self.type == 4):
      self.img = [enemyImg['A'][0], enemyImg['A'][1]]
      self.points = 10 # number of points awarded by killing this enemy
    elif (self.type == 1 or self.type == 2):
      self.img = [enemyImg['B'][0], enemyImg['B'][1]]
      self.points = 20
    elif (self.type == 0):
      self.img = [enemyImg['C'][0], enemyImg['C'][1]]
      self.points = 30
    self.iAnim = 0 # current frame of animation
    self.animClock = 0.0 # number of game frames passed since last clock update
    self.AFPS = 2.0 # animation frames per second
    self.GFAF = FPS/self.AFPS # game frames per animation frame
    self.width = self.img[self.iAnim].get_width()
    self.height = self.img[self.iAnim].get_height()

  def draw(self):
    if self.alive:
      if self.animClock >= self.GFAF:
        self.animClock = 0.0
        self.iAnim = 1 - self.iAnim
      else:
        self.animClock += 1.0
      screen.blit(self.img[self.iAnim], (self.x, self.y))
    elif self.exploding:
      if self.animClock >= self.GFAF:
        self.animClock = 0.0
        self.exploding = 0
      else:
        self.animClock += 1.0
        screen.blit(explosionImg, (self.x, self.y))

  def isAlive(self):
    return self.alive

  def kill(self):
    global numEnemiesAlive
    self.alive = 0
    self.animClock = 0.0
    self.exploding = 1
    numEnemiesAlive -= 1

  def reset(self):
    self.alive = 1
    self.animClock = 0.0
    self.exploding = 0

  def getLeft(self):
    return self.x
  
  def getTop(self):
    return self.y

  def getRight(self):
    return self.x + self.width

  def getBottom(self):
    return self.y + self.height

  def getCenterX(self):
    return self.x + (self.width/2)

  def getCenterY(self):
    return self.y + (self.height/2)

  # check if there is another enemy in front of this enemy
  # enemies = list of enemies
  # NEPR = number of enemies per row
  # NER = number of enemy rows
  def frontIsClear(self, enemies, NEPR, NER):
    # index of enemy in front
    iFront = self.i + NEPR
    # either we're in the front row, or the enemy in front of us is dead
    return self.row == NER-1 or (not enemies[iFront].isAlive())

  # check if this enemy can fire a bullet
  # NER = number of enemy rows
  # CD = enemy bullet cooldown
  def okayToFire(self, enemies, NEPR, NER, CD):
    return self.isAlive() and \
    self.frontIsClear(enemies, NEPR, NER) and \
    (enemyBulletLastFiredTime == 0 or \
    (pygame.time.get_ticks() - enemyBulletLastFiredTime) > CD) and \
    random.randint(1,4) == 1 # 1/4 chance of firing bullet
  
  # check if an onscreen bullet has collided with this enemy. play sound, and
  # return bullet index, or else -1
  # note: why we don't use rects for collisions:
  # https://www.reddit.com/r/pygame/comments/7j750k/comment/dr4g9t4/
  def bulletCollision(self, bullets):
    for bullet in bullets:
      if self.isAlive() \
      and self.getLeft() < bullet.getCenterX() \
      and bullet.getCenterX() < self.getRight() \
      and self.getTop() < bullet.getTop()\
      and bullet.getTop() < self.getCenterY():
        explosionSound.play()
        updateScore(enemies[i].points)
        self.kill()
        bullet.hit()
        speedUpEnemies()

  # check if player has collided with this enemy
  # I'm not sure if this logic is correct...
  def playerCollision(self, player):
    if self.isAlive() \
    and (self.getLeft() < player.getLeft() and player.getLeft() < self.getRight() \
    and self.getTop() < player.getTop() and player.getTop() < self.getBottom()) \
    or (self.getLeft() < player.getLeft()+cellSize and player.getLeft()+cellSize < self.getRight() \
    and self.getTop() < player.getTop()+cellSize and player.getTop()+cellSize < self.getBottom()):
      explosionSound.play()
      return True
    else:
      return False

# create rows of enemies, with empty cells on each side of the screen
def resetEnemies():
  global enemiesLRSpeed,enemiesDownSpeed,enemiesDirectionLR,\
    enemiesDistLR,enemiesDistDown,\
    enemiesMovingDown,enemiesDownDisplacement,oldEnemyYVal,curRow,enemies,\
    numEnemiesAlive

  enemiesLRSpeed = 0.25
  enemiesDownSpeed = enemiesLRSpeed/2
  enemiesDistLR = ((enemiesLRSpeed*cellSize)/FPS)
  enemiesDistDown = ((enemiesDownSpeed*cellSize)/FPS)
  enemiesDirectionLR = 1
  enemiesMovingDown = 0
  enemiesDownDisplacement = 0
  oldEnemyYVal = -1 
  curRow = 0
  numEnemiesAlive = numEnemies

  enemies.clear()

  for i in range(numEnemies):
    if i == numEnemiesPerRow*(curRow+1):
      curRow += 1
    enemyX = (enemiesMargin + (i % numEnemiesPerRow)) * cellSize
    enemyY = (1 + curRow) * cellSize
    enemies.append(Enemy(enemyX, enemyY, curRow, i, curRow))

# enemies move faster as they decrease in number
def speedUpEnemies():
  global enemiesLRSpeed,enemiesDownSpeed,enemiesDistLR,enemiesDistDown

  enemiesLRSpeed *= 1.05
  enemiesDownSpeed = enemiesLRSpeed/2
  enemiesDistLR = ((enemiesLRSpeed*cellSize)/FPS)
  enemiesDistDown = ((enemiesDownSpeed*cellSize)/FPS)

# score ######################################################################

scoreValue = 0
hiScoreValue = 0

##############################################################################

def showScore():
  x = cellSize/4
  y = cellSize/4
  score = scoreFont.render("SCORE:" + f'{scoreValue:04}' + ' ', True, (255,255,255))
  screen.blit(score,(x,y))
  hiScore = scoreFont.render("HI-SCORE:" + f'{hiScoreValue:04}', True, (255,255,255))
  screen.blit(hiScore,((screenWidthInPixels/2)-(hiScore.get_width()/2),y))

def updateScore(pts):
  global scoreValue
  scoreValue = min(scoreValue + pts, 9999)

def updateHiScore(pts):
  global scoreValue
  global hiScoreValue
  hiScoreValue = max(scoreValue, hiScoreValue)

def startGame():
  global scoreValue,player,barriers,enemies,playerBulletLastFiredTime,enemyBulletLastFiredTime,onscreenPlayerBullets,onscreenEnemyBullets

  scoreValue = 0

  player.reset()

  for barrier in barriers:
    barrier.reset()

  for enemy in enemies:
    enemy.reset()

  player.reset()

  playerBulletLastFiredTime = 0
  enemyBulletLastFiredTime = 0
  onscreenPlayerBullets.clear()
  onscreenEnemyBullets.clear()

  resetEnemies()

# game loop (1 iteration = 1 frame) ##########################################

running = True
gameOver = False
winner = False
startScreen = True

while running:
  screen.fill((0,0,0))
  # bg image
  screen.blit(bg, (0, 0))

  if startScreen:
    titleMsg = overFont.render("ALIEN INTRUDERS", True, (255,255,255))
    screen.blit(titleMsg,
    ((screenWidthInPixels/2)-(titleMsg.get_width()/2),
    (screenHeightInPixels/2)-(titleMsg.get_height()*2)))
    startMsg = scoreFont.render("Press ENTER to start", True, (255,255,255))
    screen.blit(startMsg,
    ((screenWidthInPixels/2)-(startMsg.get_width()/2),
    (screenHeightInPixels/2)+(startMsg.get_height()*2)))
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
          startScreen = False
          startGame()
  elif winner:
    winnerMsg = overFont.render("WINNER!", True, (255,255,255))
    screen.blit(winnerMsg,
    ((screenWidthInPixels/2)-(winnerMsg.get_width()/2),
    (screenHeightInPixels/2)-(winnerMsg.get_height()*2)))
    scoreMsg = scoreFont.render("SCORE:" + f"{scoreValue:04}", True, (255,255,255))
    screen.blit(scoreMsg,
    ((screenWidthInPixels/2)-(scoreMsg.get_width()/2),
    (screenHeightInPixels/2)))
    hiScoreMsg = scoreFont.render("HISCORE:" + f"{hiScoreValue:04}", True, (255,255,255))
    screen.blit(hiScoreMsg,
    ((screenWidthInPixels/2)-(hiScoreMsg.get_width()/2),
    (screenHeightInPixels/2)+(hiScoreMsg.get_height()*2)))
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
          winner = False
          startGame()
  elif gameOver:
    overMsg = overFont.render("GAME OVER", True, (255,255,255))
    screen.blit(overMsg,
    ((screenWidthInPixels/2)-(overMsg.get_width()/2),
    (screenHeightInPixels/2)-(overMsg.get_height()*2)))
    restartMsg = scoreFont.render("Press ENTER to restart", True, (255,255,255))
    screen.blit(restartMsg,
    ((screenWidthInPixels/2)-(restartMsg.get_width()/2),
    (screenHeightInPixels/2)+(restartMsg.get_height()*2)))
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
          gameOver = False
          startGame()
  else:
    # handle single key presses ##############################################
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        # fire bullet if first bullet or if cooldown expired (and you're not currently hit)
        if event.key == pygame.K_SPACE and \
        (playerBulletLastFiredTime == 0 or \
        (pygame.time.get_ticks() - playerBulletLastFiredTime) > playerBulletCooldown) and \
        not player.isExploding():
          playerBullet = Bullet()
          playerBullet.locateAtPlayer(player)
          playerBullet.fire()
          onscreenPlayerBullets.append(playerBullet)
          playerBulletLastFiredTime = pygame.time.get_ticks()
    
    # handle continuous key presses (i.e. player movement) ###################
    # https://stackoverflow.com/a/64611463
    keys = pygame.key.get_pressed()
    # number of pixels to move per frame = 
    # 1sec/60frames * (playerSpeed)cells/1sec * (cellSize)pixels/1cell
    if keys[pygame.K_LEFT]: player.moveLeft()
    elif keys[pygame.K_RIGHT]: player.moveRight()
    gameOver = player.draw()

    # check for bullet hitting player
    player.bulletCollision(onscreenEnemyBullets)
    
    # enemy logic ############################################################

    hitBoundsFlag = 0

    for i in range(numEnemies):
      # game over if enemy hits player
      if enemies[i].playerCollision(player):
        gameOver = True
        break
      # win game if no more enemies
      if numEnemiesAlive == 0:
        winner = True
        break

      # fire enemy bullets
      if enemies[i].okayToFire(enemies, numEnemiesPerRow, enemiesRows, enemyBulletCooldown):
        enemyBullet = Bullet()
        enemyBullet.locateAtEnemy(enemies[i])
        enemyBullet.fire()
        onscreenEnemyBullets.append(enemyBullet)
        enemyBulletLastFiredTime = pygame.time.get_ticks()

      # if enemies are moving right (respectively, left) and a live enemy on the
      # right (left) flank has hit the right (left) side of the screen, all
      # enemies start moving down
      if not enemiesMovingDown:
        enemies[i].x += enemiesDirectionLR * enemiesDistLR

        if not hitBoundsFlag and enemies[i].alive and \
        (enemiesDirectionLR == 1 and enemies[i].x >= (screenWidth-1)*cellSize) or \
        (enemiesDirectionLR == -1 and enemies[i].x <= 0):
          hitBoundsFlag = 1
      else:
        # moving enemies down is tricky; extra logic is required so that we
        # always move down by exactly cellSize pixels
        if oldEnemyYVal == -1 and i == 0: # remember position of first enemy (top-left corner)
          oldEnemyYVal = enemies[i].y
        enemies[i].y = oldEnemyYVal + (enemies[i].row*cellSize) + enemiesDownDisplacement
        # note that dead enemies are never removed from the enemies array because
        # their position is needed to calculate positions of live enemies

      # player bullet collision handling
      enemies[i].bulletCollision(onscreenPlayerBullets)

      # draw enemy (if alive)
      enemies[i].draw()

    # if they've hit the bounds, start moving enemies down
    if hitBoundsFlag:
      enemiesDirectionLR *= -1
      enemiesMovingDown = 1

    # if they've moved down one complete cell, start moving enemies left-right again
    if enemiesMovingDown:
      if enemiesDownDisplacement == cellSize:
        enemiesMovingDown = 0
        enemiesDownDisplacement = 0
        oldEnemyYVal = -1
      else:
        enemiesDownDisplacement = \
        min(enemiesDownDisplacement + enemiesDistDown, cellSize)

    # draw barriers and handle collisions ####################################

    for barrier in barriers:
      barrier.collision(onscreenPlayerBullets,onscreenEnemyBullets,enemies)
      barrier.draw()

    # draw all onscreen player bullets #######################################
    
    # list of indices of bullets to be removed later from the list
    bulletsToBeRemoved = []

    for i in range(len(onscreenPlayerBullets)):
      onscreenPlayerBullets[i].move()
      # remove bullets that fly off-screen
      if onscreenPlayerBullets[i].shouldRemove():
        bulletsToBeRemoved.append(i)
      else:
        onscreenPlayerBullets[i].draw()

    # remove off-screen bullets from the list by index
    bulletsToBeRemoved.sort(reverse=True) # work backwards to avoid index out of range errors!
    for i in bulletsToBeRemoved:
      onscreenPlayerBullets.pop(i)

    # draw all onscreen enemy bullets ########################################
    
    bulletsToBeRemoved.clear()

    for i in range(len(onscreenEnemyBullets)):
      onscreenEnemyBullets[i].move()
      # remove an enemy bullet that collided with a player bullet
      onscreenEnemyBullets[i].bulletCollision(onscreenPlayerBullets)
      if onscreenEnemyBullets[i].shouldRemove():
        bulletsToBeRemoved.append(i)
      else:
        onscreenEnemyBullets[i].draw()

    bulletsToBeRemoved.sort(reverse=True)
    for i in bulletsToBeRemoved:
      onscreenEnemyBullets.pop(i)

    ##########################################################################
    
    player.showHP()

  if not gameOver and not winner and not startScreen:
    showScore()

  pygame.display.update()

  gameClock.tick(FPS)
