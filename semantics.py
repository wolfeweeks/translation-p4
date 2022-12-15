import sys

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, string):
        self.stack.append(string)

    def pop(self):
        self.stack.pop()

    def find(self, string):
        for i in range(len(self.stack)):
            if self.stack[-(i + 1)] == string:
                return i
        return -1


stack = Stack()
varCounts = {}
totalVars = 0
totalLabels = 0
userVars = []

# target = open('a.asm', 'w')

def newName(nameType):
    global totalVars
    global totalLabels
    if nameType == 'var':
        totalVars += 1
        return 'T' + str(totalVars)
    elif nameType == 'label':
        totalLabels += 1
        return 'L' + str(totalLabels)


def writeBranch(op, tempLabel):
    global target
    if op == '<=':
        target.write('BRPOS ' + tempLabel + '\n')
    elif op == '%':
        target.write('BRZERO ' + tempLabel + '\n')
    elif op == '>=':
        target.write('BRNEG ' + tempLabel + '\n')
    else:
        target.write('BRPOS ' + tempLabel + '\n')
        target.write('BRNEG ' + tempLabel + '\n')


def staticSemantics(target, root, blockNo):
    global stack
    global varCounts
    global userVars

    # root.write(depth)

    def isId(token):
        if token[0] in 'abcdefghijklmnopqrstuvwxyz': return True
        return False

    if blockNo not in varCounts.keys():
        varCounts[blockNo] = 0
    
    if root:
        if root.nonterminal == 'in':
            target.write('READ ' + root.tokens[0] + '\n')
            if isId(root.tokens[0]):
                    find = stack.find(root.tokens[0])
                    if find == -1:
                        print('SEMANTICS ERROR: On line ' + str(root.tokenLines[0]) + ': identifier \'' + root.tokens[0] + '\' was not instantiated')
                        sys.exit()
                    else:
                        target.write('LOAD ' + root.tokens[0] + '\n')
                        target.write('STACKW ' + str(find) + '\n')
            return

        if root.nonterminal == 'out':
            staticSemantics(target, root.children[0], blockNo)
            temp = newName('var')
            target.write('STORE ' + temp + '\n')
            target.write('WRITE ' + temp + '\n')
            return

        if root.nonterminal == 'expr':
            if len(root.children) == 2 and root.tokens[0] == '++':
                staticSemantics(target, root.children[1], blockNo)
                temp = newName('var')
                target.write('STORE ' + temp + '\n')
                staticSemantics(target, root.children[0], blockNo)
                target.write('ADD ' + temp + '\n')
                return
            elif len(root.children) == 1:
                staticSemantics(target, root.children[0], blockNo)
                return

        if root.nonterminal == 'A':
            if len(root.children) == 2 and root.tokens[0] == '--':
                staticSemantics(target, root.children[1], blockNo)
                temp = newName('var')
                target.write('STORE ' + temp + '\n')
                staticSemantics(target, root.children[0], blockNo)
                target.write('SUB ' + temp + '\n')
                return
            elif len(root.children) == 1:
                staticSemantics(target, root.children[0], blockNo)
                return

        if root.nonterminal == 'N':
            if len(root.children) == 2:
                staticSemantics(target, root.children[1], blockNo)
                temp = newName('var')
                target.write('STORE ' + temp + '\n')
                staticSemantics(target, root.children[0], blockNo)
                if root.tokens[0] == '/':
                    target.write('DIV ' + temp + '\n')
                elif root.tokens[0] == '*':
                    target.write('MULT ' + temp + '\n')
                return
            elif len(root.children) == 1:
                staticSemantics(target, root.children[0], blockNo)
                return

        if root.nonterminal == 'R':
            if len(root.tokens) == 1:
                if isId(root.tokens[0]):
                    find = stack.find(root.tokens[0])
                    if find == -1:
                        print('SEMANTICS ERROR: On line ' + str(root.tokenLines[0]) + ': identifier \'' + root.tokens[0] + '\' was not instantiated')
                        sys.exit()
                    else:
                        target.write('STACKR ' + str(find) + '\n')
                        return
                else:
                    target.write('LOAD ' + str(root.tokens[0]) + '\n')
                    return
            else:
                staticSemantics(target, root.children[0], blockNo)
                return

        if root.nonterminal == 'mStat':
            if len(root.children) == 0:
                return
            elif len(root.children) == 2:
                staticSemantics(target, root.children[0], blockNo)
                staticSemantics(target, root.children[1], blockNo)
                return

        if root.nonterminal == 'if':
            staticSemantics(target, root.children[2], blockNo)
            tempVar = newName('var')
            target.write('STORE ' + tempVar + '\n')
            staticSemantics(target, root.children[0], blockNo)
            target.write('SUB ' + tempVar + '\n')
            tempLabel = newName('label')
            writeBranch(root.children[1].tokens[0], tempLabel)
            staticSemantics(target, root.children[3], blockNo)
            target.write(tempLabel + ': NOOP\n')
            return

        if root.nonterminal == 'M':
            if root.children[0].nonterminal == 'R':
                staticSemantics(target, root.children[0], blockNo)
                return
            else:
                staticSemantics(target, root.children[0], blockNo)
                target.write('MULT -1\n')
                return

        if root.nonterminal == 'program':
            for child in root.children:
                if child and child.nonterminal == 'block':
                    staticSemantics(target, child, blockNo + 1)
                else:
                    staticSemantics(target, child, blockNo)
            for i in range(varCounts[blockNo]):
                stack.pop()
                target.write('POP\n')
            target.write('STOP\n')
            for i in range(totalVars):
                target.write('T' + str(i + 1) + ' 0\n')
            for var in userVars:
                target.write(var + ' 0\n')
            return

        if root.nonterminal == 'vars':
            if varCounts[blockNo] > 0:
                find = stack.find(root.tokens[0])
                if find >= 0 and find < varCounts[blockNo]:
                    print('SEMANTICS ERROR: On line ' + str(root.tokenLines[0]) + ': multiple definitiions of \'' + root.tokens[0] + '\'')
                    sys.exit()
            
            stack.push(root.tokens[0])
            varCounts[blockNo] += 1
            target.write('LOAD ' + root.tokens[1] + '\n')
            target.write('PUSH\n')
            target.write('STACKW 0\n')
            if root.tokens[0] not in userVars:
                userVars.append(root.tokens[0])
            if root.children and len(root.children) != 0:
                staticSemantics(target, root.children[0], blockNo)
            return

        if root.nonterminal == 'assign':
            staticSemantics(target, root.children[0], blockNo)
            find = stack.find(root.tokens[0])
            if find == -1:
                print('SEMANTICS ERROR: On line ' + str(root.tokenLines[0]) + ': identifier \'' + root.tokens[0] + '\' was not instantiated')
                sys.exit()
            else:
                target.write('STACKW ' + str(find) + '\n')
                return

        if root.nonterminal == 'loop':
            loopLabel = newName('label')
            target.write(loopLabel + ': NOOP\n')
            staticSemantics(target, root.children[2], blockNo)
            tempVar = newName('var')
            target.write('STORE ' + tempVar + '\n')
            staticSemantics(target, root.children[0], blockNo)
            target.write('SUB ' + tempVar + '\n')
            breakLabel = newName('label')
            writeBranch(root.children[1].tokens[0], breakLabel)
            staticSemantics(target, root.children[3], blockNo)
            target.write('BR ' + loopLabel + '\n')
            target.write(breakLabel + ': NOOP\n')
            return

        if root.nonterminal == 'block':
            for child in root.children:
                staticSemantics(target, child, blockNo)
            for i in range(varCounts[blockNo]):
                stack.pop()
                target.write('POP\n')
            return
        
        if root.children is not None:
            for child in root.children:
                if child and child.nonterminal == 'block':
                    staticSemantics(target, child, blockNo + 1)
                else:
                    staticSemantics(target, child, blockNo)