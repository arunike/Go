## Imports
import sys
import random
import pygame
from pygame.locals import *
import pygame.gfxdraw
from collections import namedtuple

Chessman = namedtuple('Chessman', 'Name Value Color') ## Name: Name of the chessman, Value: Value of the chessman, Color: Color of the chessman
Point = namedtuple('Point', 'X Y') ## X: X coordinate, Y: Y coordinate

## Chessman colors
BLACK_CHESSMAN = Chessman('Black', 1, (45, 45, 45)) 
WHITE_CHESSMAN = Chessman('White', 2, (219, 219, 219))

offset = [(1, 0), (0, 1), (1, 1), (1, -1)] ## Directions

## AI class
SIZE = 30
Line_Points = 19
Outer_Width = 20
Border_Width = 4
Inside_Width = 4
Border_Length = SIZE * (Line_Points - 1) + Inside_Width * 2 + Border_Width
Start_X = Start_Y = Outer_Width + int(Border_Width / 2) + Inside_Width
SCREEN_HEIGHT = SIZE * (Line_Points - 1) + Outer_Width * 2 + Border_Width + Inside_Width * 2
SCREEN_WIDTH = SCREEN_HEIGHT + 200

## Colors and radius
Stone_Radius = SIZE // 2 - 3
Stone_Radius2 = SIZE // 2 + 3
Checkerboard_Color = (0xE3, 0x92, 0x65)
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
RED_COLOR = (200, 30, 30)
BLUE_COLOR = (30, 30, 200)

RIGHT_INFO_POS_X = SCREEN_HEIGHT + Stone_Radius2 * 2 + 10 ## X coordinate of the right information

## Checkerboard class
class Checkerboard:
    ## Initialize the checkerboard
    def __init__(self, line_points):
        self._line_points = line_points  ## Number of points in a line
        self._checkerboard = [[0] * line_points for _ in range(line_points)] ## Initialize the checkerboard

    ## Get the checkerboard
    def _get_checkerboard(self):
        return self._checkerboard

    checkerboard = property(_get_checkerboard) ## Checkerboard

    ## Check if the chessman can be dropped
    def can_drop(self, point):
        return self._checkerboard[point.Y][point.X] == 0

    ## Drop the chessman
    def drop(self, chessman, point):
        print(f'{chessman.Name} ({point.X}, {point.Y})')
        self._checkerboard[point.Y][point.X] = chessman.Value ## Drop the chessman

        if self._win(point): ## Check if the chessman wins
            print(f'{chessman.Name} Won!')

            return chessman

    ## Check if the chessman wins
    def _win(self, point): 
        cur_value = self._checkerboard[point.Y][point.X] ## Get the value of the chessman

        for os in offset: ## Check if the chessman wins in the
            if self._get_count_on_direction(point, cur_value, os[0], os[1]):
                return True

    ## Get the number of chessmen in the same direction
    def _get_count_on_direction(self, point, value, x_offset, y_offset):
        count = 1

        for step in range(1, 5): ## Check the chessman in the same direction
            x = point.X + step * x_offset
            y = point.Y + step * y_offset
            if 0 <= x < self._line_points and 0 <= y < self._line_points and self._checkerboard[y][x] == value: ## Check if the chessman is the same
                count += 1
            else: ## If not, break
                break
        for step in range(1, 5): ## Check the chessman in the opposite direction
            x = point.X - step * x_offset
            y = point.Y - step * y_offset
            if 0 <= x < self._line_points and 0 <= y < self._line_points and self._checkerboard[y][x] == value: ## Check if the chessman is the same
                count += 1
            else: ## If not,
                break

        return count >= 5

## Print text
def print_text(screen, font, x, y, text, fcolor = (255, 255, 255)): 
    imgText = font.render(text, True, fcolor)
    screen.blit(imgText, (x, y))

## Main function to run the game
def main(): 
    pygame.init() ## Initialize pygame
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) ## Set the size of the window
    pygame.display.set_caption('Go') ## Set the title of the window

    ## Load the font
    font1 = pygame.font.SysFont('SimHei', 32)
    font2 = pygame.font.SysFont('SimHei', 72)
    fwidth, fheight = font2.size('Black Won!')

    ## Initialize the checkerboard
    checkerboard = Checkerboard(Line_Points)
    cur_runner = BLACK_CHESSMAN
    winner = None
    computer = AI(Line_Points, WHITE_CHESSMAN)

    ## Initialize the number of wins
    black_win_count = 0
    white_win_count = 0

    while True: ## Main loop
        for event in pygame.event.get(): ## Get the event
            if event.type == QUIT: ## If the event is quit, exit
                sys.exit()
            elif event.type == KEYDOWN: ## If the event is keydown
                if event.key == K_RETURN: ## If the key is enter
                    if winner is not None: ## If there is a winner
                        winner = None
                        cur_runner = BLACK_CHESSMAN
                        checkerboard = Checkerboard(Line_Points)
                        computer = AI(Line_Points, WHITE_CHESSMAN)
            elif event.type == MOUSEBUTTONDOWN: ## If the event is mouse button down
                if winner is None: ## If there is no winner
                    pressed_array = pygame.mouse.get_pressed()
                    if pressed_array[0]: ## If the left button is pressed
                        mouse_pos = pygame.mouse.get_pos()
                        click_point = _get_clickpoint(mouse_pos)
                        if click_point is not None: ## If the click point is valid
                            if checkerboard.can_drop(click_point):
                                winner = checkerboard.drop(cur_runner, click_point)
                                if winner is None: ## If there is no winner
                                    cur_runner = _get_next(cur_runner)
                                    computer.get_opponent_drop(click_point)
                                    AI_point = computer.AI_drop()
                                    winner = checkerboard.drop(cur_runner, AI_point)
                                    if winner is not None: ## If there is a winner
                                        white_win_count += 1
                                    cur_runner = _get_next(cur_runner)
                                else: ## If there is a winner
                                    black_win_count += 1

                        else: ## If the click point is invalid
                            print('Invalid click point!')

        _draw_checkerboard(screen) ## Draw the checkerboard``

        for i, row in enumerate(checkerboard.checkerboard): ## Draw the chessman
            for j, cell in enumerate(row): ## Draw the chessman if the cell is white
                if cell == BLACK_CHESSMAN.Value: ## Draw the chessman if the cell is black
                    _draw_chessman(screen, Point(j, i), BLACK_CHESSMAN.Color)
                elif cell == WHITE_CHESSMAN.Value: ## Draw the chessman if the cell is white
                    _draw_chessman(screen, Point(j, i), WHITE_CHESSMAN.Color)

        _draw_left_info(screen, font1, cur_runner, black_win_count, white_win_count) ## Draw the information on the left

        if winner: ## If there is a winner
            print_text(screen, font2, (SCREEN_WIDTH - fwidth) // 2, (SCREEN_HEIGHT - fheight) // 2, winner.Name + ' Won!', RED_COLOR) ## Print the winner

        pygame.display.flip() ## Update the screen

## Get the next runner
def _get_next(cur_runner):
    if cur_runner == BLACK_CHESSMAN: ## If the current runner is black
        return WHITE_CHESSMAN
    else: ## If the current runner is white
        return BLACK_CHESSMAN

## Draw the checkerboard
def _draw_checkerboard(screen):
    screen.fill(Checkerboard_Color) ## Fill the screen with the color of the checkerboard
    pygame.draw.rect(screen, BLACK_COLOR, (Outer_Width, Outer_Width, Border_Length, Border_Length), Border_Width) ## Draw the border of the checkerboard
    
    for i in range(Line_Points): ## Draw the lines of the checkerboard
        pygame.draw.line(screen, BLACK_COLOR, (Start_Y, Start_Y + SIZE * i), (Start_Y + SIZE * (Line_Points - 1), Start_Y + SIZE * i), 1)
    
    for j in range(Line_Points): ## Draw the lines of the checkerboard
        pygame.draw.line(screen, BLACK_COLOR, (Start_X + SIZE * j, Start_X), (Start_X + SIZE * j, Start_X + SIZE * (Line_Points - 1)), 1)

    for i in (3, 9, 15): ## Draw the points of the checkerboard
        for j in (3, 9, 15): ## Draw the points of the checkerboard
            if i == j == 9: ## Draw the points of the checkerboard
                radius = 5
            else: ## Draw the points of the checkerboard
                radius = 3

            ## Draw the points of the checkerboard
            pygame.gfxdraw.aacircle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)
            pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)

## Draw the chessman
def _draw_chessman(screen, point, stone_color):
    pygame.gfxdraw.aacircle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)
    pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)

## Draw the information on the left
def _draw_left_info(screen, font, cur_runner, black_win_count, white_win_count):
    ## Draw the information of the left side
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, Start_X + Stone_Radius2), BLACK_CHESSMAN.Color)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, Start_X + Stone_Radius2 * 4), WHITE_CHESSMAN.Color)

    ## Print the information of the left side
    print_text(screen, font, RIGHT_INFO_POS_X, Start_X + 3, 'Player', BLUE_COLOR)
    print_text(screen, font, RIGHT_INFO_POS_X, Start_X + Stone_Radius2 * 3 + 3, 'AI', BLUE_COLOR)
    print_text(screen, font, SCREEN_HEIGHT, SCREEN_HEIGHT - Stone_Radius2 * 8, 'Score: ', BLUE_COLOR)

    ## Draw the information of the right side
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, SCREEN_HEIGHT - int(Stone_Radius2 * 4.5)), BLACK_CHESSMAN.Color)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, SCREEN_HEIGHT - Stone_Radius2 * 2), WHITE_CHESSMAN.Color)

    ## Print the information of the right side
    print_text(screen, font, RIGHT_INFO_POS_X, SCREEN_HEIGHT - int(Stone_Radius2 * 5.5) + 3, f'{black_win_count} Victory', BLUE_COLOR)
    print_text(screen, font, RIGHT_INFO_POS_X, SCREEN_HEIGHT - Stone_Radius2 * 3 + 3, f'{white_win_count} Victory', BLUE_COLOR)

## Draw the chessman
def _draw_chessman_pos(screen, pos, stone_color):
    pygame.gfxdraw.aacircle(screen, pos[0], pos[1], Stone_Radius2, stone_color)
    pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], Stone_Radius2, stone_color)

## Get the position of the click
def _get_clickpoint(click_pos):
    ## Get the position of the click
    pos_x = click_pos[0] - Start_X
    pos_y = click_pos[1] - Start_Y

    if pos_x < -Inside_Width or pos_y < -Inside_Width: ## If the click is out of the checkerboard
        return None

    ## Get the position of the click
    x = pos_x // SIZE
    y = pos_y // SIZE

    if pos_x % SIZE > Stone_Radius: ## If the click is out of the checkerboard
        x += 1
    if pos_y % SIZE > Stone_Radius: ## If the click is out of the checkerboard
        y += 1
    if x >= Line_Points or y >= Line_Points: ## If the click is out of the checkerboard
        return None

    return Point(x, y)

## AI class
class AI: 
    def __init__(self, line_points, chessman): ## Initialize the AI
        self._line_points = line_points
        self._my = chessman
        self._opponent = BLACK_CHESSMAN if chessman == WHITE_CHESSMAN else WHITE_CHESSMAN
        self._checkerboard = [[0] * line_points for _ in range(line_points)]

    ## Get the opponent's drop
    def get_opponent_drop(self, point):
        self._checkerboard[point.Y][point.X] = self._opponent.Value

    ## AI drop phrase
    def AI_drop(self):
        point = None
        score = 0

        for i in range(self._line_points):
            for j in range(self._line_points):
                if self._checkerboard[j][i] == 0:
                    _score = self._get_point_score(Point(i, j))
                    if _score > score:
                        score = _score
                        point = Point(i, j)
                    elif _score == score and _score > 0:
                        r = random.randint(0, 100)
                        if r % 2 == 0:
                            point = Point(i, j)

        self._checkerboard[point.Y][point.X] = self._my.Value

        return point

    def _get_point_score(self, point): ## Get the score of the point
        score = 0

        for os in offset: ## Get the score of the point
            score += self._get_direction_score(point, os[0], os[1])

        return score

    def _get_direction_score(self, point, x_offset, y_offset): ## Get the score of the point
        count = 0
        _count = 0
        space = None
        _space = None
        both = 0
        _both = 0

        flag = self._get_stone_color(point, x_offset, y_offset, True)

        if flag != 0:
            for step in range(1, 6):
                x = point.X + step * x_offset
                y = point.Y + step * y_offset
                if 0 <= x < self._line_points and 0 <= y < self._line_points:
                    if flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _both += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break
                    elif flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            _both += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _count += 1
                            if _space is False:
                                _space = True
                        else:
                            if _space is None:
                                _space = False
                            else:
                                break
                else:
                    if flag == 1:
                        both += 1
                    elif flag == 2:
                        _both += 1

        if space is False:
            space = None
        if _space is False:
            _space = None

        _flag = self._get_stone_color(point, -x_offset, -y_offset, True)

        if _flag != 0:
            for step in range(1, 6):
                x = point.X - step * x_offset
                y = point.Y - step * y_offset
                if 0 <= x < self._line_points and 0 <= y < self._line_points:
                    if _flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _both += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break
                    elif _flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            _both += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _count += 1
                            if _space is False:
                                _space = True
                        else:
                            if _space is None:
                                _space = False
                            else:
                                break
                else:
                    if _flag == 1:
                        both += 1
                    elif _flag == 2:
                        _both += 1

        score = 0

        if count == 4:
            score = 10000
        elif _count == 4:
            score = 9000
        elif count == 3:
            if both == 0:
                score = 1000
            elif both == 1:
                score = 100
            else:
                score = 0
        elif _count == 3:
            if _both == 0:
                score = 900
            elif _both == 1:
                score = 90
            else:
                score = 0
        elif count == 2:
            if both == 0:
                score = 100
            elif both == 1:
                score = 10
            else:
                score = 0
        elif _count == 2:
            if _both == 0:
                score = 90
            elif _both == 1:
                score = 9
            else:
                score = 0
        elif count == 1:
            score = 10
        elif _count == 1:
            score = 9
        else:
            score = 0

        if space or _space:
            score /= 2

        return score

    ## Get the color of the stone
    def _get_stone_color(self, point, x_offset, y_offset, next):
        ## Get the position of the stone
        x = point.X + x_offset
        y = point.Y + y_offset

        if 0 <= x < self._line_points and 0 <= y < self._line_points: ## If the point is in the checkerboard
            if self._checkerboard[y][x] == self._my.Value: ## If the stone is my stone
                return 1
            elif self._checkerboard[y][x] == self._opponent.Value: ## If the stone is opponent's stone
                return 2
            else: ## If the stone is empty
                if next: ## If the stone is empty and the next stone is not empty
                    return self._get_stone_color(Point(x, y), x_offset, y_offset, False)
                else: ## If the stone is empty and the next stone is empty
                    return 0
        else: ## If the point is not in the checkerboard
            return 0

if __name__ == '__main__':
    main()