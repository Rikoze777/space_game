import time
import curses
import asyncio
import random


TIC_TIMEOUT = 0.1


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


def draw(canvas):
    canvas.border()
    star_sprites = '+*.:'
    window_rows, window_columns = canvas.getmaxyx()
    shot = fire(canvas, window_rows-1,
                window_columns/2,
                rows_speed=-0.3,
                columns_speed=0)
    coroutines = [blink(canvas,
                        row=random.randint(2, window_rows-2),
                        column=random.randint(2, window_columns-2),
                        symbol=random.choice(star_sprites))
                  for _ in range(100)]
    curses.curs_set(False)
    while True:
        shot.send(None)
        try:
            for coroutine in coroutines.copy():
                coroutine.send(None)
        except StopIteration:
            coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
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
