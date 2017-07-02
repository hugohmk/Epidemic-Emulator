from subprocess import call
import platform
import argparse
import os


if __name__=="__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path_unix = dir_path.replace("\\","/")
    windows_plat = True
    if (platform.system()!="Windows"):
        windows_plat = False
        dir_path = dir_path_unix
    cmd=""

    parser = argparse.ArgumentParser()
    parser.add_argument("-py","--python",default="python",
                        help="Pyhton location (use this if python can not be located in PATH)")
    parser.add_argument("-t","--topology",choices=["clique","cicle","star"],default="clique",
                        help="Network topology: clique, cicle or star")
    
    args = parser.parse_args()
    with open(dir_path_unix+"/network.txt","r") as f:
        b = ""
        inter = "-i 1"
        for i in f:
            i = i.rstrip("\n").split("|")
            if len(i)<4:
                break
            if windows_plat:
                cmd = cmd + "start {0}{1} {2} -id {3} {4}\n".format(b, args.python, dir_path+"\\main.py -t "+args.topology, i[0], inter)
                b = "/B "
                inter = ""
            else:
                cmd = cmd + "{1} {2} -id {3} {4} {0}\n".format(b, args.python, dir_path+"/main.py -t "+args.topology, i[0], inter)
                b = "&"
                inter = ""
                
    extension = ".bat"
    if not windows_plat: extension = ".sh"
    
    with open(dir_path_unix+"/emulation"+extension,"w") as f:
        f.write(cmd)
