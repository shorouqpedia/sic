def nBytes (mnemonic , operand):
    f=0 #flag found or not
    bytes=-1
    if(mnemonic=="RESW" or mnemonic=="RESB" or mnemonic=="WORD" or mnemonic=="BYTE"):
        f=1
        if(mnemonic=="RESW"):
            bytes= int(operand)*3
        elif(mnemonic=="RESB"):
            bytes=int(operand)
        elif(mnemonic=="WORD"):
            bytes=3
        elif(mnemonic=="BYTE"):
            if(operand[0]=='X'):
                if((len(operand)-3)%2==0):
                    bytes=(len(operand)-3)/2
                else:
                    bytes=((len(operand)-3)/2)+1
            elif(operand[0]=='C'):
                bytes=len(operand)-3

    if(f==0): #not found
        opcode = open("OPCODE.txt","r")
        for opLine in opcode:
            OL=opLine.split("\t")
            if(mnemonic==OL[0]):
                f=1
                bytes=OL[1]
                break
        opcode.close()
    if(f==0):
        bytes=-1

    return int(bytes)

def notFound(sym):
    symbolF=open("SYMTAB.txt","r")
    f=0
    for symLine in symbolF:
        symLine=symLine[:-1]  #remove \n
        nline=symLine.split("\t")

        if(nline[0]==sym):
            f=1
            break
    symbolF.close()
    if (f==1):
        return 0
    else:
        return 1

def return_opcode (mnemonic):
    opfile = open("OPCODE.txt","r")
    f=0
    for opline in opfile:
        opline=opline[:-1]
        op=opline.split('\t')

        if(mnemonic==op[0]):
            f=1
            opcode=op[2]
            break
    opfile.close()
    if(f==1):
        return opcode
    else:
        return -1

#return address
def return_add(label):
    symf=open("SYMTAB.txt","r")
    f=0
    for line in symf:
        line=line[:-1]
        slines=line.split("\t")
        if(slines[0]==label):
            f=1
            TA=slines[1]
            break
    symf.close()

    if (f==1):
        return TA
    else:
        return -1

def return_asci(char):
    ascii = open("ASCII.txt", "r")
    found = 0

    for aline in ascii:
        line = aline
        line = line[:-1]
        lineSp = line.split('\t')

        if (lineSp[1] == str(char)):
            found = 1
            asciiCode = lineSp[0]
            break

    ascii.close()

    if (found == 1):
        return asciiCode
    else:
        return -1


fileName=input("please enter the name of the file ^_^ :")
file_asm=open(fileName,"r")
symtabFile= open("SYMTAB.txt","w")
locatedCode=open("locatedCode.txt","w")

read=file_asm.readline();
while (read[0]=="."):
    read=file_asm.readline()    #skip comments

read= read[:-1]

firstLine=read.split('\t')

HexaAdd=firstLine[2]
DecimalAdd=int(firstLine[2],16)

#print(DecimalAdd)

for line in file_asm:
    line=line[:-1]
    dline=line.split('\t')

    if (line[0]!='.'):
        if (dline[1]=="END"):
            break

        bytesN=0

        if(len(dline)==3):
            bytesN=nBytes(dline[1],dline[2])

        else:
            bytesN=nBytes(dline[1],0)
        if(bytesN==-1):
            print("Invalid mnemonic "+dline[1])
            input()
            exit(0)

        #in SYMTAB
        if(dline[0]!=''):   #labels isn't empty
            if (notFound(dline[0])):   #label isn't exist into symbol table
                symbol = dline[0]+'\t'+ HexaAdd
                symtabFile.write(symbol)
                symtabFile.write('\n')
                symtabFile.flush()
            else:
                print(dline[0]+" is declared twice .")
                input()
                exit(0)

        locatedCode.write(HexaAdd+'\t'+line)
        locatedCode.write('\n')
        locatedCode.flush()

        DecimalAdd=DecimalAdd+bytesN
        HexaAdd=str(format(DecimalAdd,'04x'))

symtabFile.close()
file_asm.close()
locatedCode.close()

Code=open("locatedCode.txt","r")
withObjCodes=open("objCode.txt","w")
objCode=open("obj.txt","w")

Code.seek(0)    #start from begining
for line in Code:
    line=line[:-1]
    rline=line.split('\t')

    addr=rline[0]
    labl=rline[1]
    mnem=rline[2]
    if (len(rline)==4):
        oprnd=rline[3]
    if (mnem!="RESW" and mnem!="RESB"):
        if (mnem=="BYTE"):
            arr_oprnd=oprnd.split('\'')
            if (arr_oprnd[0]=="X"):
                Objl=arr_oprnd[1]

            elif(arr_oprnd[0]=="C"):
                chars=list(arr_oprnd[1])
                Objl=""
                print(chars)
                for c in chars:
                    asc=return_asci(c)
                    if (asc==-1):
                        print("invalid char")
                        input()
                        exit(0)

                    Objl=Objl+asc
        elif (mnem=="WORD"):
            Objl=str(format(int(oprnd),'06x'))

        elif (mnem=="RSUB"):
            ocode=return_opcode(mnem)
            if (ocode==-1):
                print(mnem+" coudln't be found")
                input()
                exit(0)
            Objl=ocode+"0000"

        else:
            ocode=return_opcode(mnem)
            if (ocode==-1):
                print(mnem+" coudln't be found")
                input()
                exit(0)
            dOprnd=oprnd.split(',')
            trgt=return_add(dOprnd[0])
            if (trgt==-1):
                print(dOprnd[0]+" : Target Address couldn't be found")
                input()
                exit(0)
            if(len(dOprnd)==2 and dOprnd[1]=="X"):
                part1=trgt[:1]
                part2=trgt[1:]

                part1=(int(part1)+8)
                part1=str(format(part1,'01x'))

                trgt=part1+part2
            Objl=ocode+trgt

        if(mnem=="RSUB"):
            writeline=line+"\t\t"+Objl
        else:
            writeline=line+"\t"+Objl

        withObjCodes.write(writeline)
        withObjCodes.write('\n')
        objCode.write(rline[0]+"\t"+Objl)
        objCode.write('\n')

    else:
        withObjCodes.write(line+'\n')
Code.close()
withObjCodes.close()
objCode.close()


#Final Object Code
final= open("ojcFinal.txt","w")





final.close()