from subprocess import call
import os

if __name__=="__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path_unix = dir_path.replace("\\","/")
    cmd=""
    
    with open(dir_path_unix+"/network.txt","r") as f:
        b = ""
        inter = "-i 1"
        for i in f:
            i = i.rstrip("\n").split("|")
            if len(i)<4:
                break
            cmd=cmd+"start {0}D:\Python27\python.exe {1} -id {2} {3}\n".format(b, dir_path+"\\main.py", i[0], inter)
            b = "/B "
            inter = ""

    with open(dir_path_unix+"/emulation.bat","w") as f:
        f.write(cmd)

    call(dir_path_unix+"/emulation.bat")
