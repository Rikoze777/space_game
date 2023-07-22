import time
import curses
import asyncio
import random
import itertools
from curses_tools import (draw_frame, read_controls,
                          get_frame_size, fire,
                          fly_garbage, blink)
import os, glob


TIC_TIMEOUT = 0.1
SHIP_WIDTH = 5
SHIP_HEIGHT = 10
SPACE_SHIP_ANIMATION_SLOWDOWN = 3
FRAME1 = '''
     .
    .'.
    |o|
   .'o'.
   |.-.|
   '   '
    ( )
     )
    ( )
    '''
FRAME2 = '''
     .
    .'.
    |o|
   .'o'.
   |.-.|
   '   '
     )
    ( )
     (
    '''
ROCKET_FRAMES = [FRAME1, FRAME1, FRAME2, FRAME2]


def check_window_size(canvas):
    window_rows, window_columns = canvas.getmaxyx()
    for frame in ROCKET_FRAMES:
        frame_rows, frame_columns = get_frame_size(frame)
        if frame_rows >= window_rows or frame_columns >= window_columns:
            raise ValueError('The window is too small')


async def animate_spaceship(canvas, rows, columns):
    check_window_size(canvas)

    for frame in itertools.cycle(ROCKET_FRAMES):
        rows_direction, columns_direction, _ = read_controls(canvas)
        draw_frame(canvas, rows, columns, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, rows, columns, frame, negative=True)
        if rows_direction or columns_direction:
            rows += rows_direction
            rows = rows if rows > min(ROW_BORDERS) else min(ROW_BORDERS)
            rows = rows if rows < max(ROW_BORDERS) else max(ROW_BORDERS)

            columns += columns_direction
            columns = columns if columns > min(COLUMN_BORDERS)\
                else min(COLUMN_BORDERS)
            columns = columns if columns < max(COLUMN_BORDERS)\
                else max(COLUMN_BORDERS)


def draw(canvas):
    garbage_path = 'garbage/'
    star_sprites = '+*.:'
    window_rows, window_columns = canvas.getmaxyx()
    blink_tics = random.randint(2, 5)
    global ROW_BORDERS
    global COLUMN_BORDERS
    ROW_BORDERS = (1, window_rows - SHIP_HEIGHT - 1)
    COLUMN_BORDERS = (1, window_columns - SHIP_WIDTH - 1)
    shot = fire(canvas,
                window_rows/2,
                window_columns/2,
                rows_speed=-0.3,
                columns_speed=0)
    space_ship_animation = animate_spaceship(canvas,
                                             window_rows/2,
                                             window_columns/2 - 5)
    coroutines = [blink(canvas,
                        row=random.randint(2, window_rows-2),
                        column=random.randint(2, window_columns-2),
                        offset_tics=blink_tics,
                        symbol=random.choice(star_sprites),)
                  for _ in range(100)]
    for filename in glob.glob(os.path.join(garbage_path, '*.txt')):
        with open(os.path.join(os.getcwd(), filename), 'r') as garbage_file:
            frame = garbage_file.read()
        for _ in range(2):    
            column = random.randint(5, window_columns - 5)
            coroutines.append(fly_garbage(canvas, column, garbage_frame=frame))
    coroutines.append(space_ship_animation)
    coroutines.append(shot)
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
