import unittest

from maze import Cell, MazePage, InvalidExitError
    
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

class CellTest(unittest.TestCase):
    def testHasExit(self):
        cell = Cell((1, 0))
        
        self.assertTrue(cell.hasExit(1, 0))
        self.assertFalse(cell.hasExit(-1, 0))

    def testFromArrows(self):
        cell = Cell('^>')
        
        self.assertTrue(cell.hasExit(1, 0))
        self.assertFalse(cell.hasExit(-1, 0))
        
    def testAddExit(self):
        cell = Cell()
        cell.addExit(1, 0)
        
        self.assertTrue(cell.hasExit(1, 0))
        self.assertFalse(cell.hasExit(-1, 0))

    def testAddOpposite(self):
        cell = Cell()
        cell.addExit(1, 0)
        
        with self.assertRaises(InvalidExitError) as result:
            cell.addExit(-1, 0)
        
        self.assertEqual('Invalid exit (-1, 0) when (1, 0) is present.',
                         result.exception.message)
        
    def testRemoveExit(self):
        cell = Cell()
        cell.addExit(1, 0)
        
        cell.removeExit(1, 0)
        
        self.assertFalse(cell.hasExit(1, 0))

    def testString(self):
        cell = Cell((0, -1))
        
        s = repr(cell)
        
        self.assertEqual("Cell('v')", s)

class MazePageTest(unittest.TestCase):
    def testIndexing(self):
        page = MazePage(size=(3, 2))
        page[1][0].addExit(+1, 0)
          
        has_exit = page[1][0].hasExit(+1, 0)
        self.assertTrue(has_exit)
    
    def testMove(self):
        page = MazePage(size=(3, 2), start=(1,0))
        page[1][0].addExit(0, 1)
        
        pos1 = page.pos
        page.move(0, 1)
        pos2 = page.pos
          
        self.assertEqual((1,0), pos1)
        self.assertEqual((1,1), pos2)

    def testString(self):
        page = MazePage(name='Page 1', size=(2, 3), start=(0, 0))
        
        s = repr(page)
        
        self.assertEqual("MazePage('Page 1')", s)
        
    def testSolve(self):
        page1 = MazePage(name='1', size=(3, 2), start=(1, 0), goal=(1, 1))
        page2 = MazePage(name='2', size=(3, 2), start=(2, 1), goal=(2, 1))
        page2[2][1].addExit(0, 1)
        
        moves = page1.solve(page2)
        
        self.assertEqual([(page1, 0, 1)], moves)

    def testSolveTwice(self):
        page1 = MazePage(name='1', size=(3, 2), start=(1, 0), goal=(1, 1))
        page2 = MazePage(name='2', size=(3, 2), start=(2, 1), goal=(2, 1))
        page2[2][1].addExit(0, 1)
        
        page1.solve(page2) # ignore first result
        moves = page1.solve(page2) # repeat the call
        
        self.assertEqual([(page1, 0, 1)], moves)

    def testNoSolution(self):
        page1 = MazePage(name='1', size=(3, 2), start=(1, 0), goal=(1, 1))
        page2 = MazePage(name='2', size=(3, 2), start=(2, 1), goal=(2, 1))
        page2[2][1].addExit(0, -1)
        
        moves = page1.solve(page2)
        
        self.assertEqual(None, moves)

    def testMoveError(self):
        page1 = MazePage(name='1', size=(3, 2), start=(2, 0), goal=(1, 1))
        page2 = MazePage(name='2', size=(3, 2), start=(2, 1), goal=(2, 1))
        page2[2][1].addExit(1, 0)
        
        moves = page1.solve(page2)
        
        self.assertEqual(None, moves)

    def testBacktrackSolution(self):
        page1 = MazePage(name='1', size=(3, 2), start=(1, 0), goal=(2, 0))
        page2 = MazePage(name='2', size=(3, 2), start=(2, 1), goal=(2, 1))
        page2[2][1].addExit(0, 1)
        page2[2][1].addExit(1, 0)
        
        moves = page1.solve(page2)
        
        self.assertEqual([(page1, 1, 0)], moves)

    def testPartnerSolution(self):
        page1 = MazePage(name='1', size=(3, 2), start=(1, 0), goal=(2, 0))
        page2 = MazePage(name='2', size=(3, 2), start=(2, 1), goal=(2, 0))
        page2[2][1].addExit(1, 0)
        page1[2][0].addExit(0, -1)
        
        moves = page1.solve(page2)
        
        self.assertEqual([(page1, 1, 0), (page2, 0, -1)], moves)
        
    def testMutate(self):
        random = DummyRandom(randints={(0, 2): [1],  # x
                                       (0, 3): [2]}, # y
                             choiceIndexes=[3])
        page = MazePage(size=(3, 4), start=(1, 0), goal=(2, 0))
        
        page.mutate(random)
        
        exits = page[1][2].exits
        self.assertEqual(set([(0, -1)]), exits)

    def testMutateRemoval(self):
        random = DummyRandom(randints={(0, 2): [1],  # x
                                       (0, 3): [2]}, # y
                             choiceIndexes=[3])
        page = MazePage(size=(3, 4), start=(1, 0), goal=(2, 0))
        page[1][2].addExit(0, -1)
        
        page.mutate(random)
        
        exits = page[1][2].exits
        self.assertEqual(set(), exits)

    def testMutateOpposite(self):
        random = DummyRandom(randints={(0, 2): [1],  # x
                                       (0, 3): [2]}, # y
                             choiceIndexes=[3])
        page = MazePage(size=(3, 4), start=(1, 0), goal=(2, 0))
        page[1][2].addExit(0, 1)
        
        page.mutate(random)
        
        exits = page[1][2].exits
        self.assertEqual(set([(0, -1)]), exits)

    def testCycle(self):
        page1 = MazePage(name='1', size=(2, 2), start=(0, 0), goal=(1, 1))
        page2 = MazePage(name='2', size=(2, 2), start=(0, 0), goal=(1, 1))
        page2[0][0].addExit(1, 0)
        page2[1][0].addExit(-1, 0)
        page1[1][0].addExit(1, 0)
        page1[0][0].addExit(-1, 0)
        
        moves = page1.solve(page2)
        
        self.assertEqual(None, moves)

    def testFormat(self):
        page = MazePage(name='1', size=(3, 2), start=(0, 0), goal=(1, 1))
        page[0][0].addExit(1, 0)
        page[1][0].addExit(-1, 0)
        expectedDisplay = """\
1:
 x Gx  x 
S>  <  x 
"""
        
        display = page.display()
        
        self.assertMultiLineEqual(expectedDisplay, display)
