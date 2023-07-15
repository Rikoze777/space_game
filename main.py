import time
import curses
import asyncio
import random


TIC_TIMEOUT = 0.1


def draw(canvas):
    canvas.border()
    star_sprites = '+*.:'
    window_rows, window_columns = canvas.getmaxyx()
    coroutines = [blink(canvas,
                        row=random.randint(2, window_rows-2),
                        column=random.randint(2, window_columns-2),
                        symbol=random.choice(star_sprites)) for _ in range(20)]
    curses.curs_set(False)
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
            delay = frame['delay']
            for _ in range(delay):
                await asyncio.sleep(0)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
