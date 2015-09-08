from random import Random
class Cell(object):
    EXITS = ((1, 0), (0, 1), (-1, 0), (0, -1))
    ARROWS = '>^<v'
    
    def __init__(self, *exits):
        self.exits = set()
        for e in exits:
            if e in Cell.EXITS:
                self.exits.add(e)
            else:
                for arrow in e:
                    arrow_index = Cell.ARROWS.index(arrow)
                    if arrow_index >= 0:
                        self.exits.add(Cell.EXITS[arrow_index])


    def display(self):
        arrow_map = dict(zip(Cell.EXITS, Cell.ARROWS))
        arrow = ''.join((arrow_map[e] for e in sorted(self.exits)))
        return arrow or 'x'

    def __repr__(self):
        return 'Cell({!r})'.format(self.display())
    
    def addExit(self, dx, dy):
        e = dx, dy
        opposite = -dx, -dy
        if opposite in self.exits:
            raise InvalidExitError(
                'Invalid exit {} when {} is present.'.format(e, opposite))
        self.exits.add(e)
    
    def removeExit(self, dx, dy):
        self.exits.remove((dx, dy))
    
    def hasExit(self, dx, dy):
        return (dx, dy) in self.exits

class MoveError(RuntimeError):
    pass

class InvalidExitError(RuntimeError):
    pass

class MultipleSolutionsError(RuntimeError):
    pass

class MazePage(object):
    def __init__(self, name=None, size=None, start=None, goal=None):
        self.name = name
        width, height = size or (0, 0)
        self.pos = self.start = start
        self.goal = goal
        self.cells = []
        for _ in range(width):
            col = []
            for _ in range(height):
                col.append(Cell())
            self.cells.append(col)
    
    def __getitem__(self, i):
        return self.cells[i]
    
    def __repr__(self):
        if self.name is None:
            args = ''
        else:
            args = repr(self.name)
        return 'MazePage({})'.format(args)
    
    def move(self, dx, dy):
        x, y = self.pos
        x += dx
        y += dy
        width = len(self.cells)
        height = len(self.cells[0])
        if not (0 <= x < width and 0 <= y < height):
            raise MoveError('Invalid position ({}, {})'.format(x, y))
        self.pos = (x, y)
    
    def getCurrentExits(self):
        """ Get the exits allowed on the current position.
        
        @return: [(dx, dy)]
        """
        x, y = self.pos
        return self[x][y].exits
        
    def solve(self, partner, history=None):
        if history is None:
            history = []
        solution = None
        max_sidetrack_depth = 0
        for dx, dy in partner.getCurrentExits():
            try:
                self.move(dx, dy)
                try:
                    if self.pos == self.goal and partner.pos == partner.goal:
                        if solution:
                            raise MultipleSolutionsError()
                        solution = [(self, dx, dy)]
                    else:
                        state = (self, self.pos, partner, partner.pos)
                        if state in history:
                            continue
                        history.append(state)
                        moves, sidetrack_depth = partner.solve(self, history)
                        max_sidetrack_depth = max(sidetrack_depth,
                                                  max_sidetrack_depth)
                        if moves is not None:
                            if solution:
                                raise MultipleSolutionsError()
                            moves.insert(0, (self, dx, dy))
                            solution = moves
                        history.pop()
                finally:
                    self.move(-dx, -dy)
            except MoveError:
                pass
        if solution is None:
            max_sidetrack_depth += 1
        return solution, max_sidetrack_depth
    
    def mutate(self, random):
        width = len(self.cells)
        height = len(self.cells[0])
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        e = random.choice(Cell.EXITS)
        cell = self.cells[x][y]
        if cell.hasExit(*e):
            cell.removeExit(*e)
        else:
            opposite = (-e[0], -e[1])
            if cell.hasExit(*opposite):
                cell.removeExit(*opposite)
            cell.addExit(*e)
    
    def display(self):
        if self.name:
            display = self.name + ':'
        else:
            display = ''
        display += '\n'
        width = len(self.cells)
        height = len(self.cells[0])
        for i in range(height):
            y = height-i-1
            for x in range(width):
                pos = (x, y)
                if pos == self.goal:
                    display += 'G'
                elif pos == self.start:
                    display += 'S'
                else:
                    display += ' '
                cell_display = self.cells[x][y].display()
                if len(cell_display) == 1:
                    cell_display += ' '
                display += cell_display
            display += '\n'
        return display

if __name__ == '__main__':
    print 'Searching...'
    page1 = MazePage(name='Page 1', size=(3, 4), start=(0, 0), goal=(2, 3))
    page2 = MazePage(name='Page 2', size=(3, 4), start=(0, 1), goal=(2, 2))
    
    random = Random()
    moves = None
    sidetrack_depth = 0
    while moves is None or sidetrack_depth != 2:
        page1.mutate(random)
        page2.mutate(random)
        try:
            moves, sidetrack_depth = page1.solve(page2)
        except MultipleSolutionsError:
            pass
    
    print 'Found.'
    print page1.display()
    print page2.display()
    print moves
elif __name__ == '__live_coding__':
    import unittest
    def testSomething(self):
        page1 = MazePage(name='1', size=(3, 2), start=(1, 0), goal=(1, 1))
        page2 = MazePage(name='2', size=(3, 2), start=(2, 1), goal=(2, 1))
        page2[2][1].addExit(0, 1)
        
        moves, sidetrack_depth = page1.solve(page2)
        
        self.assertEqual([(page1, 0, 1)], moves)
        self.assertEqual(0, sidetrack_depth)
    
    class DummyRandom(object):
        def __init__(self, choiceIndexes=None, randints=None):
            self.choiceIndexes = choiceIndexes or []
            self.randints = randints or []
            
        def choice(self, seq):
            choiceIndex = self.choiceIndexes.pop(0)
            for i, item in enumerate(seq):
                if i == choiceIndex:
                    return item
            raise IndexError(choiceIndex)
        
        def randint(self, a, b):
            return self.randints[(a, b)].pop(0)
        
    class DummyTest(unittest.TestCase):
        
        def test_delegation(self):
            testSomething(self)

    suite = unittest.TestSuite()
    suite.addTest(DummyTest("test_delegation"))
    test_results = unittest.TextTestRunner().run(suite)

    print(test_results.errors)
    print(test_results.failures)
