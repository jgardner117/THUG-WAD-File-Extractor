import csv
import os.path
import argparse


def classtocsv(file):
    # A simple class that dumps each AssetFile object to a row in a CSV. Creates a CSV called Extracted Files if one is
    # not found.
    fname = "Extracted Files.csv"
    if os.path.isfile(fname):
        with open(fname, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([file.name, file.size, file.eof])
        print("Successfully appended row to csv")
    else:
        with open(fname, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["File Name", "File Size", "Start of Next File"])
            writer.writerow([file.name, file.size, file.eof])
        print("Successfully created csv and appended row")


def extractfile(endfile,wadfile):
    # This function takes an instance of the AssetFile class, and uses the information provided to extract the file
    # from the .WAD file
    f = open(wadfile, "rb")
    newfilepath = os.path.dirname(os.path.abspath(__file__)) + "/Extracted" + endfile.name.replace('\\', '/')
    if os.path.dirname(newfilepath) != "":
        os.makedirs(os.path.dirname(newfilepath), exist_ok=True)
    outfile = open(newfilepath, "wb", )
    f.seek(endfile.lasteof, 0)
    data = f.read(endfile.size)
    outfile.write(data)
    outfile.close()
    print("Sucessfully extracted " + newfilepath)


class AssetFile:
    # A class that models the asset file objects found in the .HED file
    def __init__(self):
        self.name = ""
        self.size = 0
        self.eof = ""
        self.lasteof = 0


def getfilesize(byte):
    # Calculates and returns filesize
    return int.from_bytes(byte, byteorder='little', signed=False)


def getfilename(hedfile):
    # Builds and returns the file name
    namecount = 0
    namedone = False
    filename = ""
    while not namedone:
        namecount += 1
        byte = hedfile.read(2).hex()
        if byte[2:] == "00" and byte[0:2] != "00":
            filename += bytes.fromhex(byte).decode("ASCII").replace('\x00', '')
            if namecount % 2 != 0:
                hedfile.read(2).hex()
                namedone = True
            else:
                namedone = True
        elif byte == "0000":
            if namecount % 2 != 0:
                hedfile.read(2).hex()
                namedone = True
            else:
                namedone = True
        else:
            filename += bytes.fromhex(byte).decode("ASCII")
    return filename


def geteof(hedfile):
    # Calculates & returns the start of the next file
    fileend = hedfile.read(4)
    eof = ""
    if fileend.hex() != "ffffffff":
        # This if skips the eof assignment for the final file, as it doesn't have one
        eof = int.from_bytes(fileend, byteorder='little', signed=False)
    return eof


def main():
    parser = argparse.ArgumentParser(description='Extract asseets from Tony Hawks Underground .WAD files')
    parser.add_argument('hed', type=str, help='.HED file location')
    parser.add_argument('wad', type=str, help='.WAD file location')
    args = parser.parse_args()
    with open(args.hed, "rb") as hedfile:
    #with open("C:\\Users\\CFHHATEPH34R\\Downloads\\thug\SKATE5.HED", "rb") as hedfile:
        # Skip past the initial padding and first file
        hedfile.read(4)
        newfile = AssetFile()
        lasteof = 0
        while True:
            # Read the next byte
            byte = hedfile.read(4)

            # If no bytes are returned, end of HED file has been reached
            if not byte:
                break

            # Build & assign lasteof
            newfile.lasteof = lasteof
            print("LastEOF: " + str(newfile.lasteof))

            # Build & assign filesize
            newfile.size = getfilesize(byte)
            print("Filesize: " + str(newfile.size))

            # Build & assign file name
            newfile.name = getfilename(hedfile)
            print("File name: " + newfile.name)

            # Build & assign the end of file
            newfile.eof = geteof(hedfile)
            print("EOF: " + str(newfile.eof))

            # Add object as a new row to the Extracted Files.csv
            classtocsv(newfile)

            # Extract the file from the .WAD file
            extractfile(newfile,args.wad)

            # Save the eof to the lasteof and reset the class for the next iteration
            lasteof = newfile.eof
            newfile = AssetFile()

    hedfile.close()


main()
