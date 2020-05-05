from PySide2 import QtCore, QtGui, QtWidgets
import random
import sys

cell_size = 20  # 每格的宽度
Columns = 12
Rows = 20

NoShape, ZShape, SShape, LineShape, \
TShape, SquareShape, LShape, MirroredLShape = range(8)

# 定义各种形状 字典
SHAPES = [ [],
    [(-1, -1), (0, -1), (-1, 0), (0, 0)],
    [(-1, 0), (0, 0), (0, -1), (1, -1)],
    [(-1, 0), (0, 0), (0, -1), (1, 0)],
    [(0, 1), (0, 0), (0, -1), (0, -2)],
    [(-1, 0), (0, 0), (-1, -1), (-1, -2)],
    [(-1, 0), (0, 0), (0, -1), (0, -2)],
    [(-1, -1), (0, -1), (0, 0), (1, 0)],
]

# 定义各种形状的颜色
SHAPESCOLOR = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC, 
               0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

# 定义一个Board类，操作与之相关的初始化、清空、检查等
class Board():  
    def __init__(self): # 类的初始化函数，自动调用
        self.table = []
        for r in range(Rows): 
            i_row = [NoShape for j in range(Columns)]  
            self.table.append(i_row)

    def check_row_full(self, row): 
        '检查第row行是否满了'
        return (self.table[row].count(NoShape) == 0)
    def getShapeAt(self,cr):
        c,r = cr
        return self.table[r][c]
    def setShapeAt(self,cr, shape):
        c,r = cr
        self.table[r][c] = shape
    
    def check_and_clear(self):
        fulllines = 0
        for ri in range(Rows):
            if self.check_row_full(ri):
                fulllines += 1
                for cur_ri in range(ri, 1, -1):
                    self.table[cur_ri] = self.table[cur_ri-1][:]
                self.table[0] = [NoShape for j in range(Columns)]
        return fulllines    # 返回
        
    def clearboard(self):  # 清空板子
        for r in range(Rows):
            for c in range(Columns):
                self.table[r][c] = NoShape

class TetrixPiece():
    def __init__(self, shape, rotatetimes=0):
        self.shape = shape 
        self.cell_list = SHAPES[self.shape]
        if rotatetimes > 0 :
            for i in range(rotatetimes):
                self.rotate_left()
        
    def rotate_left(self):
        rotate_cell_list = []
        for cell in self.cell_list:
            cc,cr = cell
            rotate_cell_list.append((cr, -cc))
        self.cell_list = rotate_cell_list
    
    def rotate_right(self):
        rotate_cell_list = []
        for cell in self.cell_list:
            cc,cr = cell
            rotate_cell_list.append((-cr, cc))
        self.cell_list = rotate_cell_list
    def getleft(self):
        return min([cr[0] for cr in self.cell_list])
    def getright(self):
        return max([cr[0] for cr in self.cell_list])
    def gettop(self):
        return min([cr[1] for cr in self.cell_list])
    def getbottom(self):
        return max([cr[1] for cr in self.cell_list])
    
class TetrixBoard(QtWidgets.QFrame, Board):
    scoreChanged = QtCore.Signal(int)
    levelChanged = QtCore.Signal(int)
    linesRemovedChanged = QtCore.Signal(int)
    newNextShape = QtCore.Signal(int,int)
        
    def __init__(self, parent=None):
        super(TetrixBoard, self).__init__(parent)
        Board.__init__(self)
        self.curPiece = None
        self.nextPiece = None
        self.curCR = (Columns//2, 0)        
        self.isWaitingNext = True
        self.isPaused = False
        self.timer = QtCore.QBasicTimer()
        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
    def newGame(self):
        self.isWaitingNextPiece = False
        self.numLinesRemoved = 0
        self.score = 0
        self.level = 0
        # self.speed = 500
                
        self.clearboard()

        self.curPiece = TetrixPiece(random.randint(1,7),random.randint(0,3))
        nextshape = random.randint(1,7)
        rotatetimes = random.randint(0,3)
        self.nextPiece = TetrixPiece(nextshape, rotatetimes)
        
        self.newNextShape.emit(nextshape, rotatetimes)
        self.linesRemovedChanged.emit(self.numLinesRemoved)
        self.scoreChanged.emit(self.score)
        self.levelChanged.emit(self.level)
        self.timer.start(self.timeoutTime(), self)
    
    def timeoutTime(self):
        return 1000 / (1 + self.level)    
    
    def pause(self):
        self.isPaused = not self.isPaused
        if self.isPaused:
            self.timer.stop()
        else:
            self.timer.start(self.timeoutTime(), self)
        self.update()
        
    def paintEvent(self, event):
        super(TetrixBoard, self).paintEvent(event)

        painter = QtGui.QPainter(self)
        rect = self.contentsRect()

        if self.isPaused:
            painter.drawText(rect, QtCore.Qt.AlignCenter, "Pause")
            return
        color = QtGui.QColor("gray")
        painter.setPen(color.lighter())
        # for r in range(Rows+1):
        #     painter.drawLine(0,r*cell_size, Columns*cell_size, r*cell_size)
        # for c in range(Columns+1):
        #     painter.drawLine(c*cell_size, 0, c*cell_size, Rows*cell_size)    
        
        for r in range(Rows):
            for c in range(Columns):
                shape = self.getShapeAt((c,r))
                if shape != NoShape:
                    self.drawSquare(painter, (c,r), shape)
                            
        if self.curPiece != None:
            for cell in self.curPiece.cell_list:
                c = self.curCR[0] + cell[0]
                r = self.curCR[1] + cell[1]
                if 0 <= c < Columns and 0 <= r < Rows:
                    self.drawSquare(painter, (c,r), self.curPiece.shape)
            left = self.curPiece.getleft()+self.curCR[0]
            right = self.curPiece.getright()+self.curCR[0]
            color = QtGui.QColor("gray")
            painter.setPen(color.lighter())
            painter.drawLine(left*cell_size,0,left*cell_size,Rows*cell_size)
            painter.drawLine((right+1)*cell_size,0,(right+1)*cell_size,Rows*cell_size)
                
    def drawSquare(self, painter, cr, shape):
        color = QtGui.QColor(SHAPESCOLOR[shape])
        x = cr[0] * cell_size
        y = cr[1] * cell_size
        painter.fillRect(x + 1, y + 1, 
                         cell_size - 2,cell_size - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y+cell_size-1, x, y)
        painter.drawLine(x, y, x+cell_size-1, y)

        painter.setPen(color.darker())
        painter.drawLine(x+1, y+cell_size-1,x+cell_size-1, y+cell_size-1)
        painter.drawLine(x+cell_size-1, y+cell_size-1, x+cell_size-1, y+1)


    def keyPressEvent(self, event):
        if self.isPaused or self.curPiece == None:
            super(TetrixBoard, self).keyPressEvent(event)
            return

        key = event.key()
        if key == QtCore.Qt.Key_Left:
            self.left()
        elif key == QtCore.Qt.Key_Right:
            self.right()
        elif key == QtCore.Qt.Key_Down:
            self.oneLineDown()
        elif key == QtCore.Qt.Key_Up:
            self.rotateLeft()
        elif key == QtCore.Qt.Key_Space:
            self.land()
        #elif key == QtCore.Qt.Key_D:
            #self.oneLineDown()
        else:
            super(TetrixBoard, self).keyPressEvent(event)

    def left(self):
        if self.try_move((-1,0)):   # 如果能够向左移动一格
            self.move((-1,0))       # 就移动一格
    def right(self):
        if self.try_move((1,0)):    # 如果能够向右移动一格
            self.move((1,0))        # 就移动一格
    def rotateLeft(self):
        self.curPiece.rotate_left()     # 向左转动
        if self.try_move([0,0]) is False:  # 如果检查不能转动
            self.curPiece.rotate_right()   # 再转回来
    def rotateRight(self):
        self.curPiece.rotate_right()    # 向右转动
        if self.try_move([0,0]) is False:  # 如果不能转动
            self.curPiece.rotate_left()    # 再转回来            
    def land(self):     # 到底
        max_down = 0    # 最大向下的数量
        for i in range(Rows):
            if self.try_move([0,i]) is True:
                max_down = i
            else:
                break
        self.move([0,max_down])
        self.oneLineDown()
        
    def newPiece(self):
        nextshape = random.randint(1,7)
        rotatetimes = random.randint(0,3)

        self.nextPiece = TetrixPiece(nextshape,rotatetimes)
        self.newNextShape.emit(nextshape,rotatetimes)
        
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.isWaitingNext:  # 如果在等下一个
                self.isWaitingNext = False 
                self.curPiece = self.nextPiece
                self.curCR = [Columns//2,0]
                
                if not self.try_move((0,1)): # 如果不能移动，说明gameover了
                    self.gameover()
                    self.isPaused = True
                    self.timer.stop()
                    return
                self.newPiece()
                self.timer.start(self.timeoutTime(), self)
            else:
                self.oneLineDown()
        else:
            super(TetrixBoard, self).timerEvent(event)
    
    def gameover(self):
        pass
    
    def oneLineDown(self):
        if self.try_move((0,1)):    # 如果能够向下移动一行
            self.move((0,1))        # 向下移动一行
        else:                       # 否则就是到底了
            self.isWaitingNext = True   # 表示开始下一个
            self.save_block_to_table()

            self.curPiece = None
            fulllines = self.check_and_clear()  # 检查表里是否满行了
            if fulllines > 0:
                self.update()
                self.numLinesRemoved += fulllines
                self.score = self.numLinesRemoved * 10
                self.linesRemovedChanged.emit(self.numLinesRemoved)
                self.scoreChanged.emit(self.score)  # 发射消息
                self.level = self.numLinesRemoved // 10
                self.levelChanged.emit(self.level)
                
    # 绘制向指定方向移动后的俄罗斯方块
    def move(self, direction=[0, 0]):
        """
        绘制向指定方向移动后的俄罗斯方块
        :param direction: 俄罗斯方块移动方向
        :return:
        """
        self.curCR[0] += direction[0]
        self.curCR[1] += direction[1]
        self.update()
        
    #判断俄罗斯方块是否可以朝指定方向移动
    def try_move(self, direction=[0, 0]):
        """
            判断俄罗斯方块是否可以朝指定方向移动
            :param direction: 俄罗斯方块移动方向
            :return: boolean 是否可以朝指定方向移动
            """
        c1, r1 = self.curCR
        dc, dr = direction
        
        for cell in self.curPiece.cell_list:
            cell_c, cell_r = cell
            c = cell_c + c1 + dc
            r = cell_r + r1 + dr
            # 判断该位置是否超出左右边界，以及下边界
            # 一般不判断上边界，因为俄罗斯方块生成的时候，可能有一部分在上边界之上还没有出来
            if c < 0 or c >= Columns or r >= Rows:
                return False

            # 必须要判断r不小于0才行，具体原因你可以不加这个判断，试试会出现什么效果
            if r >= 0 and (self.getShapeAt((c,r))!= NoShape):
                return False

        return True
    
    def save_block_to_table(self):
        for cell in self.curPiece.cell_list:
            c0,r0 = cell
            self.setShapeAt((self.curCR[0]+c0,self.curCR[1]+r0), self.curPiece.shape)
    
class NextPieceBuf(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(NextPieceBuf, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.shape = NoShape

    def newNextPiece(self, shape, rt):
        self.shape = shape
        self.piece = TetrixPiece(shape,rt)
        self.dc = self.piece.getright() - self.piece.getleft()
        self.dr = self.piece.getbottom() - self.piece.gettop()
        self.update()        
        
    def paintEvent(self, event):
        super(NextPieceBuf, self).paintEvent(event)
        if self.shape == NoShape:
            return
        painter = QtGui.QPainter(self)
        rect = self.contentsRect()
        color = QtGui.QColor(SHAPESCOLOR[self.shape])
        left = (rect.left()+rect.right()-(self.dc+1)*cell_size)//2 - self.piece.getleft()*cell_size
        top = (rect.top()+rect.bottom()-(self.dr+1)*cell_size)//2 - self.piece.gettop()*cell_size

        for cr in self.piece.cell_list:
            x = cr[0] * cell_size + left
            y = cr[1] * cell_size + top
            painter.fillRect(x + 1, y + 1, 
                            cell_size - 2,cell_size - 2, color)

            painter.setPen(color.lighter())
            painter.drawLine(x, y + cell_size - 1, x, y)
            painter.drawLine(x, y, x + cell_size - 1, y)

            painter.setPen(color.darker())
            painter.drawLine(x + 1, y + cell_size - 1,
                            x + cell_size - 1, y + cell_size - 1)
            painter.drawLine(x + cell_size - 1, y + cell_size - 1, 
                            x + cell_size - 1, y + 1)

class TetrixWindow(QtWidgets.QWidget):
    def __init__(self):
        super(TetrixWindow, self).__init__()

        self.board = TetrixBoard()

        nextPieceBuf = NextPieceBuf()
        
        scoreLcd = QtWidgets.QLCDNumber(5)
        scoreLcd.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        levelLcd = QtWidgets.QLCDNumber(2)
        levelLcd.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        linesLcd = QtWidgets.QLCDNumber(5)
        linesLcd.setSegmentStyle(QtWidgets.QLCDNumber.Filled)

        startButton = QtWidgets.QPushButton("&Start")
        startButton.setFocusPolicy(QtCore.Qt.NoFocus)
        quitButton = QtWidgets.QPushButton("&Quit")
        quitButton.setFocusPolicy(QtCore.Qt.NoFocus)
        pauseButton = QtWidgets.QPushButton("&Pause")
        pauseButton.setFocusPolicy(QtCore.Qt.NoFocus)
        
        startButton.clicked.connect(self.board.newGame)
        pauseButton.clicked.connect(self.board.pause)
        quitButton.clicked.connect(qApp.quit)
        self.board.scoreChanged.connect(scoreLcd.display)
        self.board.levelChanged.connect(levelLcd.display)
        self.board.linesRemovedChanged.connect(linesLcd.display)
        self.board.newNextShape.connect(nextPieceBuf.newNextPiece)
        
        nextlabel = QtWidgets.QLabel("NEXT")
        levellabel = QtWidgets.QLabel("LEVEL")
        scorelabel = QtWidgets.QLabel("SCORE")
        lineremovedlabel = QtWidgets.QLabel("LINES REMOVED")
        
        layout = QtWidgets.QGridLayout()
        layout.addWidget(nextlabel, 0, 0)
        layout.addWidget(nextPieceBuf, 1, 0)
        layout.addWidget(levellabel, 2, 0)
        layout.addWidget(levelLcd, 3, 0)
        layout.addWidget(startButton, 4, 0)
        layout.addWidget(self.board, 0, 1, 6, 1)
        layout.addWidget(scorelabel, 0, 2)
        layout.addWidget(scoreLcd, 1, 2)
        layout.addWidget(lineremovedlabel, 2, 2)
        layout.addWidget(linesLcd, 3, 2)
        layout.addWidget(quitButton, 4, 2)
        layout.addWidget(pauseButton, 5, 2)
        self.setLayout(layout)

        self.setWindowTitle("Tetrix")
        self.resize(550, 370)

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = TetrixWindow()
    window.show()
    random.seed(None)
    sys.exit(app.exec_())