import time
import curses
import asyncio
from random import randint


def draw(canvas):
    canvas.border()
    coroutines = [blink(canvas,
                        row=5,
                        column=randint(3, 10),
                        symbol='*') for _ in range(6)]
    curses.curs_set(False)
    while True:
        # canvas.addstr(row, column, '*', curses.A_DIM)
        # canvas.refresh()
        # time.sleep(2)
        # canvas.addstr(row, column, '*',)
        # canvas.refresh()
        # time.sleep(0.3)
        # canvas.addstr(row, column, '*', curses.A_BOLD)
        # canvas.refresh()
        # time.sleep(0.5)
        # canvas.addstr(row, column, '*',)
        # canvas.refresh()
        # time.sleep(0.3)
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
