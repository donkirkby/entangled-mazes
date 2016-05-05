import math
from math import atan2, pi
from random import Random
import turtle

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.platypus.flowables import Flowable, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from maze import MazePage, generateMazePair
from pdf_turtle import PdfTurtle
from cherrypy.test.sessiondemo import page

class PdfMaze(object):
    ROOT2 = math.sqrt(2)
    def __init__(self, page):
        self.page = page
        
    def draw(self, t):
        """ Draw a page of the maze using turtle graphics.
        
        @param page: a MazePage object to draw
        @param t: a turtle graphics object
        """
        screen_width = t.window_width()
        screen_height = t.window_height()
        width, height = self.page.size
        cell_size = min(screen_width/width, screen_height*0.9/height)
        t.penup()
        t.goto(-cell_size*width/2, -cell_size*height/2)
        for y in range(height):
            for x in range(width):
                self.drawCell(x, y, t, cell_size)
                t.fd(cell_size)
            t.back(cell_size*width)
            t.left(90)
            t.fd(cell_size)
            t.right(90)
    
    def drawCell(self, x, y, t, cell_size):
        margin = cell_size/5
        symbol_size = cell_size - 2 * margin
        cell = self.page[x][y]
        old_pen = t.width()
        if (x, y) in (self.page.start, self.page.goal):
            t.pendown()
            if (x, y) == self.page.goal:
                t.width(old_pen * 4)
            for _ in range(4):
                t.fd(cell_size)
                t.left(90)
            t.width(old_pen)
        t.penup()
        t.left(45)
        t.fd(margin * PdfMaze.ROOT2)
        t.right(45)
        exits = cell.exits
        if not exits:
            self.drawX(t, symbol_size)
        else:
            self.drawArrow(t, symbol_size, exits)
        t.left(45)
        t.back(margin * PdfMaze.ROOT2)
        t.right(45)
        pass
    
    def drawX(self, t, size):
        t.left(45)
        t.pendown()
        t.fd(size * PdfMaze.ROOT2)
        t.penup()
        t.right(45)
        t.back(size)
        t.right(45)
        t.pendown()
        t.fd(size * PdfMaze.ROOT2)
        t.penup()
        t.left(45)
        t.back(size)
    
    def drawArrow(self, t, size, exits):
        xdir = ydir = 0
        for dx, dy in exits:
            xdir += dx
            ydir += dy
        if xdir and ydir:
            arrow_size = size * PdfMaze.ROOT2
        else:
            arrow_size = size
        arrow_dir = atan2(ydir, xdir)/pi*180
        t.left(45)
        t.fd(size/2 * PdfMaze.ROOT2)
        t.right(45)
        t.seth(arrow_dir)
        t.back(arrow_size/2)
        t.pendown()
        t.fd(arrow_size)
        t.penup()
        t.begin_fill()
        t.left(150)
        t.fd(size/5)
        t.left(120)
        t.fd(size/5)
        t.left(120)
        t.fd(size/5)
        t.right(30)
        t.end_fill()
        t.back(arrow_size/2)
        t.seth(45)
        t.back(size/2 * PdfMaze.ROOT2)
        t.right(45)

def generatePage():
    page = MazePage(name='Page 1', size=(3, 4), start=(0, 0), goal=(2, 3))
    
    random = Random()
    for _ in range(30):
        page.mutate(random)
    return page
    
class TurtleArt(Flowable):
    def __init__(self, page):
        self.page = page
        
    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        self.height = availHeight
        return (availWidth, availHeight)
        
    def draw(self):
        t = PdfTurtle(self.canv, self._frame)
        PdfMaze(self.page).draw(t)

def main():
    doc = SimpleDocTemplate("example.pdf")
    styles = getSampleStyleSheet()
    story = []
    pages = generateMazePair()
    for page in pages:
        story.append(Paragraph(page.name, styles['Normal']))
        story.append(Spacer(1,0.055*inch))
        story.append(TurtleArt(page))
    doc.build(story)
    ## Uncomment this to display the PDF after you generate it.
    #from subprocess import call
    #call(["evince", "example.pdf"])
    
if __name__ == '__main__':
    main()
elif __name__ == '__live_coding__':
    page = generatePage()
    pdf = PdfMaze(page)
    pdf.draw(turtle)
