from MAIN_video_functions import animate_dir, move_episode, move_danmaku, episode_dir


class Episode:
    def __init__(self, episode_info):
        from MAIN_video_functions import get_info
        import os

        # all self. variables
        self.animate_name, self.episode_name, self.episode_index = get_info(episode_info)   # to create new name
        self.video_file_path = os.path.dirname(episode_info["video"][0])                    # where's the video stored
        self.video_file = list(episode_info["video"])                                       # video files
        self.danmaku = episode_info["Bullet"]                                               # the danmaku file

    def combine_videos(self):
        import os

        if len(self.video_file) == 1:   # if the video is already a single flv file
            if self.video_file[0].split(".") == "flv":
                return

        # variables
        new_name = self.episode_index + '_' + self.animate_name + "_" + self.episode_name + ".flv"
        new_name = new_name.replace(" ", "_")
        new_name = new_name.replace("/", "_")

        target_path = self.video_file_path

        # create destination file
        if not os.path.isfile(target_path+"\\"+new_name):
            file = open(target_path+"\\"+new_name, "x")
            file.close()

        # clear the file and then write in the videos to combine
        file = open(os.getcwd() + "\\" + "FileList.txt", "w")
        for video in self.video_file:
            file.write("file " + "'" + video + "'\n")
        file.close()

        # start combine
        os.system("ffmpeg -f concat -safe 0 -y -i FileList.txt -c copy {}\\{}"
                  .format(target_path, new_name))

        # finish combine
        self.video_file = target_path + "\\" + new_name

    def change_file_location(self, destination, one_ani_one_dir=False, one_ep_one_dir=False):
        path = destination

        # check is the animate dir all ready existed, if not create
        if one_ani_one_dir:
            path = animate_dir(self.animate_name, destination=path)
            if one_ep_one_dir:
                path = episode_dir(self.episode_name, self.episode_index, destination=path)
        elif one_ep_one_dir:
            path = episode_dir(self.episode_name, self.episode_index, destination=path)

        # move episode and bullet into the animate dir
        move_episode(self.video_file, path)
        move_danmaku(self.danmaku, path)


# A class that contain all animates under the path given
class AllVideos:
    def __init__(self, path):
        from MAIN_video_functions import get_files

        # the location where the animate files located
        self.files_location = path

        # the videos that is under the path
        self.videos = list(get_files(self.files_location))

        count = 0
        for episode in self.videos:
            self.videos[count] = (Episode(episode))
            count += 1

    def __iter__(self):
        self.index = len(self.videos)
        return self

    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.videos[self.index]
