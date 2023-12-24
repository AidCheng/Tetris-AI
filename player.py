from board import Direction, Rotation, Action
from random import Random
import time

class Player:
    def __init__(self):
        self.best_board = None
        
    
    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)

    def move_to_target(self, cloned_board, target_x):
        has_landed = False
        while has_landed == False and target_x < cloned_board.falling.left:
            has_landed = cloned_board.move(Direction.Left)
        while has_landed == False and target_x > cloned_board.falling.left:
            has_landed = cloned_board.move(Direction.Right)

        return has_landed

    def rotate_block(self,board):
        board.falling.rotate(Rotation.Clockwise,board)
    
    def calculate_landing_height(self,blocks):
        print(blocks)
        max_height = 0
        for (x,y) in blocks:
            height = 24-y
            if height > max_height:
                max_height = height
        return max_height
    
    def calculate_height(self,board):
        colomn_heights = 0
        for x in range (board.width):
            for y in range (board.height):
                if (x,y) in board.cells:
                    colomn_heights += (board.height - y)
                    break
        return colomn_heights
                      
    def calculate_hole(self, board, height):
        hole = 0
        height = 24 - height
        for x in range (board.width):
            start_counting = False
            for y in range (height,board.height):
                if (x,y) in board.cells:
                    start_counting = True
                if start_counting is True:
                    if (x,y) not in board.cells:
                        hole += 1
        return hole

    
    def check_eliminate(self,block,pre_block):
        score_added = block.score - pre_block.score
        height = self.heights(block)

        if score_added >= 400:
            return score_added ** 5
        if score_added < 200 and score_added > 25 and max(height) <= 13:
            return -1000
        if score_added >= 200 and score_added < 400 and max(height) <= 13:
            return -100
        else:
            return 0

    def calculate_bumpiness(self, board):
        colomn_heights = []
        for x in range (board.width):
            for y in range (board.height):
                if (x,y) in board.cells:
                    colomn_heights.append(board.height - y)
                    break
                if y == board.height - 1:
                    colomn_heights.append(0)
        
        bumpiness = 0
        for i in range(len(colomn_heights)-1):
            bumpiness += abs(colomn_heights[i] - colomn_heights[i+1])
        
        return bumpiness ** 1.1

    def calculate_score(self,board, preboard):
        previous_cells = preboard.cells.copy()
        new_cells = board.cells.copy()
        landed_block = new_cells.copy()
        
        for sets in previous_cells:
            if sets in landed_block:
                landed_block.remove(sets)
        
        height = self.calculate_height(board)
        eliminate = self.check_eliminate(board, preboard)
        landing_height = self.calculate_landing_height(landed_block)
        holes = self.calculate_hole(board, height)
        bumpiness = self.calculate_bumpiness(board)
        
        self.print_board(board)    
        print(f"height:{height}, landing_height{landing_height}, holes{holes}, bumpiness{bumpiness}")
        
        score = - 0.1 * (max(self.heights(board)) ** 3)  - 1000 * holes - 100 * bumpiness + eliminate

        return score
     
    def heights(self,board):
        colomn_heights = []
        for x in range (board.width):
            for y in range (board.height):
                if (x,y) in board.cells:
                    colomn_heights.append(board.height - y)
                    break
                if y == board.height - 1:
                    colomn_heights.append(0)
        return colomn_heights
        
            
    def find_top_score(self, score):
        max_move = 0
        max_score = score[0]
        for i in range(len(score)):
            if score[i] > max_score:
                max_move = i
                max_score = score[i]
        print("bast score",max_score)
        return max_move         
    
    def the_top_score(self, score):
        max_move = 0
        max_score = score[0]
        for i in range(len(score)):
            if score[i] > max_score:
                max_move = i
                max_score = score[i]
        return max_score       
    
    def to_discard(self,ori_board):
        previous_score = ori_board.score
        board = ori_board.clone()
        board.falling = board.next
        score = []
        
        temp_board = None
        for i in range(0,4):
            if temp_board is None:
                board_to_rotate = board.clone()
            else:
                board_to_rotate = temp_board.clone()
            
            board_to_rotate.rotate(Rotation.Clockwise)
            temp_board = board_to_rotate.clone()
            
            for target_x in range (board.width):
                cloned_board = board_to_rotate.clone()
                if cloned_board.falling is not None:
                    has_landed = False
                    has_landed = self.move_to_target(cloned_board, target_x)
                    if not has_landed:
                        cloned_board.move(Direction.Drop)
                    score.append(cloned_board.score - previous_score)
                else:
                    return
        
        if max(score) > 1000:
            return True
        return False
        

        
        
    def choose_action(self, board):       
        if board.falling is None:
            return Direction.Down
            
        elif board.falling is not None: 
            
            discard = self.to_discard(board)
            if discard is True and board.discards_remaining > 0:
                return Action.Discard
            
            score = []
            movement = [{"left":0,"rotate":0}]
            self.print_board(board)
            move = 0
            temp_board = None
            
            for i in range(0,4):
                if temp_board is None:
                    board_to_rotate = board.clone()
                else:
                    board_to_rotate = temp_board.clone()
                
                board_to_rotate.rotate(Rotation.Clockwise)
                movement[move]["rotate"] = (i+1)%4
                temp_board = board_to_rotate.clone()
                
                for target_x in range (board.width):
                    cloned_board = board_to_rotate.clone()
                    if cloned_board.falling is not None:
                        movement[move]["left"] = cloned_board.falling.left - target_x
                    else: 
                        return
                    
                    has_landed = False
                    has_landed = self.move_to_target(cloned_board, target_x)
                    if not has_landed:
                        cloned_board.move(Direction.Drop)
                    
                    score.append(self.calculate_score(cloned_board, board))
                   
                    if self.calculate_score(cloned_board, board) >= max(score):
                        best_board = cloned_board.clone()
                   
                    print("current score",score[move], movement[move])
                    
                    movement.append({"left":0,"rotate":movement[move]["rotate"]})
                    move += 1
        
            
            moves = self.find_top_score(score)
            actions = []
            
            for i in range(movement[moves]["rotate"]):
                actions.append(Rotation.Clockwise)
            
            if movement[moves]["left"] >= 0:
                for i in range(movement[moves]["left"]):
                    actions.append(Direction.Left)
            
            else:
                for i in range(-(movement[moves]["left"])):
                    actions.append(Direction.Right)
            
            column_heights = self.heights(best_board)
            if max(column_heights) > 16:
                if board.bombs_remaining > 0:
                    actions.append(Action.Bomb)
                elif board.discards_remaining > 0:
                    return Action.Discard
                
            actions.append(Direction.Drop)
            print(actions)
            return actions
        

            
        
        

class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)
                

            

    def choose_action(self, board):
        self.print_board(board)
        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])

SelectedPlayer = Player
