import sys
import time

def custom_error(message, passive=False):
    print(message)
    if not passive:
        sys.exit()        

class Object:
    def __init__(self, v, n):
        self.value = v
        self.name = n
        self.references = 0

class Instruction:
    def __init__(self, operation, parameters=None):
        self.operation = operation
        self.parameters = parameters

# reads files and returns split lines 
def read_file(file_name):
    f = open(file_name)
    text = f.read()
    f.close()
    return text.splitlines()    

class VM:
    def __init__(self):
        # stack memory, stacker is a single stack vm
        self.inner_stack = []
        # tos is the top of the stack
        self.tos = None
        # memory structure for objects
        self.heap = []
        # the instruction stack
        self.instruction_stack = []
        # points the current instruction
        self.program_counter = -1

    # pops the top of the stack 
    def pop(self):
        rval = self.tos
        if len(self.inner_stack) > 0:
            self.tos = self.inner_stack.pop(0)
        return rval
    
    # pushes a value to the top of the stack
    def push(self, value):
        if self.tos != None:
            self.inner_stack.insert(0, self.tos)
        self.tos = value
    
    # removes n1 the tos and brings n2 as the new tos
    def drop(self):
        self.tos = self.inner_stack.pop(0)

    # duplicates n1 and pushes it to the stack
    def dup(self):
        self.inner_stack(self.tos, 0)

    # pushes a copy of n2 onto the top of the stack
    def over(self):
        self.push(self.inner_stack[0])

    # swaps n1 and n2
    def swap(self):
        n1 = self.inner_stack[0]
        n2 = self.tos
        self.tos = n1
        self.inner_stack[0] = n2

    # pops tos and stores it on the heap with its assigned variable name
    def store(self, name):
        self.heap.append(Object(name, self.pop()))

    # pushes the object off the heap to tos
    def fetch(self, name):
        for obj in self.heap:
            if obj.name == name:
                self.push(obj.value)
                return None
        sys.exit()
        
    # add n1 and n2
    def add(self):
        n2 = self.inner_stack.pop(0)
        self.tos += n2
    
    # subtracts n2 from n1
    def sub(self):
        n2 = self.inner_stack.pop(0)
        self.tos -= n2

    # multiples n1 and n2
    def mult(self):
        n2 = self.inner_stack.pop(0)
        self.tos *= n2
    
    # divides n1 by n2
    def div(self):
        n2 = self.inner_stack.pop(0)
        self.tos /= n2

    # pushes 1 to the stack if n1 is gthan n2
    def gthan(self):
        n2 = self.inner_stack.pop(0)
        if self.tos > n2:
            self.tos = 1
        else:
            self.tos = 0
    
    # pushes 1 to the stack if n1 is lthan n2
    def lthan(self):
        n2 = self.inner_stack.pop(0)
        if self.tos < n2:
            self.tos = 1
        else:
            self.tos = 0
    
    # pushes 1 to the stack if n1 is gthanoeq to n2
    def gthanoeq(self):
        n2 = self.inner_stack.pop(0)
        if self.tos >= n2:
            self.tos = 1
        else:
            self.tos = 0

    # pushes 1 to the stack if n1 is lthanoeq to n2
    def lthanoeq(self):
        n2 = self.inner_stack.pop(0)
        if self.tos <= n2:
            self.tos = 1
        else:
            self.tos = 0
    
    # pushes 1 to the stack if n1 is equal to n2
    def eq(self):
        n2 = self.inner_stack.pop(0)
        if self.tos == n2:
            self.tos = 1
        else:
            self.tos = 0
    
    # jumps to set address on the instruction stack and proceeds from there
    def jump(self, address):
        self.program_counter = address
    
    # moves program counter up one to skip the next instruction explicitly
    def skip(self):
        self.program_counter += 1
    
    # pops and prints tos
    def stack_print(self):
        print(self.pop())

    # executes the next instruction
    def execute(self):
        self.program_counter += 1
        instr: Instruction = self.instruction_stack[self.program_counter]
        op = instr.operation
        if op == "add":
            self.add()
        elif instr.operation == "sub":
            self.sub()
        elif op == "mult":
            self.mult()
        elif op == "div":
            self.div()
        elif op == "gthan":
            self.gthan()
        elif op == "lthan":
            self.lthan()
        elif op == "gthanoeq":
            self.gthanoeq()
        elif op == "lthanoeq":
            self.lthanoeq()
        elif op == "push":
            self.push(instr.parameters[0])
        elif op == "drop":
            self.drop()
        elif op == "swap":
            self.swap()
        elif op == "over":
            self.over()
        elif op == "eq":
            self.eq()
        elif op == "pop":
            self.pop()
        elif op == "if":
            self.stack_if()
        elif op == "end":
            sys.exit()
        elif op == "print":
            self.stack_print()
        elif op == "store":
            self.store(instr.parameters[0])
        elif op == "fetch":
            self.store(instr.parameters[0])
        else:
            custom_error("Unknown operation " + op)
        return self.execute()
        
    # if tos >= 1 execute the next instruction otherwise skip it
    def stack_if(self):
        if self.pop() < 1:
            self.skip()

    # parses file into the instruction set
    def parse_file(self, file_name):
        lines = read_file(file_name)
        instructions = []
        for line in lines:
            tokens = line.split(" ")
            instruction = None
            if len(tokens) > 1:
                instruction = Instruction(tokens.pop(0), [])
                for token in tokens:
                    if instruction.operation == "load" or instruction.operation == "store":
                        instruction.parameters.append(token)
                    elif token[0] in ["'", '"'] and token[-1] in ["'", '"']:
                        token = token.replace('"', "")
                        token = token.replace("'", "")
                        instruction.parameters.append(token)
                    elif token[0].isdigit():
                        is_float = False
                        for char in token:
                            if not char.isdigit():
                                if char == ".":
                                    is_float = True
                                else:
                                    custom_error("Token of unkown type " + token)
                        r_token = None
                        if is_float:
                            r_token = float(token)
                        else:
                            r_token = int(token)
                        instruction.parameters.append(r_token)
                    else:
                        custom_error("Token of unkown type " + token)
            else:
                instruction = Instruction(tokens[0])
            instructions.append(instruction)
        self.instruction_stack = instructions

    def execute_debug(self):
        print("STACK")
        print(self.inner_stack)
        print("TOS")
        print(self.tos)
        print("HEAP")
        print(self.heap)
        self.program_counter += 1
        print("Current instruction")
        print(self.instruction_stack[self.program_counter].operation)
        instr: Instruction = self.instruction_stack[self.program_counter]
        op = instr.operation
        if op == "add":
            self.add()
        elif instr.operation == "sub":
            self.sub()
        elif op == "mult":
            self.mult()
        elif op == "div":
            self.div()
        elif op == "gthan":
            self.gthan()
        elif op == "lthan":
            self.lthan()
        elif op == "gthanoeq":
            self.gthanoeq()
        elif op == "lthanoeq":
            self.lthanoeq()
        elif op == "push":
            self.push(instr.parameters[0])
        elif op == "drop":
            self.drop()
        elif op == "swap":
            self.swap()
        elif op == "over":
            self.over()
        elif op == "eq":
            self.eq()
        elif op == "pop":
            self.pop()
        elif op == "if":
            self.stack_if()
        elif op == "end":
            sys.exit()
        elif op == "print":
            self.stack_print()
        elif op == "store":
            self.store(instr.parameters[0])
        elif op == "fetch":
            self.store(instr.parameters[0])
        else:
            custom_error("Unknown operation " + op)
        return self.execute_debug()

start = time.time()
vm = VM()
vm.parse_file("./test.bc")
vm.execute()
end = time.time()
print(end - start)