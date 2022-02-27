import curses
import sys
import os

y = 0
posy = 0
x = 0
posx = 0
lines = []

def checkX(cols):
    global y, posy, x, posx, lines
    if posx + x > len(lines[posy + y]) - 1:
        if len(lines[posy + y]) < cols:
            posx = 0
        else:
            posx = x - cols + 1
        x = len(lines[posy + y]) - posx - 1

def checkY(rows):
    global y, posy, x, posx, lines
    if y < posy:
        posy = 0
    if posy + y > rows - 2:
        if len(lines) < rows:
            posy = 0
        else:
            posy = y + 2 - rows
        y = y - posy

def padStr(size, *strings):
    strings = [str(string) for string in strings]
    endStr = ' '.join(strings[1:])
    string = strings[0] + ' ' * (size - len(strings[0] + endStr)) + endStr
    return string

def modeStr(mode):
    if mode == 'None':
        return ''
    elif ':' in mode:
        return mode
    else:
        return ' --' + mode + '--'

def main(stdscr, file):
    global y, posy, x, posx, lines
    key = ''
    mode = 'None'
    quit = False
    curses.set_escdelay(50)
    stdscr.clear()
    
    curses.curs_set(1)
    rows, cols = stdscr.getmaxyx()
    
    if os.path.exists(file):
        with open(file, 'r') as f:
            for line in f:
                lines.append(line.replace('\t', '    ').replace('\r', '\n').replace('\n\n', '\n'))
    else:
        lines.append('')
    
    while not quit:
        if x < 0: x = 0
        elif x >= cols - 1: x = cols - 1
        if y < 0: y = 0
        elif y >= rows - 1: y = rows - 2
        
        for i in range(rows - 1):
            if i >= len(lines):
                stdscr.addstr(i, 0, '~' + ' ' * (cols - 2))
            else:
                stdscr.addstr(i, 0,  padStr(cols - 1, lines[i + posy][posx:posx + cols - 1]))
        stdscr.addstr(rows - 1, 0, padStr(cols - 1, modeStr(mode), x + posx, y + posy))
        stdscr.move(y, x)
        stdscr.refresh()

        key = stdscr.getch()
        cont = True
        if key == curses.KEY_RESIZE:
            x = 0
            y = 0
            posy = 0
            rows, cols = stdscr.getmaxyx()
        elif key == curses.KEY_DOWN:
            if posy + y < len(lines) - 1:
                if posy + rows < len(lines) and posy + y > rows // 3 * 2:
                    posy += 1
                elif y < rows - 2:
                    y += 1
                checkX(cols)
        elif key == curses.KEY_UP:
            if posy > 0 and y < rows // 3:
                posy -= 1
            elif y > 0:
                y -= 1
            checkX(cols)
        elif key == curses.KEY_RIGHT:
            if x < cols and x < len(lines[posy + y]) - 1:
                if posx + cols < len(lines[posy + y]) and posx + x > cols // 3 * 2:
                    posx += 1
                elif x < cols - 1:
                    x += 1
        elif key == curses.KEY_LEFT:
            if posx > 0 and x < cols // 3:
                posx -= 1
            elif x > 0:
                x -= 1
        elif key == 27: #ESC
            mode = 'None'
        elif key == curses.KEY_HOME:
            posx = 0
            x = 0
        elif key == curses.KEY_END:
            x = len(lines[posy + y]) - 1
            if x > cols:
                posx = x - cols + 1
                x = cols - 1
        else:
            cont = False
            
        if cont: continue
        if mode == 'None':
            if key == ord(':'):
                mode = ':'
            elif key == ord('i'):
                mode = 'insert'
        elif mode.startswith(':'):
            if key == curses.KEY_BACKSPACE:
                mode = mode[0: len(mode) - 1]
                if mode == '': mode = 'None'
            elif key == ord('\n'):
                if mode[1:].isnumeric():
                    y = int(mode[1:])
                    checkY(rows)
                    x = 0
                if 'w' in mode:
                    with open(file, 'w') as w:
                        for line in lines:
                            if not line.endswith('\n'):
                                w.write(line + '\n')
                            else:
                                w.write(line)
                if 'q' in mode:
                    quit = True
                mode = 'None'
            else:
                mode += chr(key)
        elif mode == 'insert':
            if key == curses.KEY_BACKSPACE:
                if x > 0:
                    lines[posy + y] = lines[posy + y][0:x - 1] + lines[posy + y][x:]
                    x -= 1
                elif posy + y > 0:
                    x = len(lines[posy + y - 1])
                    lines[posy + y - 1] = lines[posy + y - 1][0:] + lines[posy + y]
                    lines.pop(posy + y)
                    y -= 1
            elif key == curses.KEY_DC:
                if x < len(lines[posy + y]) - 1:
                    lines[posy + y] = lines[posy + y][0:x] + lines[posy + y][x + 1:]
                elif posy + y < len(lines):
                    x = len(lines[posy + y - 1]) - 1
                    lines[posy + y] = lines[posy + y][0:-1] + lines[posy + y + 1]
                    lines.pop(posy + y + 1)
            elif key == ord('\n'):
                temp = lines[posy + y][x:]
                lines[posy + y] = lines[posy + y][0:x]
                if not temp.endswith('\n'): temp += '\n'
                lines.insert(posy + y + 1, temp)
                x = 0
                y += 1
            elif key == ord('\t'):
                if x <= len(lines[posy + y]):
                    lines[posy + y] = lines[posy + y][0:x] + '    ' + lines[posy + y][x:]
                else:
                    lines[posy + y] += '    '
                x += 4
            else:
                if x <= len(lines[posy + y]):
                    lines[posy + y] = lines[posy + y][0:x] + chr(key) + lines[posy + y][x:]
                else:
                    lines[posy + y] += chr(key)
                x += 1
            

if len(sys.argv) != 2:
    print('Filename must be included')
    sys.exit()

file = sys.argv[1]
curses.wrapper(main, file)

