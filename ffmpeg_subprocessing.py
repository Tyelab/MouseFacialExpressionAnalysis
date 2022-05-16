# find .avi videos, re-encode them using python subprocessing for specialk

from pathlib import Path
import subprocess
import lxml.etree
import sys

def xml_parser(xml_path: Path) -> lxml.etree._ElementTree:
    """
    Parse Prairie View's xml with lxml.
    Prairie View's xml that's contained in the .xml and .env files is
    inconsistent with versioning. Using lxml allows for use of a parser
    that can escape errors when it finds badly formed xml.
    Args:
        xml_path:
            Absolute path to the file needing to be parsed.
    
    Returns:
        Root of xml tree.
    """

    # Define lxml parser that's used for reading the tree with
    # recover=True so it can pass badly formed XML lines
    parser = lxml.etree.XMLParser(recover=True)

    # Get the "root" of the tree for parsing specific elements
    root = lxml.etree.parse(str(xml_path), parser).getroot()
    
    return root


def get_framerate(raw_dir: Path):

    # Generate list of environment files inside the raw directory

    # Get the root of xml tree
    root = xml_parser(raw_dir)

    xpath = ".//PVStateValue[@key='framerate']"

    element = root.find(xpath)

    framerate = round(float(element.attrib["value"]), 2)

    return framerate


base_dir = Path("/nadata/snlkt/specialk_cs/2p/raw")

dir_list = [path for path in base_dir.glob("*/*/*.avi")]

count = 0

for dir in dir_list:

    count += 1

    xml_path = [xml for xml in dir.parent.glob("*/*.env")]


    if len(xml_path) != 1:
        print("ERROR")
        print(dir)
    else:
        pass

    try:
        x = get_framerate(xml_path[0])

    except IndexError:

        print(dir, "MISSING XML?")

        pass

    output_name = dir.parent / str(dir.stem + ".mp4")

    cmd = [f"ffmpeg -r '{x}' -i {str(dir)} -c:v h264 -preset superfast -pix_fmt yuv420p -crf 15 -threads 2 {str(output_name)}"]

    print(cmd)

    process = subprocess.Popen(cmd, shell=True)



# ffmpeg -i "20211216_CSE014_plane1_-333.325.avi" -c:v h264 -r 29.42 "20211216_CSE014_plane1_-333.325.mp4"

# ffmpeg -i "20211216_CSE014_plane1_-333.325.avi" -c:v h264 -preset superfast -pix_fmt yuv420p -crf 23 "new.mp4"
