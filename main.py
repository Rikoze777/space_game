import time
import curses
import asyncio
import random
import itertools

TIC_TIMEOUT = 0.1
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

SPACE_SHIP_ANIMATION_SLOWDOWN = 3

ROCKET_FRAMES = [
    '''
     .
    .'.
    |o|
   .'o'.
   |.-.|
   '   '
    ( )
     )
    ( )
    ''',
    '''
     .
    .'.
    |o|
   .'o'.
   |.-.|
   '   '
     )
    ( )
     (
    ''',
]


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""
    
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
    
    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break
                
            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""
    
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def check_window_size(canvas):
    window_rows, window_columns = canvas.getmaxyx()
    for frame in ROCKET_FRAMES:
        frame_rows, frame_columns = get_frame_size(frame)
        if frame_rows >= window_rows or frame_columns >= window_columns:
            raise ValueError('The window is too small')


async def animate_spaceship(canvas, rows, culumns):
    check_window_size(canvas)

    for frame in itertools.cycle(ROCKET_FRAMES):
        rows_direction, columns_direction, _ = read_controls(canvas)
        rows += rows_direction
        culumns += columns_direction
        draw_frame(canvas, rows, culumns, frame)
        for _ in range(SPACE_SHIP_ANIMATION_SLOWDOWN):
            await asyncio.sleep(0)
        draw_frame(canvas, rows, culumns, frame, negative=True)


def draw(canvas):
    star_sprites = '+*.:'
    window_rows, window_columns = canvas.getmaxyx()
    space_ship_animation = animate_spaceship(canvas,
                                             window_rows/2,
                                             window_columns/2)
    # shot = fire(canvas, window_rows-1,
    #             window_columns/2,
    #             rows_speed=-0.3,
    #             columns_speed=0)
    stars = [blink(canvas,
                   row=random.randint(2, window_rows-2),
                   column=random.randint(2, window_columns-2),
                   symbol=random.choice(star_sprites))
             for _ in range(100)]
    coroutines = stars + [space_ship_animation]
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)
    while True:
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


async def blink(canvas, row, column, symbol='*'):
    frames = [
        {'style': curses.A_DIM, 'delay': 20},
        {'style': curses.A_NORMAL, 'delay': 3},
        {'style': curses.A_BOLD, 'delay': 5},
        {'style': curses.A_NORMAL, 'delay': 3}
    ]

    while True:
        for frame in frames:
            canvas.addstr(row, column, symbol, frame['style'])
            delay = random.randint(2, 5) + frame['delay']
            for _ in range(delay):
                await asyncio.sleep(0)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
