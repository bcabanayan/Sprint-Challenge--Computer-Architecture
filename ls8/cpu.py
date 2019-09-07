"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
JMP = 0b01010100
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.registers = [0] * 8
        self.pc = 0
        self.running = True
        self.ops = {
            HLT: self.op_hlt,
            LDI: self.op_ldi,
            PRN: self.op_prn,
            MUL: self.op_mul,
            PUSH: self.op_push,
            POP: self.op_pop,
            CALL: self.op_call,
            ADD: self.op_add,
            RET: self.op_ret,
            JMP: self.op_jmp,
            CMP: self.op_cmp,
            JEQ: self.op_jeq,
            JNE: self.op_jne
        }
        # stack pointer set to starting point in ram
        self.registers[7] = 0xF3
        self.sp = self.registers[7]
        # equal, less than, greater than flags
        self.E = 0
        self.L = 0
        self.G = 0

    def op_hlt(self, OP_A, OP_B):
        self.running = False
    
    def op_ldi(self, OP_A, OP_B):
        MAR = OP_A
        MDR = OP_B
        self.registers[MAR] = MDR

    def op_prn(self, OP_A, OP_B):
        print(self.registers[OP_A])

    def op_mul(self, OP_A, OP_B):
        self.alu('MUL', OP_A, OP_B)
    
    def op_add(self, OP_A, OP_B):
        self.alu('ADD', OP_A, OP_B)

    def op_push(self, OP_A, OP_B):
        self.registers[7] = (self.sp - 1) % 255
        self.sp = self.registers[7]

        value_to_push = self.registers[OP_A]

        self.ram_write(self.sp, value_to_push)

    def op_pop(self, OP_A, OP_B):
        value_to_pop = self.ram_read(self.sp)

        self.registers[OP_A] = value_to_pop

        self.registers[7] = (self.sp + 1) % 255
        self.sp = self.registers[7]

    def op_call(self, OP_A, OP_B):
        address_to_jump_to = self.registers[OP_A]
        # store address of the next instruction
        next_instruction_address = self.pc + 2
        self.registers[7] = (self.registers[7] - 1) % 255
        self.ram_write(self.sp, next_instruction_address)
        # set pc to address to jump to
        self.pc = address_to_jump_to

    def op_ret(self, OP_A, OP_B):
        address_to_return_to = self.ram_read(self.sp)

        self.registers[7] = (self.registers[7] + 1) % 255

        self.pc = address_to_return_to

    def op_jmp(self, OP_A, OP_B):
        address_to_jump_to = self.registers[OP_A]
        self.pc = address_to_jump_to

    def op_cmp(self, OP_A, OP_B):
        self.alu('CMP', OP_A, OP_B)            

    def op_jeq(self, OP_A, OP_B):
        if self.E == 1:
            address_to_jump_to = self.registers[OP_A]
            self.pc = address_to_jump_to
        else:
            self.pc += 2

    def op_jne(self, OP_A, OP_B):
        if self.E == 0:
            address_to_jump_to = self.registers[OP_A]
            self.pc = address_to_jump_to
        else:
            self.pc += 2

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR  

    def load(self, filename):
        """Load a program into memory."""
        
        address = 0

        # try:
        with open(filename) as file:
            for line in file:
                comment_split = line.split('#')
                instruction = comment_split[0]
                if instruction == '':
                    continue
                first_bit = instruction[0]
                if first_bit == '1' or first_bit == '0':
                    self.ram[address] = int(instruction[:8], 2)
                    address += 1

        # except IOError: #File Not Found Error
        #     print('I cannot find that file, check the name')
        #     sys.exit(2)

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
        elif op == "CMP":
            if self.registers[reg_a] == self.registers[reg_b]:
                self.E = 1
                self.L = 0
                self.G = 0
            elif self.registers[reg_a] < self.registers[reg_b]:
                self.E = 0
                self.L = 1
                self.G = 0
            elif self.registers[reg_a] > self.registers[reg_b]:
                self.E = 0
                self.L = 0
                self.G = 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while self.running:
            IR = self.ram_read(self.pc)

            OP_A = self.ram_read(self.pc + 1)
            OP_B = self.ram_read(self.pc + 2)

            OP_SIZE = IR >> 6

            INS_SET = ((IR >> 4) & 0b1) == 1

            if IR in self.ops:
                self.ops[IR](OP_A, OP_B)

            if not INS_SET:
                self.pc += OP_SIZE + 1