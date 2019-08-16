from Niconvert import convert
import os
import json

# 'danmaku' is Japanese 「弾幕」's romanji「ロマン字」, in english it is called"bullet screen" and called ‘弹幕’ in chinese.
# I use it here in that bilibili uses it to name their bullet screen file.


# get the file to be combine together
def get_files(path):
    if not os.path.exists(path):
        raise NotADirectoryError

    episode_list = []

    for root, sub_dir, files in os.walk(path):  # collect each episodes and return their info
        if is_animate(root):
            info_file = os.path.join(root, "entry.json")        # the path to episode and animate information
            danmaku = os.path.join(root, "danmaku.xml")          # the path to the danmaku file
            blvs = []                                           # file for the path to all .blv files

            for sub_root, sub_root_dir, sub_root_file in os.walk(root):  # loop to find all
                if is_episode(sub_root):
                    for file in sub_root_file:
                        target_path = os.path.join(sub_root, file)
                        if is_blv(target_path):
                            blvs.append(target_path)
                        elif is_flv(target_path):
                            blvs.append(target_path)

            # save the information of this episode into list
            episode_list.append({"animate_info": info_file, "video": blvs, "Bullet": danmaku})

    # return back the list of episodes
    return episode_list


def is_animate(directory):
    test_dir = directory
    for root, sub_dir, files in os.walk(test_dir, topdown=True):
        if "entry.json" in files:    # if entry.json file in directory this is a episode directory
            return True
        else:
            return False


def is_episode(directory):  # to check if the directory is a episode directory that contain .blv video files
    test_dir = directory

    for root, sub_dir, files in os.walk(test_dir, topdown=True):
        if "0.blv" in files:    # if 0.blv file in directory this is a episode directory
            return True
        elif "0.flv" in files:
            return True
        else:
            return False


def is_blv(path):   # check if this is a blv file by check the end
    if os.path.isfile(path):
        if os.path.basename(path).split(".")[-1] == "blv":
            return True
    return False


def is_flv(path):
    if os.path.isfile(path):
        if os.path.basename(path).split(".")[-1] == "flv":
            return True
    return False


# change file format
def change_format(file_path):
    if not os.path.isfile(file_path):   # detect if the path is correct
        raise FileNotFoundError

    dir_path = os.path.dirname(file_path)
    original_name = os.path.basename(file_path)

    new_name_list = list(os.path.basename(file_path).split("."))
    new_name_list[-1] = "flv"
    new_name = new_name_list[0] + "." + new_name_list[-1]

    if os.path.isfile(new_name):
        return new_name

    os.rename(os.path.join(dir_path, original_name), os.path.join(dir_path, new_name))

    return os.path.join(dir_path, new_name)


def get_info(episode_dic, request):    # get the information of the episode(animate's name or episode'name)
    file_path = episode_dic['animate_info']
    file = open(file_path, 'r', encoding='utf-8')  # if not decode as utf-8 error would occur
    data = json.load(file)
    file.close()

    name = ""

    if request == "__animate_name__":
        name = data["title"]

    elif request == "__episode_name__":
        name = data["ep"]["index_title"]

    return name  # return the value of what the request wanted


def animate_dir(animate, destination):  # check is the animate dir all ready existed, if not create
    # the animate dir
    animate_dir_path = os.path.join(destination, animate)
    # what is under the destination dir
    dirs = os.listdir(destination)
    if animate not in dirs:
        os.makedirs(animate_dir_path)
    # return the path to the animate dir
    return animate_dir_path


def episode_dir(episode, destination):
    # the animate dir
    episode_dir_path = os.path.join(destination, episode)
    # what is under the destination dir
    dirs = os.listdir(destination)
    if episode not in dirs:
        os.makedirs(episode_dir_path)
    # return the path to the animate dir
    return episode_dir_path


def move_episode(video, animates_dir_name):                                                     # test passed
    # variable
    new_location = os.path.join(animates_dir_name, os.path.basename(video))
    # move
    os.rename(video, new_location)


def move_danmaku(danmaku, animates_dir_name):                                                   # test passed
    if not danmaku:
        return
    # variable
    new_location = os.path.join(animates_dir_name, os.path.basename(danmaku))
    # move
    os.rename(danmaku, new_location)


def change_bullet_to_ass(danmaku, episode_name, animate_name):

    if not os.path.isfile(danmaku):
        return None

    # variables
    new_name = os.path.dirname(danmaku) + "\\" + animate_name + '_' + episode_name + ".ass"     # the new name of file

    danmaku_path = os.path.dirname(danmaku)

    file = open(danmaku_path)
    content = file.read()
    file.close()

    content = convert(content, "1920:1080", "Microsoft YaHei", 64, 4, 0, 0)     # input, resolution, font, font size,
                                                                                # line count, bottom margin, shift
    '''
    danmaku2ass = os.path.dirname(str(__file__)) + "/Libs/Danmu2Ass/Kaedei.Danmu2Ass.exe"   # path to danmaku2ass
    command = "{} {}"                                                                       # the format of command

    if os.path.isfile(new_name):
        return new_name

    # change file type to ass
    os.system(command.format(danmaku2ass, danmaku))
    '''

    # change name of the changed ass file
    danmaku = list(os.path.basename(danmaku).split("."))
    danmaku = danmaku_path + "/" + str(danmaku[0]) + ".ass"
    os.rename(danmaku, new_name)

    # write the new content in
    file = open(new_name, "w")
    file.write(content)
    file.close()

    # return the new name back
    return new_name
