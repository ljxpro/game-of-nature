import pygame
import random
import numpy as np

class Insect:
    Color=(130,130,130)
    def __init__(self,pos,eat_gene,vision_gene,grid):
        self.life = 12
        self.x,self.y = pos
        self.died = False
        self.eat_gene = eat_gene
        self.vision_gene = vision_gene
        self.energy = 0.5
        self.sex = random.choice(["male","female"])
        self.reset_gene(grid)
        
    def reset_gene(self,grid):
        grid.cells[(self.x,self.y)]["insect_occupied"] = True
        grid.cells[(self.x,self.y)]["insect_energy"] = self.energy
        grid.cells[(self.x,self.y)]["insect_sex"] = self.sex
        grid.cells[(self.x,self.y)]["eat_gene"] = self.eat_gene
        grid.cells[(self.x,self.y)]["vision_gene"] = self.vision_gene
        if self.eat_gene[0]+self.eat_gene[1] < 1:
            self.eat = 0.2
        else:
            self.eat = 0.4
        if self.vision_gene[0]+self.vision_gene[1] < 1:
            self.vision = 3
        else:
            self.vision = 5

        
    def survey(self,x, y, d):
        points = [(i, j) for i in range(int(x - d), int(x + d + 1)) for j in range(int(y - d), int(y + d + 1))]
        points.remove((x, y))
        within_distance = filter(lambda p: (x - p[0]) ** 2 + (y - p[1]) ** 2 <= d ** 2, points)
        return list(within_distance)
        
    def action(self,grid):
        candidates = self.survey(self.x,self.y,self.vision)
        candidates = [(n,m) for (n,m) in candidates if ((n>=0)and(m>=0)and(n<grid.grid_width)and(m<grid.grid_height))]
        candidates = [(i,j) for (i,j) in candidates if grid.cells[(i,j)]["plant_occupied"] and grid.cells[(i,j)]["insect_occupied"]==False]
        maximum_pos = []
        if any(candidates):
            maximum = max([grid.cells[x]["plant_life"] for x in candidates])
            for candidate in candidates:
                if grid.cells[candidate]["plant_life"] == maximum:
                    maximum_pos.append(candidate)
                    break
        if len(maximum_pos)>0:
            grid.cells[(self.x,self.y)]["insect_occupied"] = False
            del grid.cells[(self.x,self.y)]["insect_sex"]
            del grid.cells[(self.x,self.y)]["insect_energy"]
            self.x,self.y= random.choice(maximum_pos)
            grid.cells[(self.x,self.y)]["insect_occupied"] = True
            grid.cells[(self.x,self.y)]["insect_sex"] = self.sex
            grid.cells[(self.x,self.y)]["insect_energy"] = self.energy
            grid.cells[(self.x,self.y)]["eat_gene"] = self.eat_gene
            grid.cells[(self.x,self.y)]["vision_gene"] = self.vision_gene
        if grid.cells[(self.x,self.y)]["plant_occupied"] == True:
            self.energy += grid.cells[(self.x,self.y)]["plant_life"]*self.eat
            grid.cells[(self.x,self.y)]["insect_energy"] = self.energy
            grid.cells[(self.x,self.y)]["plant_life"] *= 0.5
            
    
    def attack(self):
        pass
        
    def breed(self,grid,insects):
        neighbors = self.survey(self.x,self.y,1.5)
        neighbors = [(n,m) for ( n,m) in neighbors if ((n>=0)and(m>=0)and(n<grid.grid_width)and(m<grid.grid_height))]

        empty_space = [x for x in neighbors if not grid.cells[x]["insect_occupied"] and grid.cells[x]["plant_occupied"]]
        
        neighbors = [x for x in neighbors if grid.cells[x]["insect_occupied"]]
        neighbors = [x for x in neighbors if grid.cells[x]["insect_sex"]!=self.sex]
        if len(neighbors)>0 and len(empty_space)>0:
            random.shuffle(neighbors)
            random.shuffle(empty_space)
            neighbor = max(neighbors, key=lambda x: grid.cells[x]["insect_energy"])
            empty_space = max(empty_space, key=lambda x: grid.cells[x]["plant_life"])
            if grid.cells[neighbor]["insect_energy"]>=1:
                pz1 = [random.choice(self.eat_gene),random.choice(grid.cells[(self.x,self.y)]["eat_gene"])]
                pz2 = [random.choice(self.vision_gene),random.choice(grid.cells[(self.x,self.y)]["vision_gene"])]
                gene = list(zip(pz1,pz2))
                grid.cells[neighbor]["insect_energy"] -= 1
                self.energy -= 1
                insects.append(Insect((empty_space[0],empty_space[1]),list(gene[0]),list(gene[1]),grid))

    def consume(self,grid,insects):
        self.life -= 1
        if self.life<=0 or self.energy <= 0.5:
            self.died = True
            grid.cells[(self.x,self.y)]["insect_occupied"] = False
            del grid.cells[(self.x,self.y)]["insect_sex"]
            del grid.cells[(self.x,self.y)]["insect_energy"]
            del grid.cells[(self.x,self.y)]["eat_gene"]
            del grid.cells[(self.x,self.y)]["vision_gene"]
            
    def update(self,grid,insects):
        self.energy = grid.cells[(self.x,self.y)]["insect_energy"]
        self.action(grid)
        if self.sex=="female" and self.energy>1:
            self.breed(grid,insects)
        self.consume(grid,insects)
        grid.cells[(self.x,self.y)]["insect_energy"] = self.energy

    def draw(self,screen,tile_size):
        if not self.died:
            radius = tile_size//2
            pygame.draw.circle(screen, self.Color, center = (self.x*tile_size+radius, self.y*tile_size+radius),radius= radius)

class Plant:
    def __init__(self,pos,light_gene,water_gene,grid):
        self.green = 160
        self.x, self.y = pos
        self.died = False
        self.get_light_gene = light_gene
        self.get_water_gene = water_gene
        self.neighbors = {}
        self.candidates = []
        self.reset(grid)
  
    def reset(self,grid):
        self.life = 1+random.random()*0.8
        grid.cells[(self.x,self.y)]["plant_occupied"] = True
        grid.cells[(self.x,self.y)]["plant_life"] = self.life
        if [x + y for x,y in [self.get_light_gene]][0] >= 1:
            self.green += 46
        if [x + y for x,y in [self.get_light_gene]][0] >= 0:
            self.green += 45
        self.Color = (100, self.green, 60,0.5)
    
    def grow(self):
        if [x + y for x,y in [self.get_light_gene]][0] == 0:
            self.life += 0.2
        else:
            self.life += 0.7
        if [x + y for x,y in [self.get_water_gene]][0] == 0:
            self.life += 0.2
        else:
            self.life += 0.7
            
        
    def cell2position(self, cell, tile_size):
        x, y = cell
        return (x * tile_size, y * tile_size)

    def draw(self,screen,tile_size):
        if not self.died:
            x, y = self.cell2position((self.x,self.y),tile_size)
            pygame.draw.rect(screen,self.Color,(x,y,tile_size,tile_size))
        
    
    def breed(self,grid,plants):
        # 定义候选位置
        candidates = [(self.x-1,self.y),(self.x+1,self.y),(self.x,self.y+1),(self.x,self.y-1),
                      (self.x-1,self.y+1),(self.x+1,self.y+1),(self.x-1,self.y-1),(self.x+1,self.y-1)]

        # 过滤候选位置，确保位置在网格内，且未被植物占据
        candidates = [(n,m) for (n,m) in candidates if ((n>=0)and(m>=0)and(n<grid.grid_width)and(m<grid.grid_height))]
        candidates = [(n,m) for (n,m) in candidates if not (grid.cells[(n,m)]["plant_occupied"])]
        self.candidates = candidates
        # 如果候选位置不为空，则生成一个新的植物
        if any(candidates):
            # 从亲本中随机选择两个基因
            pz1 = [random.choice(self.get_light_gene),random.choice(self.get_water_gene)]
            pz2 = [random.choice(self.get_light_gene),random.choice(self.get_water_gene)]
            # 将两个基因组合成一个新的基因
            gene = list(zip(pz1,pz2))
            plants.append(Plant(candidates[random.randint(0,len(candidates)-1)],list(gene[0]),list(gene[1]),grid))
    
    def consume(self,grid):
        self.life -= 1
        candidates = [(self.x-1,self.y),(self.x+1,self.y),(self.x,self.y+1),(self.x,self.y-1),
                      (self.x-1,self.y+1),(self.x+1,self.y+1),(self.x-1,self.y-1),(self.x+1,self.y-1)]

        neighbors = 0
        for candidate in self.candidates:
            if grid.cells[candidate]["plant_occupied"] == True:
                neighbors += 1
        if neighbors>=5:
            self.life -= 0.7
        if neighbors>=7:
            self.life -= 1
        if self.life<=0:
            grid.cells[(self.x,self.y)]["plant_occupied"] = False
            del grid.cells[(self.x,self.y)]["plant_life"]
            self.died = True
        else:
            grid.cells[(self.x,self.y)]["plant_life"] = self.life
            
            
    def update(self,grid,new_plants):
        self.life = grid.cells[(self.x,self.y)]["plant_life"]
        self.grow()
        self.breed(grid,new_plants)
        self.consume(grid)


class Grid:
    Color = (255,232,168)
    def __init__(self, grid_width, grid_height,tile_size):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.tile_size = tile_size
        self.cells = {}
        self.reset_cells()
  
    def reset_cells(self):
        for i in range(self.grid_width):
            for j in range(self.grid_height):
                self.cells[(i,j)] = {"plant_occupied":False,"insect_occupied":False}
  
    def position2cell(self, position):
        x, y = position
        return (x // self.tile_size, y // self.tile_size)
    
    def cell2position(self, cell):
        x, y = cell
        return (x * self.tile_size, y * self.tile_size)

    def draw(self, screen):
        for cell in self.cells:
            if not self.cells[cell]["plant_occupied"]:
                x, y = self.cell2position(cell)
                pygame.draw.rect(screen,self.Color,(x, y, self.tile_size, self.tile_size))

class Game:
    DARK_GREY = (80, 80, 80) #灰色rgb
    def __init__(self, Width=1200, Height=800,Tile_size = 10) :
        pygame.init()#初始化pygame
        self.Width = Width
        self.Height = Height
        self.Tile_size = Tile_size
        self.screen = pygame.display.set_mode((Width, Height))#输入窗口大小
        self.clock = pygame.time.Clock()
        self.grid = Grid(Width//Tile_size, Height//Tile_size, Tile_size)#设置以10像素为一格的网格
        self.update_freq = 300#刷新频率(ms)
        self.time_passed = 0
        self.running = True
        self.pause = True
        self.i_pause = True
        self.FPS = 45#屏幕刷新率
        self.step = 0
        self.reset()

    def reset(self):
        num_p = 20
        num_i = 30
        self.plants = []
        self.insects = []
        self.p_pos = set([(random.randrange(0, self.Width//self.Tile_size), random.randrange(0, self.Height//self.Tile_size)) for _ in range(num_p)])
        self.i_pos = set([(random.randrange(0, self.Width//self.Tile_size), random.randrange(0, self.Height//self.Tile_size)) for _ in range(num_i)])
        for xy in self.p_pos:
            plant = Plant(xy,
                     [random.randrange(0,2),random.randrange(0,2)],
                     [random.randrange(0,2),random.randrange(0,2)],
                     self.grid)
            self.plants.append(plant)
        for xy in self.i_pos:
            eat_gene = [random.randrange(0,2),random.randrange(0,2)]
            vision_gene = [random.randrange(0,2),random.randrange(0,2)]
            insect = Insect(xy,eat_gene,vision_gene,self.grid)
            self.insects.append(insect)
                                        
            
    def get_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.pause = not self.pause
                    self.i_pause = True
                    
                if event.key == pygame.K_i:
                    self.i_pause = not self.i_pause
                
                if event.key == pygame.K_c:
                    self.pause = True
                
                if event.key == pygame.K_r:
                    self.step = 0
                    self.grid.reset_cells()
                    self.reset()

    def update(self):
        if not self.pause:
            self.time_passed += self.clock.tick(self.FPS)
            if self.time_passed > self.update_freq:
                self.time_passed = 0
                self.step += 1
                self.new_plants = []
                self.new_insects = []
                random.shuffle(self.plants)
                for plant in self.plants:
                    if not plant.died:
                        plant.update(self.grid,self.new_plants)
                    else:
                        self.plants.remove(plant)
                for i in range(int(len(self.new_plants)*0.4)):
                    remove_plant = random.choice(self.new_plants)
                    self.grid.cells[(remove_plant.x,remove_plant.y)]["plant_occupied"] = False
                    del self.grid.cells[(remove_plant.x,remove_plant.y)]["plant_life"]
                    self.new_plants.remove(remove_plant)
                if not self.i_pause:
                    random.shuffle(self.insects)
                    for insect in self.insects:
                        if not insect.died:
                            insect.update(self.grid,self.new_insects)
                        else:
                            self.insects.remove(insect)
                    for i in range(int(len(self.new_insects)*0.4)):
                        remove_insect = random.choice(self.new_insects)
                        self.grid.cells[(remove_insect.x,remove_insect.y)]["insect_occupied"] = False
                        del self.grid.cells[(remove_insect.x,remove_insect.y)]["insect_energy"]
                        del self.grid.cells[(remove_insect.x,remove_insect.y)]["insect_sex"]
                        del self.grid.cells[(remove_insect.x,remove_insect.y)]["eat_gene"]
                        del self.grid.cells[(remove_insect.x,remove_insect.y)]["vision_gene"]
                        self.new_insects.remove(remove_insect)
                self.plants.extend(self.new_plants)
                self.insects.extend(self.new_insects)



    def draw(self):
        self.screen.fill(Game.DARK_GREY)
        self.grid.draw(self.screen)
        for plant in self.plants:
            plant.draw(self.screen,self.Tile_size)
        for insect in self.insects:
            insect.draw(self.screen,self.Tile_size)
        for col in range(self.grid.grid_width):
            pygame.draw.line(self.screen, Game.DARK_GREY, (col * self.Tile_size, 0), (col * self.Tile_size, self.Height))
        for row in range(self.grid.grid_height):
            pygame.draw.line(self.screen, Game.DARK_GREY, (0,row * self.Tile_size), (self.Width,row * self.Tile_size))
        
        pygame.display.update()
  
    def play(self):
        while self.running:
            self.get_input()
            self.update()
            self.draw()
            
        pygame.quit()

if __name__ == "__main__":
    game = Game(900,600,15)
    game.play()