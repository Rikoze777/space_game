import time
import curses
import asyncio
import random
from random import randint


TIC_TIMEOUT = 0.1


def draw(canvas):
    canvas.border()
    coroutines = [blink(canvas,
                        row=5,
                        column=randint(3, 10),
                        symbol='*') for _ in range(6)]
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
