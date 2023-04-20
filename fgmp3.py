import sys
from mutagen.id3 import ID3, APIC, USLT, TPE1, TIT2, TALB
import os

def parse_arg():
    argv = sys.argv
    argc = len(argv)
    
    assert argc >= 2
    mp3_path = argv[1]
    
    if argc >= 3 and (argv[2] == "--list" or argv[2] == "--show"):
        option_dict = {"show": True}
        return mp3_path, option_dict
    
    if argc >= 3 and (argv[2] == "--clear"):
        option_dict = {"clear": True}
        return mp3_path, option_dict
    
    legal_options = ["--caption", "--singer", "--image", "--lyrics", "--album", "--artist", "--title", "--cover", "--comment", "--comments"]
    # def augment_options(options):
    #     minus_options = ["-" + option[0] for option in options]
    #     double_minus_options = ["--" + option for option in options]
    #     options.extend(minus_options)
    #     options.extend(double_minus_options)
    # augment_options(legal_options)
    option_dict = {}
    for i, arg in enumerate(argv):
        if i % 2 == 1 or i == 0:
            continue
        assert arg in legal_options, f"illegal option {arg}"
        assert arg.startswith("--")
        option_key = arg[2:]
        option_value = argv[i+1]
        assert not option_key in option_dict.keys()
        option_dict[option_key] = option_value
    return mp3_path, option_dict
    
        
def modify_mp3(mp3_path, caption=None, artist=None, album=None, lyrics_path=None, image_path=None, comment=None, clear=None):
    tag = ID3(mp3_path)
    if caption:
        if caption.lower() == "null":
            tag.pop("TIT2", None)
        else:
            tag.pop("TIT2", None)
            tag.add(TIT2(encoding=3, text=[caption,]))
        
    if artist:
        if artist.lower() == "null":
            tag.pop("TPE1", None)
        else:
            tag.pop("TPE1", None)
            tag.add(TPE1(encoding=3, text=[artist,]))
            
    if album:
        if album.lower() == "null":
            tag.pop("TALB", None)
        else:
            tag.pop("TALB", None)
            tag.add(TALB(encoding=3, text=[album,]))
            
    if image_path:
        if image_path.lower() == "null":
            for key in tag.keys():
                if key.startswith("APIC"):
                    image_key = key
            tag.pop(image_key, None)
        else:
            if image_path.endswith(".jpg") or image_path.endswith(".jpeg"):
                image_mime = "image/jpeg"
            elif image_path.endswith(".png"):
                image_mime = "image/png"
            elif image_path.endswith(".bmp"):
                image_mime = "image/bmp"
            else:
                print(f"Error: Unsupported image format")
                exit()
            with open(image_path, mode="rb", encoding="utf8") as image_file:
                image_data = image_file.read()
                image_frame = APIC(
                    encoding=3,
                    mime=image_mime,
                    type=3,
                    desc="Cover",
                    data=image_data
                )
                tag.add(image_frame)
    
    if lyrics_path:
        if lyrics_path.lower() == "null":
            for key in tag.keys():
                if key.startswith("USLT"):
                    lyrics_key = key
            tag.pop(lyrics_key, None)
        else:
            assert False, "Lyrics modification is not enable already, you can only remove the lyrics\n"
            lyrics_frame = USLT( # create a USLT frame
                encoding=3, # UTF-8 encoding
                lang="eng", # language code
                desc="Lyrics", # description of the lyrics
                text="Some lyrics here" # lyrics text
            )
            tag.add(lyrics_frame) # add the frame to the tag
            
    if comment:
        if comment.lower() == "null":
            keys = [key for key in tag.keys() if key.startswith("COMM")]
            for key in keys:
                del tag[key]
        else:
            assert False, "\nComment modification is not enable already, you can only remove the lyrics\n"
            
    if clear:
        keys = list(tag.keys())
        for key in keys:
            tag.pop(key, None)
            
    tag.save()


def show_mp3_metadata(mp3_path):
    tag = ID3(mp3_path) # create a tag object
    for frame in tag: # loop through all the frames in the tag
        if frame =="TIT2":
            key = "Caption"
        elif frame == "TPE1":
            key = "Artist"
        elif frame == "TALB":
            key = "Album"
        elif frame == "APIC" or frame == "APIC:":
            key = "Image"
        elif frame == "USLT":
            key = "Lyrics"
        else:
            key = frame

        if frame == "APIC" or frame == "APIC:":
            print(key, "Some Image", sep=": ")
        else:
            print(key, tag[frame], sep=": ") # print the frame name and value
        print()


def apply_mp3(mp3_path, options):
    if "caption" in options.keys():
        caption = options["caption"]
    elif "title" in options.keys():
        caption = options["title"]
    else:
        caption = None
    
    if "album" in options.keys():
        album = options["album"]
    else:
        album = None
    
    if "artist" in options.keys():
        artist = options["artist"]
    elif "singer" in options.keys():
        artist = options["singer"]
    else:
        artist = None
        
    if "image" in options.keys():
        image_path = options["image"]
    elif "cover" in options.keys():
        image_path = options["cover"]
    else:
        image_path = None

    if "lyrics" in options.keys():
        lyrics_path = options["lyrics"]
    else:
        lyrics_path = None
    
    if "comment" in options.keys():
        comment = options["comment"]
    elif "comments" in options.keys():
        comment = options["comments"]
    else:
        comment = None
        
    if "clear" in options.keys():
        clear = True
    else:
        clear = False

    if "show" in options.keys() or "list" in options.keys():
        show_mp3_metadata(mp3_path)
    else:
        modify_mp3(mp3_path=mp3_path,
               caption=caption,
               artist=artist,
               album=album,
               lyrics_path=lyrics_path,
               image_path=image_path,
               comment=comment,
               clear=clear
               )        

if __name__ == "__main__":
    mp3_path, options = parse_arg()
    if not os.path.exists(mp3_path):
        assert False, f"MP3 file/directory {mp3_path} does not exist\n"
    elif os.path.isfile(mp3_path):
        apply_mp3(mp3_path, options)
    else:
        for mp3_name in os.listdir(mp3_path):
            mp3_filepath = os.path.join(mp3_path, mp3_name)
            if os.path.isfile(mp3_filepath) and mp3_name.endswith(".mp3"):
                apply_mp3(mp3_filepath, options)
    
    
        
        