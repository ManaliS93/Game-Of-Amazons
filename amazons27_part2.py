# Basic El Juego de las Amazonas in Python 2.7
# For more information about the game itself, please refer to:
#      http://en.wikipedia.org/wiki/Game_of_the_Amazons
#
# This file provides some basic support for you to develop your automatic Amazons player.
# It gives everyone a common starting point, and it will make it easier for us to set your players
# to play against each other. Therefore, you should NOT make any changes to the provided code unless
# directed otherwise. If you find a bug, please email me.

# This implementation includes two class definitions, some utility functions,
# and a function for a human player ("human").
# The two classes are:
# - The Amazons class: the main game controller
# - The Board class: contains info about the current board configuration.
#   It is through the Board class that the game controller
#   passes information to your player function.
# More details about these two classes are provided in their class definitions

# Your part: Write an automatic player function for the Game of the Amazons.
# * your automatic player MUST have your email userID as its function name (e.g., reh23)
# * The main game controller will call your function at each turn with
#   a copy of the current board as the input argument.  
# * Your function's return value should be your next move.
#   It must be expressed as a tuple of three tuples: e.g., ((0, 3), (1,3), (8,3)) 
#    - the start location of the queen you want to move (in row, column)
#    - the queen's move-to location,
#    - the arrow's landing location.
#   If you have no valid moves left, the function should return False.

# As usual, we won't spend much time on the user interface. 
# Updates of the game board are drawn with simple ascii characters.
#
# - Below is a standard initial board configuration:
#   * The board is a 10x10 grid. (It is advisable to use a smaller board during development/debugging)
#   * Each side has 4 queens. The white queens are represented as Q's; the black queens are represented as q's
#
#      a b c d e f g h i j
#   9  . . . q . . q . . . 
#   8  . . . . . . . . . . 
#   7  . . . . . . . . . . 
#   6  q . . . . . . . . q 
#   5  . . . . . . . . . . 
#   4  . . . . . . . . . . 
#   3  Q . . . . . . . . Q 
#   2  . . . . . . . . . . 
#   1  . . . . . . . . . . 
#   0  . . . Q . . Q . . . 
#
# - During a player's turn, one of the player's queens must be moved, then an arrow must be shot from the moved queen.
# - the arrow is represented as 'x'
# - neither the queens nor their arrows can move past another queen or an arrow
#
# - The objective of the game is to minimze your opponent's queens' movement.
# - The game technically ends when one side's queens have no more legal moves,
#   but the game practically ends when the queens from the two sides have been
#   segregated. We will just count up the territories owned by each side and
#   the side with the larger territory will be declared the winner

############################################

import copy, random, re, time, sys

# The Amazons class controls the flow of the game.
# Its data include:
# * size -- size of board: assume it's <= 10
# * time_limit -- # of seconds a mchine is allowed to take (<30)
# * playerW -- name of the player function who'll play white
# * playerB -- name of the player function who'll play black
# * wqs -- initial positions of the white queens
# * bqs -- initial positions of the black queens
# * board -- current board configuration (see class def for Board)
# Its main functions are:
# * play: the main control loop of a game, which would:
#   - turn taking management: calls each auto player's minimax function (or "human")
#   - check for the validity of the player's move:
#     an auto player loses a turn if an invalid move is returned or if it didn't return a move in the alloted time  
#   - check for end game condition 
#   - declare the winner
# * update: this function tries out the move on a temporary board.
#   if the move is valid, the real board will be updated.
# * end_turn: just get the score from the board class

class Amazons:
    def __init__(self, fname):
        fin = open(fname, 'r')
        self.time_limit = int(fin.readline())
        self.size = int(fin.readline())
        self.playerW = fin.readline().strip()
        self.wqs = tuple(map(ld2rc,fin.readline().split()))
        self.playerB = fin.readline().strip()
        self.bqs  = tuple(map(ld2rc,fin.readline().split()))
        self.board = Board(self.size, self.wqs, self.bqs)

    def update(self, move):
        try:
            (src,dst,adst) = move
        except: return False

        # try out the move on a temp board        
        tmp_board = copy.deepcopy(self.board)
        if tmp_board.valid_path(src,dst):
            tmp_board.move_queen(src,dst)
            if tmp_board.valid_path(dst, adst):
                # the move is good. make the real board point to it
                tmp_board.shoot_arrow(adst)
                del self.board
                self.board = tmp_board
                return True
        # move failed. 
        del tmp_board
        return False

    def end_turn(self):
        return self.board.end_turn()

    def play(self):
        bPlay = True
        wscore = bscore = 0
        while (bPlay):
            for p in [self.playerW, self.playerB]:
                # send player a copy of the current board
                tmp_board = copy.deepcopy(self.board)
                tstart = time.clock()
                move = eval("%s(tmp_board)"%p)
                tstop = time.clock()
                del tmp_board

                print p,": move:", [rc2ld(x) for x in move],"time:", tstop-tstart, "seconds"
                if not move:
                    # if move == False --> player resigned   
                    if self.board.bWhite:
                        (wscore, bscore) = (-1,0)
                    else: (wscore, bscore) = (0,-1)
                    bPlay = False
                    break

                # only keep clock for auto players
                if p != "human" and (tstop - tstart) > self.time_limit:
                    print p, ": took too long -- lost a turn"
                elif not self.update(move):
                    print p, ": invalid move", move, " lost a turn"

                # at the end of the turn, check whether the game ended
                # and update whether white is playing next
                (wscore, bscore) = self.end_turn()
                if wscore and bscore:
                    continue
                else:
                    bPlay = False
                    break
        # print final board
        self.board.print_board()
        if wscore == -1:
            print self.playerW,"(white) resigned.", self.playerB,"(black) wins"
        elif bscore == -1:
            print self.playerB,"(black) resigned.", self.playerW,"(white) wins"
        elif not wscore:
            print self.playerB,"(black) wins by a margin of",bscore
        else: print self.playerW, "(white) wins by a margin of",wscore
                
        
##############################################
# The Board class stores basic information about the game configuration.
# 
# NOTE: The amount of info stored in this class is kept to a minimal. This
# is on purpose. This is just set up as a way for the game controller to
# pass information to your automatic player. Although you cannot change
# the definition of the Board class, you are not constrained to use the
# Board class as your main state reprsentation. You can define your own
# State class and copy/transform from Board the info you need.

# The Board class contains the following data:
#  * config: the board configuration represented as a list of lists.
#    The assumed convention is (row, column) so config[0][1] = "b0"
#  * bWhite: binary indicator -- True if it's white's turn to play
# The Board class supports the following methods:
#  * print_board: prints the current board configuration
#  * valid_path: takes two location tuples (in row, column format) and returns 
#    whether the end points describe a valid path (for either the queen or the arrow)
#  * move_queen: takes two location tuples (in row, column format)
#    and updates the board configuration to reflect the queen moving
#    from src to dst
#  * shoot_arrow: takes one location tuple (in row, column format)
#    and updates the board configuration to include the shot arrow
#  * end_turn: This function does some end of turn accounting: update whose
#    turn it is and determine whether the game ended
#  * count_areas: This is a helper function for end_turn. It figures out
#    whether we can end the game
class Board:
    def __init__(self, size, wqs, bqs):
        self.bWhite = True
        self.config = [['.' for c in range(size)] for r in range(size)]
        for (r,c) in wqs:
            self.config[r][c] = 'Q'
        for (r,c) in bqs:
            self.config[r][c] = 'q'
            
    def print_board(self):
        size = len(self.config)
        print ("     Black")
        tmp = "  "+" ".join(map(lambda x: chr(x+ord('a')),range(size)))
        print (tmp)
        for r in range(size-1, -1, -1):
            print r, " ".join(self.config[r]), r
        print (tmp)
        print ("     White\n")

    def valid_path(self, src, dst):
        (srcr, srcc) = src
        (dstr, dstc) = dst        

        srcstr = rc2ld(src)
        dststr = rc2ld(dst)

        symbol = self.config[srcr][srcc]
        if (self.bWhite and symbol != 'Q') or (not self.bWhite and symbol != 'q'):
            print "invalid move: cannot find queen at src:",srcstr
            return False

        h = dstr-srcr
        w = dstc-srcc
        if h and w and abs(h/float(w)) != 1: 
            print("invalid move: not a straight line")
            return False
        if not h and not w:
            print("invalid move: same star-end")
            return False

        if not h:
            op = (0, int(w/abs(w)))
        elif not w:
            op = (int(h/abs(h)),0)
        else:
            op = (int(h/abs(h)),int(w/abs(w)))

        (r,c) = (srcr,srcc)
        while (r,c) != (dstr, dstc):
            (r,c) = (r+op[0], c+op[1])
            if (self.config[r][c] != '.'):
                print "invalid move: the path is not cleared between",srcstr,dststr
                return False
        return True

    def move_queen(self, src, dst):
        self.config[dst[0]][dst[1]] = self.config[src[0]][src[1]]
        self.config[src[0]][src[1]] = '.'

    def shoot_arrow(self, dst):
        self.config[dst[0]][dst[1]] = 'x'

    def end_turn(self):
        # count up each side's territories
        (w,b) = self.count_areas()
        # if none of the queens of either side can move, the player who just
        # played wins, since that player claimed the last free space.
        if b == w and b == 0:
            if self.bWhite: w = 1
            else: b = 1
        # switch player
        self.bWhite = not self.bWhite
        return (w,b)

    # adapted from standard floodfill method to count each player's territories
    # - if a walled-off area with queens from one side belongs to that side
    # - a walled-off area with queens from both side is neutral
    # - a walled-off area w/ no queens is deadspace
    def count_areas(self):
        # replace all blanks with Q/q/n/-
        def fill_area(replace):
            count = 0
            for r in range(size):
                for c in range(size):
                    if status[r][c] == '.':
                        count+=1
                        status[r][c] = replace
            return count
        
        # find all blank cells connected to the seed blank at (seedr, seedc) 
        def proc_area(seedr,seedc):
            symbols = {} # keeps track of types of symbols encountered in this region
            connected = [(seedr,seedc)] # a stack for df traversal on the grid
            while connected:
                (r, c) = connected.pop()
                status[r][c] = '.'
                for ops in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                    (nr, nc) = (r+ops[0], c+ops[1])
                    if nr < 0 or nr >= size or nc < 0 or nc >= size:
                        continue
                    # if it's a new blank, need to process it; also add to seen
                    if self.config[nr][nc] == '.' and status[nr][nc] == '?':
                        status[nr][nc] = '.'
                        connected.append((nr,nc))
                    # if it's a queen or an arrow; just mark as seen
                    elif self.config[nr][nc] != '.': 
                        status[nr][nc] = 'x'
                        symbols[self.config[nr][nc]] = 1

            if 'Q' in symbols and not 'q' in symbols: # area belongs to white
                return (fill_area('Q'), 0, 0)
            elif 'q' in symbols and not 'Q' in symbols: #area belongs to black
                return (0, fill_area('q'),0)
            elif 'q' in symbols and 'Q' in symbols: # area is neutral
                return (0, 0, fill_area('n'))
            else: # deadspace -- still have to fill but don't return its area value
                fill_area('-')
                return (0,0,0)

        size = len(self.config)
        # data structure for keeping track of seen locations
        status = [['?' for i in range(size)] for j in range(size)]
        wtot = btot = ntot = 0
        for r in range(size):
            for c in range(size):            
                # if it's an empty space and we haven't seen it before, process it
                if self.config[r][c] == '.' and status[r][c] == '?':
                    (w,b,n) = proc_area(r,c)
                    wtot += w
                    btot += b
                    ntot += n
                # if it's anything else, but we haven't seen it before, just mark it as seen and move on
                elif status[r][c] == '?':
                    status[r][c] = 'x'
                    
        if ntot == 0: # no neutral space left -- should end game
            if wtot > btot:
                return (wtot-btot, 0)
            else: return (0, btot-wtot)
        else: return (wtot+ntot, btot+ntot)

# utility functions:
# ld2rc -- takes a string of the form, letter-digit (e.g., "a3")
# and returns a tuple in (row, column): (3,0)
# rc2ld -- takes a tuple of the form (row, column) -- e.g., (3,0)
# and returns a string of the form, letter-digit (e.g., "a3")

def ld2rc(raw_loc):
    return (int(raw_loc[1]), ord(raw_loc[0])-ord('a'))
def rc2ld(tup_loc):
    return chr(tup_loc[1]+ord('a'))+str(tup_loc[0])

# get next move from a human player
# The possible return values are the same as an automatic player:
# Usually, the next move should be returned. It must be specified in the following format:
# [(queen-start-row, queen-start-col), (queen-end-row,queen-end-col), (arrow-end-row, arrow-end-col)]
# To resign from the game, return False

def human(board):

    board.print_board()

    if board.bWhite:
        print("You're playing White (Q)")
    else:
        print("You're playing Black (q)")

    print("Options:")
    print('* To move, type "<loc-from> <loc-to>" (e.g., "a3-d3")')
    print('* To resign, type "<return>"')
    while True: # loop to get valid queen move from human
        while True: # loop to check for valid input syntax first
            raw_move = raw_input("Input please: ").split()
            if not raw_move: # human resigned
                return False
            # if they typed "a3-d3"
            elif re.match("^[a-j][0-9]\-[a-j][0-9]$",raw_move[0]):
                break
            else: print str(raw_move),"is not a valid input format"
        (src, dst) = map(ld2rc, raw_move[0].split('-'))
        if board.valid_path(src, dst):
            board.move_queen(src, dst)
            break 

    board.print_board()
    print("Options:")
    print('* To shoot, type "<loc-to>" (e.g., "h3")')
    print('* To resign, type "<return>"')
    while True: # loop to get valid move from human
        while True: # loop to check for valid syntax first
            raw_move = raw_input("Input please: ")
            if not raw_move:
                return False
            if re.match("^[a-j][0-9]$",raw_move):
                break
            else: print raw_move,"is not a valid input"
        adst = ld2rc(raw_move)
        if board.valid_path(dst,adst):
            return (src,dst,adst)

###################### Your code between these two comment lines ####################################
import Queue
nodeQueue=Queue.Queue()
copyQueue=Queue.Queue()
dict={}
id=0
limit=0
class Node:
	def __init__ (self,state,level,utility,boards,parent=[],child=[]):
		self.state = state
		self.parent = parent
		self.child = child
		self.level=level
		self.utility=utility
		self.boards=boards
		#print "**************************************************************"
		#print boards.print_board()
				
	def addChild (node1,node2):
		#print "------+++++++Inside add child node1 state", node1.state,"node2 state: ",node2.state
		node1=dict[node1.state]
		node2=dict[node2.state]
		
		if not node1 in node2.parent:
			node2.parent.append(node1)
		#print "adding ",node2.state ," to ",node1.state , "as child"
		if not node2 in node1.child:
			node1.child.append(node2)
		
		#for i in range (0,len(node2.parent)):
			#y=node2.parent[i]
			#print "parent of ",node2.state ,"is",y.state
		#for i in range (0,len(node1.child)):
			#print "child of", node1.state,"is",node1.child[i].state
		#print"========================================================="

def mcs116(board):
	#print "*****************",board.config[2][3]
	rootnode=Node(((0,0),(0,0),(0,0)),0,0,board,parent=[],child=[])
	dict[((0,0),(0,0),(0,0))]=rootnode
	nodeQueue.put(rootnode)
	
	next=build_tree(rootnode,2)
	#print"next returned",next
	dict.clear()
	global id
	id=0
	
	return next;
def build_tree(node1,depth):
	'''while not nodeQueue.empty():
		new_curr_node = nodeQueue.get(0)
		print "current node level--------------->",new_curr_node.level,"state",new_curr_node.state
		new_curr_node.board.print_board()
		if new_curr_node.level<=depth:
			traverser(new_curr_node,new_curr_node.board)'''
	#traverser(node1,node1.boards)
	
	getQueues(node1,node1.boards,"Q")
	
	inq = nodeQueue.get()
	falsenode=Node(((0,0),(0,0),(0,0)),0,0,inq.boards,parent=[],child=[])
	nodeQueue.put(falsenode)
	
	
	#print "size of queue",nodeQueue.qsize(),nodeQueue.empty()
	
	while not nodeQueue.empty():
		
		inq = nodeQueue.get()
		if inq.state==((0,0),(0,0),(0,0)):
			#print"false node found",inq.state
			#print "size of new nodeQ",nodeQueue.qsize()
			break
		#print "---------------------------------------------------------------------------------------------------------"
		#print "inq state",inq.state
		#inq.boards.print_board()
		actualN=dict[inq.state]
		getQueues(actualN,actualN.boards,"q")
		
	#print "child length",len(dict[((3,4),(4,3),(3,2))].child)
	nodeQueue.put(falsenode)
	while not nodeQueue.empty():
		
		inq = nodeQueue.get()
		if inq.state==((0,0),(0,0),(0,0)):
			#print"false node found",inq.state
			#print "size of new nodeQ",nodeQueue.qsize()
			break
		#print "---------------------------------------------------------------------------------------------------------"
		#print "inq state",inq.state
		#inq.boards.print_board()
		actualN=dict[inq.state]
		getQueues(actualN,actualN.boards,"Q")
	#print"print for Q board termi"
	final_size=nodeQueue.qsize()
	heuristic(nodeQueue,"Q")
	prun=alpha_beta(node1)
	#print "final_size",final_size
	if final_size==0:
		#print "0 queue"
		for i in range (0,len(node1.child)):
			return node1.child[i].state
	for z in range(0,final_size):
		#print "in for loop",dict[953].utility,z
		if dict[z].utility==prun:
			#print"yuhooooo"
			termi=dict[z].parent[0].parent[0].parent[0]
			
			#print "----******------",termi.state
			return termi.state
			break
	global id
	for z in range(0,id):
		#print "prun is",prun
		if dict.has_key((z,z)):
			if dict[(z,z)].utility==prun:
				#print"yuhoohoo"
				termi=dict[z].parent[0].parent[0].parent[0]
				#print "----******------",termi.state
				return termi.state
	return node1.child[0].state 
	#print "-------------------------------------------------------------------->>>>>>>>>>>>>>>>>>>>>",prun
	
	#nodeQueue.get(0).boards.print_board()
def getQueues(node1,board,qcol):
	
	x=[];
	y=[];
	#print "''''''''''",len(board.config)
	for i,r in enumerate(board.config):
		for j,c in enumerate(r):
			if c==qcol:
				x.append(i)
				y.append(j)
				#print c,i,j
	traverser(node1,node1.boards,x,y,qcol)

def traverser(node,board,a,b,qcol):
	x=a;
	y=b;
	
	for p in range(0,len(x)):
		temp_dly=y[p]
		temp_uly=y[p]
		temp_dry=y[p]
		temp_ury=y[p]
		#tempx=x[p]-1
		tempx_dl_list=[]
		tempx_dr_list=[]
		global limit
		for i in range (x[p]+1,len(board.config)):#------------Up-----------
			
			limit+=1
		
			if limit>1:
				limit=0
				break
			if board.config[i][y[p]]=='.':
				#print "i found empty at up",i,y[p]
				#start = time.clock();
				arrow(x[p],y[p],i,y[p],board,node,qcol)
				#print "time taken for up arrow: ",time.clock()-start, "seconds ***************	"
			else:
				break
		for j in range (y[p]+1,len(board.config)):#---------------Right---------
			limit+=1
		
			if limit>1:
				limit=0
				break
			if board.config[x[p]][j]=='.':
				#print "i found empty at for right",x[p],j
				arrow(x[p],y[p],x[p],j,board,node,qcol)
			else:
				break
		for i in range (x[p]-1,-1,-1):				#--------------Down------------
			limit+=1
		
			if limit>1:
				limit=0
				break
			if board.config[i][y[p]]=='.':
				#print "i found empty at down",i,y[p]
				arrow(x[p],y[p],i,y[p],board,node,qcol)
			else:
				break
		for j in range (y[p]-1,-1,-1):				#--------------Left----------
			limit+=1
		
			if limit>5:
				limit=0
				break
			if board.config[x[p]][j]=='.':
				#print "i found empty at for left",x[p],j
				arrow(x[p],y[p],x[p],j,board,node,qcol)
			else:
				break
			
		for n in range (0,x[p]): #--------------Down Right--------------
			tempx_dl_list.append(n)
		for j in reversed (tempx_dl_list):
			limit+=1
		
			if limit>1:
				limit=0
				break
			temp_dly=temp_dly+1
			if not(temp_dly)==len(board.config):
				if board.config[j][temp_dly]=='.':
					#print "i found empty at for down right",j,temp_dly, board.config[j][temp_dly]
					arrow(x[p],y[p],j,temp_dly,board,node,qcol)
				else:
					break
			else:
				break
		for j in range (x[p]+1,len(board.config)): #---------------------Up Right----------------
			limit+=1
		
			if limit>1:
				limit=0
				break
			temp_uly=temp_uly+1
			if not(temp_uly)==len(board.config):
				if board.config[j][temp_uly]=='.':
					#print "i found empty at for up right",j,temp_uly, board.config[j][temp_uly]
					arrow(x[p],y[p],j,temp_uly,board,node,qcol)
				else:
					break
			else:
				break		
		for n in range (0,x[p]): #--------------Down Left-------------------
			#print "---",n
			tempx_dr_list.append(n)
		for j in reversed (tempx_dr_list):
			limit+=1
		
			if limit>1:
				limit=0
				break
			temp_dry=temp_dry-1
			
			if not(temp_dry)<0:
				if board.config[j][temp_dry]=='.':
					#print "i found empty at for down left",j,temp_dry, board.config[j][temp_dry]
					arrow(x[p],y[p],j,temp_dry,board,node,qcol)
				else:
					break
			else:
				break
		for j in range (x[p]+1,len(board.config)): #----------Up Left----------------
			limit+=1
		
			if limit>1:
				limit=0
				break
			#print "x is" ,j
			temp_ury=temp_ury-1
			#print "x is" ,j,"y is",temp_ury
			if not(temp_ury)<0:
				if board.config[j][temp_ury]=='.':
					#print "i found empty at for up left",j,temp_ury, board.config[j][temp_ury]
					arrow(x[p],y[p],j,temp_ury,board,node,qcol)
				else:
					#print"will break now"
					break
			else:
				break		
				
		#print "-------------------------"
	return

def arrow(oldx,oldy,x,y,board,pnode,qcol):
	#print "board at start of arrow"
	#print board.config
	#board.print_board()
	#if pnode.state==((3,4),(4,3),(3,2)):
		#print "found in arrow"
	temp_dly=y
	temp_uly=y
	temp_dry=y
	temp_ury=y
	#tempx=x[p]-1
	tempx_dl_list=[]
	tempx_dr_list=[]
	board.config[x][y]=qcol
	#print "Q is at ",x,y,board.config[x][y]
	board.config[oldx][oldy]='.'
	#print "Q removed from",oldx,oldy,board.config[oldx][oldy]
	start = time.clock()
	global limit
	
	for i in range (x+1,len(board.config)):#------------Up-----------
		limit+=1
			
		if limit>3:
			limit=0
			break

		new_board=copy.deepcopy(board)	
		if board.config[i][y]=='.':
			#if pnode.state==((3, 4), (4, 3), (3, 2)): 
				#print"in up*** foundddd",i,y#print "arrow position for ",x,y,"is",i,y
			
			
			if not dict.has_key(((oldx,oldy),(x,y),(i,y))):
				new_board.config[i][y]="x"
				
				#print"before new node"
				#new_board.print_board()
				new_node=Node(((oldx,oldy),(x,y),(i,y)),pnode.level+1,0,new_board,parent=[],child=[])
				#print "board of  up",new_node.state
				#new_node.boards.print_board()
				dict[new_node.state]=copy.deepcopy(new_node)
				
				
				
				#new_node.boards.config[i][y]='x'
				#new_node.boards.config[x][y]='Q'
				#new_node.boards.config[oldx][oldy]='.'
				#nodeQueue.put(new_node)
				nodeQueue.put(copy.deepcopy(new_node))
				Node.addChild(pnode,new_node)
				new_board.config[i][y]="."
			
			
		else:
			
			break

		
	#print " time taken for up arrow: ", time.clock()-start, " seconds@@@@@@@@@@@@@@@@@"
	for j in range (y+1,len(board.config)):#---------------Right---------
		limit+=1
		
		if limit>3:
			limit=0
			break
	
		if board.config[x][j]=='.':
			#print "arrow position for ",x,y,"is",x,j
			
			if not dict.has_key(((oldx,oldy),(x,y),(x,j))):
				new_board=board
				new_board.config[x][j]="x"
				
				new_node=Node(((oldx,oldy),(x,y),(x,j)),pnode.level+1,0,new_board,parent=[],child=[])
				#print "board of right",new_node.state
				#new_node.boards.print_board()
				dict[new_node.state]=copy.deepcopy(new_node)
				
				#nodeQueue.put(new_node)
				nodeQueue.put(copy.deepcopy(new_node))
				Node.addChild(pnode,new_node)
				new_board.config[x][j]="."
		else:
			break
	for i in range (x-1,-1,-1):				#--------------Down------------
		limit+=1
		
		if limit>3:
			limit=0
			break
		if board.config[i][y]=='.':
			#print "arrow position for ",x,y,"is",i,y
			
			if not dict.has_key(((oldx,oldy),(x,y),(i,y))):
				new_board=board
				new_board.config[i][y]="x"
				new_node=Node(((oldx,oldy),(x,y),(i,y)),pnode.level+1,0,new_board,parent=[],child=[])
				#print "board of down",new_node.state
				#new_node.boards.print_board()
				dict[new_node.state]=copy.deepcopy(new_node)
				
				#nodeQueue.put(new_node)
				nodeQueue.put(copy.deepcopy(new_node))
				Node.addChild(pnode,new_node)
				new_board.config[i][y]="."
		else:
			break
	for j in range (y-1,-1,-1):				#--------------Left----------
		limit+=1
		
		if limit>3:
			limit=0
			break
		if board.config[x][j]=='.':
			#print "arrow position for ",x,y,"is",x,j
			
			if not dict.has_key(((oldx,oldy),(x,y),(x,j))):
				new_board=board
				new_board.config[x][j]="x"
				new_node=Node(((oldx,oldy),(x,y),(x,j)),pnode.level+1,0,new_board,parent=[],child=[])
				#print "board of left",new_node.state
				#new_node.boards.print_board()
				dict[new_node.state]=copy.deepcopy(new_node)
				if new_node.state==((3, 4), (4, 3), (3, 2)): 
					print"in left"
				#nodeQueue.put(new_node)
				nodeQueue.put(copy.deepcopy(new_node))
				Node.addChild(pnode,new_node)
				new_board.config[x][j]="."
		else:
			break
	for n in range (0,x): #--------------Down Right--------------
		tempx_dl_list.append(n)
	for j in reversed (tempx_dl_list):
		if limit>3:
			limit=0
			break

		temp_dly=temp_dly+1
		if not(temp_dly)==len(board.config):
			if board.config[j][temp_dly]=='.':
				#print "arrow position for ",x,y,"is",j,temp_dly, board.config[j][temp_dly]
				
				if not dict.has_key(((oldx,oldy),(x,y),(j,temp_dly))):
					limit+=1
					new_board=board
					new_board.config[j][temp_dly]="x"
					new_node=Node(((oldx,oldy),(x,y),(j,temp_dly)),pnode.level+1,0,new_board,parent=[],child=[])
					#print "board of down right",new_node.state
					#new_node.boards.print_board()
					dict[new_node.state]=copy.deepcopy(new_node)
					if new_node.state==((3, 4), (4, 3), (3, 2)): 
						print"in down right"
					#nodeQueue.put(new_node)
					nodeQueue.put(copy.deepcopy(new_node))
					Node.addChild(pnode,new_node)
					new_board.config[j][temp_dly]="."
			else:
				break
		else:
			break
	##start = time.clock()
	for j in range (x+1,len(board.config)): #---------------------Up Right----------------
		temp_uly=temp_uly+1
		if not(temp_uly)==len(board.config):
			if board.config[j][temp_uly]=='.':
				limit+=1
			
				if limit>5:
					limit=0
					break
				#print "arrow position for ",x,y,"is",j,temp_uly, board.config[j][temp_uly]
				
				if not dict.has_key(((oldx,oldy),(x,y),(j,temp_uly))):
					new_board=board
					new_board.config[j][temp_uly]="x"
					
					new_node=Node(((oldx,oldy),(x,y),(j,temp_uly)),pnode.level+1,0,new_board,parent=[],child=[])
					#print "board of up right",new_node.state
					#new_node.boards.print_board()
					dict[new_node.state]=copy.deepcopy(new_node)
					if new_node.state==((3, 4), (4, 3), (3, 2)): 
						print"in up right"
					#nodeQueue.put(new_node)
					nodeQueue.put(copy.deepcopy(new_node))
					Node.addChild(pnode,new_node)
					new_board.config[j][temp_uly]="."
			else:
				break
		else:
			break		
	#print "time taken for top right arrow: ", time.clock()-start, " seconds$$$$$$$$$$$$$"
	for n in range (0,x): #--------------Down Left-------------------
		#print "---",n
		tempx_dr_list.append(n)
	for j in reversed (tempx_dr_list):
		temp_dry=temp_dry-1
		limit+=1
		
		if limit>3:
			limit=0
			break	
		if not(temp_dry)<0:
			if board.config[j][temp_dry]=='.':
				#print "arrow position for ",x,y,"is",j,temp_dry, board.config[j][temp_dry]
				
				if not dict.has_key(((oldx,oldy),(x,y),(j,temp_dry))):
					
					new_board=board
					new_board.config[j][temp_dry]="x"
					new_node=Node(((oldx,oldy),(x,y),(j,temp_dry)),pnode.level+1,0,new_board,parent=[],child=[])
					#print "board of down left",new_node.state
					#new_node.boards.print_board()
					dict[new_node.state]=copy.deepcopy(new_node)
					#nodeQueue.put(new_node)
					nodeQueue.put(copy.deepcopy(new_node))
					Node.addChild(pnode,new_node)
					new_board.config[j][temp_dry]="."
			else:
				break
		else:
			break
	for j in range (x+1,len(board.config)): #----------Up Left----------------
			#print "x is" ,j
		temp_ury=temp_ury-1
			#print "x is" ,j,"y is",temp_ury
		if not(temp_ury)<0:
			if board.config[j][temp_ury]=='.':
				limit+=1
			
				if limit>3:
					limit=0
					break
				#print "arrow position for ",x,y,"is",j,temp_ury, board.config[j][temp_ury]
				
				if not dict.has_key(((oldx,oldy),(x,y),(j,temp_ury))):
					new_board=board
					new_board.config[j][temp_ury]="x"
					new_node=Node(((oldx,oldy),(x,y),(j,temp_ury)),pnode.level+1,0,copy.deepcopy(new_board),parent=[],child=[])
					#print "board of up left",new_node.state
					#new_node.boards.print_board()
					dict[new_node.state]=copy.deepcopy(new_node)
					if new_node.state==((3, 4), (4, 3), (3, 2)): 
						print"in up left"
					#nodeQueue.put(new_node)
					nodeQueue.put(copy.deepcopy(new_node))
					Node.addChild(pnode,new_node)
					new_board.config[j][temp_ury]="."
			else:
				#print"will break now"
				break
		else:
			break
	board.config[x][y]='.'
	board.config[oldx][oldy]=qcol

def heuristic(termi_node,qcol):
	count=0
	unique=0
	#print "termi_node size--------------------------------------------------------------->>> ",termi_node.qsize()
	while not termi_node.empty():
		bcNode=termi_node.get(0)
		bc=bcNode.boards
		#bc.print_board()
		x=[];
		y=[];
	
		for i,r in enumerate(bc.config):
			for j,c in enumerate(r):
				if c==qcol:
					x.append(i)
					y.append(j)
					#print c,i,j
	
		#flag=True
		for p in range(0,len(x)):
			
			temp_dly=y[p]
			temp_uly=y[p]
			temp_dry=y[p]
			temp_ury=y[p]
			#tempx=x[p]-1
			
			for i in range (x[p]+1,6):#------------Up-----------
				
				if bc.config[i][y[p]]=='.':
					count=count+1
					#print i,y[p],'for up',x[p],y[p] 
				else:
					break
			for j in range (y[p]+1,6):#---------------Right---------
				if bc.config[x[p]][j]=='.':
					count=count+1
					#print x[p],j,'for right',x[p],y[p]
				else:
					break
			for i in range (x[p]-1,-1,-1):				#--------------Down------------
				if bc.config[i][y[p]]=='.':
					count=count+1
					#print i,y[p],'for down',x[p],y[p]
				else:
					break
			for j in range (y[p]-1,-1,-1):				#--------------Left----------
				if bc.config[x[p]][j]=='.':
					count=count+1
					#print x[p],j,'for left',x[p],y[p]
				else:
					break
			for j in range (x[p]-1,-1,-1):#--------------Down Right--------------
				temp_dly=temp_dly+1
				if not(temp_dly)==len(bc.config):
					if bc.config[j][temp_dly]=='.':
						count=count+1
						#print j,temp_dly,'for Dright',x[p],y[p]
					else:
						break
				else:
					break
			for j in range (x[p]+1,5): #---------------------Up Right----------------
				temp_uly=temp_uly+1
				if not(temp_uly)==len(bc.config):
					if bc.config[j][temp_uly]=='.':
						count=count+1
						#print j,temp_uly,'for Uright',x[p],y[p]
					else:
						break
				else:
					break		
			for j in range (x[p]-1,-1,-1):#--------------Down Left-------------------
				temp_dry=temp_dry-1	
				if not(temp_dry)<0:
					if bc.config[j][temp_dry]=='.':
						count=count+1
						#print j,temp_dry,'for DLeft',x[p],y[p]
					else:
						break
				else:
					break
			for j in range (x[p]+1,len(bc.config)): #----------Up Left----------------
				temp_ury=temp_ury-1
				
				if not(temp_ury)<0:
					if bc.config[j][temp_ury]=='.':
						count=count+1
						#print j,temp_ury,'for ULeft',x[p],y[p]
					else:					
						break
				else:
					break		
				#flag=False		
		#print "-------------------------count is",count
		Terminal= Node(unique,100,count,bc,parent=[],child=[])
		dict[unique]=Terminal
		Node.addChild(bcNode,Terminal)
		unique=unique+1
		#bcNode.utility=count
		#print bcNode.state ,"has child",bcNode.child[0].state, bcNode.child[0].utility, len(bcNode.child)
		#print";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
		count=0
	
	#print"--------------__________________________________-----------------------------"

def heu2(hnode,board):
	#print"heu2 called", hnode.state
	'''global dict
	if hnode.state==((3,4),(4,3),(3,2)):
		hnode.boards.print_board()
		#print"in dict"
		dict[hnode.state].boards.print_board()
		print dict[((3,4),(4,3),(3,2))].state
		dict[((3,4),(4,3),(3,2))].boards.print_board()
		#print "its parent" ,hnode.parent[0].state'''
	
	
	count=0
	bc=copy.deepcopy(board)
	#bc.print_board()
	x=[];
	y=[];
	
	for i,r in enumerate(bc.config):
		for j,c in enumerate(r):
			if c=='q':
				x.append(i)
				y.append(j)
	for p in range(0,len(x)-2):
		temp_dly=y[p]
		temp_uly=y[p]
		temp_dry=y[p]
		temp_ury=y[p]
			#tempx=x[p]-1
			
		for i in range (x[p]+1,len(bc.config)):#------------Up-----------
			
			if bc.config[i][y[p]]=='.':
				count=count+1
				#print i,y[p],'for up',x[p],y[p] 
			else:
				break
		for j in range (y[p]+1,len(bc.config)):#---------------Right---------
			if bc.config[x[p]][j]=='.':
				count=count+1
				#print x[p],j,'for right',x[p],y[p]
			else:
				break
		for i in range (x[p]-1,-1,-1):				#--------------Down------------
			if bc.config[i][y[p]]=='.':
				count=count+1
				#print i,y[p],'for down',x[p],y[p]
			else:
				break
		for j in range (y[p]-1,-1,-1):				#--------------Left----------
			if bc.config[x[p]][j]=='.':
				count=count+1
				#print x[p],j,'for left',x[p],y[p]
			else:
				break
		for j in range (x[p]-1,-1,-1):#--------------Down Right--------------
			temp_dly=temp_dly+1
			if not(temp_dly)==len(bc.config):
				if bc.config[j][temp_dly]=='.':
					count=count+1
					#print j,temp_dly,'for Dright',x[p],y[p]
				else:
					break
			else:
				break
		for j in range (x[p]+1,len(bc.config)): #---------------------Up Right----------------
			temp_uly=temp_uly+1
			if not(temp_uly)==len(bc.config):
				if bc.config[j][temp_uly]=='.':
					count=count+1
					#print j,temp_uly,'for Uright',x[p],y[p]
				else:
					break
			else:
				break		
		for j in range (x[p]-1,-1,-1):#--------------Down Left-------------------
			temp_dry=temp_dry-1	
			if not(temp_dry)<0:
				if bc.config[j][temp_dry]=='.':
					count=count+1
					#print j,temp_dry,'for DLeft',x[p],y[p]
				else:
					break
			else:
				break
		for j in range (x[p]+1,len(bc.config)): #----------Up Left----------------
			temp_ury=temp_ury-1
			
			if not(temp_ury)<0:
				if bc.config[j][temp_ury]=='.':
					count=count+1
					#print j,temp_ury,'for ULeft',x[p],y[p]
				else:					
					break
			else:
				break		
			#flag=False		
	#print "-------------------------count is",count
	global id
	Terminal= Node((id,id),100,count,bc,parent=[],child=[])
	dict[(id,id)]=Terminal
	#print "added",(id,id)
	#print "inserted into",(id,id), dict[(id,id)].state,count
	id=id+1
	
	Node.addChild(hnode,Terminal)
	#print "returned ",count
	return count
	
def alpha_beta(node):
	v=maxVal(node,-10000,10000)
	return v
	
def maxVal(node,alpha,beta):
	#print "check node",node.state
	
	if len(node.child)<=0 :
		if node.utility==0:
			return heu2(node,node.boards)
		return node.utility;
	v=-10000
	for i in range (0,len(node.child)):
		x=node.child[i] 
		v=max(v,minVal(x,alpha,beta))
		if v>=beta:
			return v
		alpha = max(alpha,v)
	return v
def minVal(node,alpha,beta):
	#print "check node",node.state
	
	if len(node.child)<=0 :
		if node.utility==0:
			return heu2(node,node.boards)
		return node.utility;
	v=10000
	for i in range (0,len(node.child)):
		x=node.child[i] 
		v=min(v,maxVal(x,alpha,beta))
		if v<=alpha:
			return v
		beta = min(beta,v)
	return v
###################### Your code between these two comment lines ####################################
        
def main():
    if len(sys.argv) == 2:
        fname = sys.argv[1]
    else:
        fname = raw_input("setup file name?")
    game = Amazons(fname)
    game.play()

if __name__ == "__main__":
    main()
    

