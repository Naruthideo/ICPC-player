#!/usr/bin/python
# ICPC Challenge
# Mouthuy Francois-Xavier

import random,sys,string,math

# Number of children on each team.
CCOUNT = 4
# Constants for the objects in each cell of the field
GROUND_EMPTY,GROUND_TREE,GROUND_S,GROUND_M,GROUND_MS,GROUND_L,GROUND_LM,GROUND_LS,GROUND_SMR,GROUND_SMB = range(0,10)
HOLD_EMPTY,HOLD_P1,HOLD_P2,HOLD_P3,HOLD_S1,HOLD_S2,HOLD_S3,HOLD_M,HOLD_L = range(0,9)
# Constant for the players
RED,BLUE = 0,1
# Height of a child.
STANDING_HEIGHT,CROUCHING_HEIGHT,OBSTACLE_HEIGHT = 9,6,6
# Maximum Euclidean distance a child can throw.
THROW_LIMIT = 24
# Snow capacity limit for a space.
MAX_PILE = 9
CONTENT_HEIGHT = [0,9,1,2,3,3,5,4,6,6]
# Width and height of the playing field.
SIZE = 31
# Constant used to mark child locations in the map, not used in this player.
GROUND_CHILD = 10
X,Y = 0,1
CATCH,KILL,GET_A_SNOWMAN,KILL_A_SNOWMAN,SLEEPING_KILL,SELFISH_KILL,ACTION,WALK = xrange(8)

def dist((x1,y1),(x2,y2)):
    return math.sqrt(float((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1)))
# Return the value of x, clamped to the [ a, b ] range.
def clamp( x, a, b ):
    if x < a:
        return a
    if x > b:
        return b
    return x

# Simple representation for a child's action
class Move:
    action = "idle" # Action the child is making.
    dest = None # Destination of this action (or null, if it doesn't need one) */
    def self_print(self):
        if m.dest:
            sys.stdout.write("%s %d %d\n" % (m.action,m.dest.x,m.dest.y))        
        else:
            sys.stdout.write("%s\n" % m.action)

# Representation of a map
CONTENT,SNOW_HEIGHT = 0,1
class Map:
    def __init__(self):
        self.field = list()
        for x in xrange(SIZE):
            line = list()
            for y in xrange(SIZE):
                line.append([-1,-1])
            self.field.append(line)
    def free(self,x,y):
        return (x>=0 and y>=0 and x<SIZE and y<SIZE and self.field[x][y][SNOW_HEIGHT]<6 and 
                self.field[x][y][CONTENT]<8 and self.field[x][y][CONTENT]!=GROUND_TREE
                and type(self.field[x][y][CONTENT])==int)
    
    def get_path(self,(x,y),(xt,yt)):
        sys.stderr.write(str((x,y,xt,yt)))
        n = max(abs(xt-x),abs(yt-y))
        path = list()
        for t in range(1,n):
            path.append((x+int(round(float(t*(xt-x))/n)),
                         y+int(round(float(t*(yt-y))/n))))
        return path
    def get_height(self,x,y):
        content,height = self.field[x][y]
        return max(((content==GROUND_TREE and 9) or
                    (type(content)!=int and (content.standing and STANDING_HEIGHT or CROUCHING_HEIGHT)) or 0),
                   height + (type(content)==int and CONTENT_HEIGHT[content] or 0))
    def get_shots(self,src,standing,dest):
        x,y = src
        xt,yt = dest
        dx,dy = xt-x,yt-y
        d = dist(src,dest)
        d_delta = d/max(abs(dx),abs(dy))
        i,start = 0,1
        path = self.get_path(src,dest)
        height = standing and STANDING_HEIGHT or CROUCHING_HEIGHT
        shots = list() # all the differents shots that can hit the target
        while((d+i*d_delta)<THROW_LIMIT): # we cannot throw beyond that limit
            N = len(path)+i # the number of steps that will be made by the snowballs ( max(dx,dy) steps to hit )
            ch,cont=0,True
            for j in range(start,len(path)+1):
                xj,yj = path[j-1]
                ch = height-int(round(float(9*j)/N))
                if j!=len(path) and ch<=self.get_height(xj,yj):
                    cont = False
                    break
                start = j!=len(path) and j or start
            if cont:
                d_throw = d+i*d_delta
                shots.append((ch,dest,(x+dx*float(d_throw)/d,y+dy*float(d_throw)/d),d_throw)) 
                # (height at target,target,throw dest,throw factor)
            i+=1
        return shots
        
# Simple representation for a child in the game.
class Child:
    def __init__(self):
        self.pos = [-1,-1] # Location of the child.
        self.standing = True # True if  the child is standing.
        self.color = BLUE # Side the child is on.
        self.holding = HOLD_EMPTY # What's the child holding.
        self.dazed = 0 # How many more turns this child is dazed.
        self.hist = [] # a record of last child states
        self.visible = False
    def modify(self,turn,pos,standing,holding,dazed):
        self.hist.append((turn-1,self.pos,self.standing,self.holding,self.dazed))
        self.pos = pos
        self.standing = standing
        self.holding = holding
        self.dazed = dazed
IDLE,RELOADING = xrange(2)
class RedChild(Child):
    def __init__(self):
        Child.__init__(self)
        self.status = IDLE
        self.color = RED
        self.target = (random.randint(0,SIZE-1),random.randint(0,SIZE-1))
        self.required_dist = 5
    def moves(self,field):
        x,y = self.pos
        xt,yt = type(self.target)!=tuple and self.target.pos or self.target
        all_pos = []
        if field.free(x+1,y): 
            all_pos.append((x+1,y,None))
            if self.standing and field.free(x+2,y):
                all_pos.append((x+2,y,(x+1,y)))
        if field.free(x-1,y):
            all_pos.append((x-1,y,None))
            if self.standing and field.free(x-2,y):
                all_pos.append((x-2,y,(x-1,y)))
        if field.free(x,y-1):
            all_pos.append((x,y-1,None))
            if self.standing and field.free(x,y-2):
                all_pos.append((x,y-2,(x,y-1)))
        if field.free(x,y+1):
            all_pos.append((x,y+1,None))    
            if self.standing and field.free(x,y+2):
                all_pos.append((x,y+2,(x,y+1)))
        if self.standing:
            if field.free(x+1,y+1): 
                all_pos.append((x+1,y+1,None))
            if field.free(x-1,y+1):
                all_pos.append((x-1,y+1,None))
            if field.free(x+1,y-1):
                all_pos.append((x+1,y-1,None))
            if field.free(x-1,y-1):
                all_pos.append((x-1,y-1,None))            
        all_pos = map(lambda((x1,y1,path)): (dist((xt,yt),(x1,y1)),x1,y1,path),all_pos)
        all_pos.sort()
        return (self.standing,all_pos)
    
rnd = random.Random()
field = Map()
score = [0,0]
# List of children on the field, half for each team.
allies = []
enemies = [] 
for i in range(CCOUNT):
    allies.append(RedChild())
    enemies.append(Child())
snowmans = list()
tocapture = list()
targets = list()
for c in allies:
    if c.target not in targets:
        targets.append(c.target)
turnNum = string.atoi( sys.stdin.readline() )
while turnNum >= 0:
    # read the scores of the two sides.
    tokens = string.split( sys.stdin.readline() )
    score[ RED ] = string.atoi(tokens[0])
    score[ BLUE ] = string.atoi(tokens[1])
    # Parse the current map.
    for i in range(SIZE):
        tokens = string.split(sys.stdin.readline())
        for j in range(SIZE):
            # Can we see this cell?
            if tokens[j][0] != '*':
                field.field[i][j][SNOW_HEIGHT] = string.find(string.digits, tokens[j][0])
                field.field[i][j][CONTENT] = string.find(string.ascii_lowercase, tokens[j][1])
                if field.field[i][j][CONTENT]==GROUND_SMB and (i,j) not in snowmans:
                    snowmans.append((i,j))
                elif field.field[i][j][CONTENT]!=GROUND_SMB and (i,j) in snowmans:
                    snowmans.remove((i,j))
                if field.field[i][j][CONTENT]==GROUND_LM and (i,j) not in tocapture:
                    tocapture.append((i,j))
                    
    # Read the states of all the children.
    for c in allies+enemies:
        # Can we see this child?        
        tokens = string.split( sys.stdin.readline() )
        if tokens[ 0 ] == "*":
            c.visible = False
        else:
            # Record the child's location.
            c.visible = True
            c.modify(turnNum,[string.atoi(tokens[0]),string.atoi(tokens[1])],(tokens[2]=='S'),
                     string.find(string.ascii_lowercase,tokens[3]),string.atoi(tokens[4]))
            field.field[c.pos[X]][c.pos[Y]][CONTENT]=c
    # erase wrong captures
    for x,y in tocapture:
        if field.field[x][y][CONTENT]!=GROUND_LM:
            tocapture.remove((x,y))
    # Look all possibilities
    poss = list()
    for c in allies:
        if (dist(type(c.target)==tuple and c.target or c.target.pos,c.pos) or 
            not random.randint(0,20)):
            if c.target in targets :
                targets.remove(c.target)
            while(True):
                my_captures = [(dist(c.pos,pos),pos) for pos in tocapture]
                my_captures.sort()
                if my_captures and my_captures[0][0]<8:
                    if my_captures[0][1] not in targets:
                        c.target = my_captures[0][1]
                        c.required_dist = 1.1
                        break
                if snowmans and random.randint(0,6):
                    tmp = random.choice(snowmans)
                    if tmp not in targets:
                        c.target = tmp
                        c.required_dist = 5
                        break                    
                c.target= (random.randint(0,SIZE-1),random.randint(0,SIZE-1))
                break
            if c.target not in targets:
                targets.append(c.target)
            
        actions = list()
        catchs = list()
        kills,unarmed,dazed = list(),list(),list()
        snow_kills,captures = list(),list()
        walks = c.moves(field)
        # Try to acquire a snowball if we need one.

        if (c.holding==HOLD_S1 or c.holding==HOLD_S2 or c.holding==HOLD_S3):
            for xt in range(max(0,c.pos[X]-1),min(SIZE-1,c.pos[X]+1)+1):
                for yt in range(max(0,c.pos[Y]-1),min(SIZE-1,c.pos[Y]+1)+1):
                    if field.field[xt][yt][CONTENT]==GROUND_LM:
                        m = Move()
                        m.action = 'drop'
                        m.dest = (xt,yt)
                        captures.append(m)
                        sys.stderr.write('drop on that bitch')
        if c.holding != HOLD_EMPTY and not c.dazed and not c.standing:
            m = Move()
            m.action = 'stand'
            actions.append(m)
        if (c.holding != HOLD_S1 and c.holding != HOLD_S2 and c.holding != HOLD_S3) and not c.dazed:
            # Crush into a snowball, if we have snow.
            if c.holding == HOLD_P1:
                m = Move()
                m.action = 'crush'
                actions.append(m)
            else:
                if c.standing:
                    m = Move()
                    m.action = 'crouch'
                    actions.append(m)
                else:
                    # We don't have snow, see if there is some nearby.
                    for ox in range(c.pos[X]-1,c.pos[X]+2):
                        for oy in range(c.pos[Y]-1,c.pos[Y]+2):
                            # Is there snow to pick up?
                            if (ox>=0 and ox<SIZE and
                                oy>=0 and oy<SIZE and
                                (ox!=c.pos[X] or oy!=c.pos[Y]) and
                                field.field[ox][oy][CONTENT]==GROUND_EMPTY and
                                field.field[ox][oy][SNOW_HEIGHT]>0):
                                m = Move()
                                m.action = 'pickup'
                                m.dest = (ox,oy)
                                actions.append(m)
        if not c.dazed:
            for enemy in enemies:
                if enemy.visible:
                    if ((enemy.holding==HOLD_S1 or enemy.holding==HOLD_S2 or enemy.holding==HOLD_S3)
                        and (c.holding==HOLD_S1 or c.holding==HOLD_S2 or c.holding==HOLD_EMPTY)
                        and not enemy.dazed
                        and dist(enemy.pos,c.pos)<9
                        and field.get_shots(enemy.pos,enemy.standing,c.pos)):
                        m = Move()
                        m.action = 'catch'
                        m.dest = enemy.pos
                        catchs.append(m)
                    if ((c.holding==HOLD_S1 or c.holding==HOLD_S2 or c.holding==HOLD_S3)
                        and dist(enemy.pos,c.pos)<23):
                        shots = filter(lambda(x):(x[0]>field.field[enemy.pos[X]][enemy.pos[Y]][SNOW_HEIGHT] and
                                                  x[0]<= (enemy.standing and STANDING_HEIGHT or CROUCHING_HEIGHT)),
                                       field.get_shots(c.pos,c.standing,enemy.pos))
                        if enemy.dazed:
                            dazed.extend(shots)
                        elif (enemy.holding!=HOLD_S1 and enemy.holding!=HOLD_S2 and enemy.holding!=HOLD_S3):
                            unarmed.extend(shots)
                        else :
                            kills.extend(shots)
            if (c.holding==HOLD_S1 or c.holding==HOLD_S2 or c.holding==HOLD_S3):
                for snowman in snowmans:
                    sys.stderr.write('gotta a snowman in sight')
                    shots = field.get_shots(c.pos,c.standing,snowman)
                    for shot in shots:
                        sys.stderr.write( "%s %d with %d\n" % ('snowman should be hit at height'
                                                               ,field.field[snowman[X]][snowman[Y]][SNOW_HEIGHT]
                                                               ,shot[0]))
                    shots = filter(lambda(x):x[0]==1+field.field[snowman[X]][snowman[Y]][SNOW_HEIGHT],
                                   shots)
                    snow_kills.extend(shots)
        poss.append((catchs,kills,captures,snow_kills,dazed,unarmed,actions,walks))

    dontkillhim = list()
    dontkillthat = list()
    dontcapturehim = list()
    dontpickthere = list()
    dontgothere = list()
    for c,(catchs,kills,captures,snow_kills,dazed,unarmed,actions,walks) in zip(allies,poss):
        done = False
        if catchs and random.randint(0,9)>=(2*len(catchs)-1):
            catch = random.choice(catchs)
            sys.stdout.write( "%s %d %d\n" % (catch.action,catch.dest[X],catch.dest[Y]))
            sys.stderr.write( "%s %d %d\n" % (catch.action,catch.dest[X],catch.dest[Y]))
            done = True
        if not done and captures:
            capture = None
            while captures:
                capture = random.choice(captures)
                captures.remove(capture)
                if capture.dest not in dontcapturehim:
                    dontcapturehim.append(capture.dest)
                    break
                else: capture=None
            if capture:
                sys.stdout.write('%s %d %d\n' % (capture.action,capture.dest[X],capture.dest[Y]))
                sys.stderr.write('%s %d %d\n' % (capture.action,capture.dest[X],capture.dest[Y]))
                done = True
        if not done and snow_kills:
            snow_kill = None
            while(snow_kills):
                snow_kill = random.choice(snow_kills)
                snow_kills.remove(snow_kill)
                if snow_kill[1] not in dontkillthat:
                    dontkillthat.append(snow_kill[1])
                    break
            if snow_kill:
                sys.stdout.write('%s %d %d\n' % ('throw',snow_kill[2][X],snow_kill[2][Y]))
                sys.stderr.write('%s %d %d\n' % ('throw',snow_kill[2][X],snow_kill[2][Y]))
                done = True
        if not done and kills and random.randint(0,30):
            kill = None
            while(kills):
                kill = random.choice(kills)
                kills.remove(kill)
                if kill[1] not in dontkillhim:
                    dontkillhim.append(kill[1])
                    break
            if kill:
                sys.stdout.write('%s %d %d\n' % ('throw',kill[2][X],kill[2][Y]))
                sys.stderr.write('%s %d %d\n' % ('throw',kill[2][X],kill[2][Y]))
                done = True
        if not done and unarmed and random.randint(0,5):
            kill = random.choice(unarmed)
            sys.stdout.write('%s %d %d\n' % ('throw',kill[2][X],kill[2][Y]))
            sys.stderr.write('%s %d %d\n' % ('throw',kill[2][X],kill[2][Y]))
            done = True
        if not done and dazed and random.randint(0,1):
            kill = random.choice(dazed)
            sys.stdout.write('%s %d %d\n' % ('throw',kill[2][X],kill[2][Y]))
            sys.stderr.write('%s %d %d\n' % ('throw',kill[2][X],kill[2][Y]))
            done = True
        if not done and actions and (not c.standing or random.randint(0,4)):
            act = None
            while actions:
                act = random.choice(actions)
                actions.remove(act)
                if act.dest:
                    if act.action!='pickup' or act.dest not in dontpickthere:
                        if act.action=='pickup':
                            dontpickthere.append(act.dest)
                        sys.stdout.write('%s %d %d\n' % (act.action,act.dest[X],act.dest[Y]))
                        sys.stderr.write('%s %d %d\n' % (act.action,act.dest[X],act.dest[Y]))
                        done = True
                        break
                else:
                    done=True
                    sys.stdout.write('%s\n' % act.action)
                    sys.stderr.write('%s\n' % act.action)
                    break
        if not done and walks:
            for (d_temp,x,y,path) in walks[1]:
                if (x,y) not in dontgothere and (not path or (path not in dontgothere)):
                    sys.stdout.write('%s %d %d\n' % (walks[0] and 'run' or 'crawl',x,y))
                    sys.stderr.write('%s %d %d\n' % (walks[0] and 'run' or 'crawl',x,y))
                    done = True
                    dontgothere.append((x,y))
                    if path : dontgothere.append(path)
                    break
        if not done:
            sys.stdout.write('idle\n')
            sys.stderr.write('idle\n')
    sys.stderr.write('round %d done !!!\n' % turnNum)
    sys.stdout.flush()
    turnNum = string.atoi( sys.stdin.readline() )
    
