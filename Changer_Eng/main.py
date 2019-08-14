from MAIN_UI import Ui_MainWindow
from MAIN_object_V1 import AllVideos
from MAIN_video_functions import change_format, change_bullet_to_ass

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QBrush, QImage, QPalette

from tkinter.filedialog import askdirectory
from tkinter import Tk

import sys


# the main window structure
class VideoChangerUI(QMainWindow, Ui_MainWindow):
    def __init__(self, background=None):
        # set up UI
        super(VideoChangerUI, self).__init__()
        self.setupUi(self)
        self.textBrowser_2.setText("Please enter the path you wish in the input line or select browser\n"
                                   "You can view the video in your selected dir in the window on the right by clicking"
                                   " the confirm button\n"
                                   "If you want all video to be direct to a certain directory, select the enable box ne"
                                   "xt to the output line. You also need to enter the path in the output line.\n"
                                   "To start the process, click start.")

        # variables
        self.video_names = []
        self.output_to_dir = False
        self.with_danmaku = True
        self.one_ep_one_dir = False
        self.one_ani_one_dir = False

        # process log
        self.log = ""

        # set a background if wanted - back ground image file name need to be bg0.png
        if background:
            image = QImage(background)              # get the image
            image = image.scaled(self.size())       # resize to window size
            palette = QPalette()
            palette.setBrush(10, QBrush(image))
            self.setPalette(palette)                # set the image

        # signal and slots
        # push button tachi with signal 「clicked」
        self.pushButton_2.clicked.connect(self.button_browse_input)   # browse the computer to find the directory
        self.pushButton.clicked.connect(self.button_confirm)    # confirm the path found by browse
        self.pushButton_3.clicked.connect(self.button_start)    # start the process of combining
        self.pushButton_4.clicked.connect(self.button_browse_output)
        # check box tachi- signal「stateChanged」
        self.checkBox.stateChanged.connect(self.output_dir_state)       # when check box's state been changed,
        self.checkBox_2.stateChanged.connect(self.output_with_danmaku)  # change the variable at the same time
        self.checkBox_4.stateChanged.connect(self.one_ep_per_dir)
        self.checkBox_5.stateChanged.connect(self.one_ani_per_dir)

    # slots
    def button_confirm(self):
        self.video = AllVideos(str(self.lineEdit.text()))   # create a AllVideo class named video
        self.video_names = sort_videos(self.video)          # list videos in the AllVideo object
        self.textBrowser_2.setText(self.video_names)        # show the texts in textBrowser

    def button_browse_input(self):
        # hide the tk window
        root = Tk()
        root.withdraw()

        # use askdirectory to create a selecting window
        file_dir = askdirectory(title='Select the directory to be input from')

        # show the finding in the lineEdit bar
        self.lineEdit.setText(file_dir)

    def button_browse_output(self):
        # hide the tk window
        root = Tk()
        root.withdraw()

        # use askdirectory to create a selecting window
        file_dir = askdirectory(title='Select the directory to be output to')

        # show the finding in the lineEdit bar
        self.lineEdit_2.setText(file_dir)

    def button_start(self):
        # reset
        self.log = ""
        self.textBrowser.setText("")
        self.progressBar.setValue(0)

        # start
        all_task = len(self.video.videos)*4         # do a estimation of task
        self.progressBar.setMaximum(all_task)       # give the task number to the progress bar
        self.__update_log("start processing"
                          "pre-processing videos")

        outer_count = 0
        for episode in self.video.videos:

            # pre-process of danmaku
            name = self.__pre_process_danmaku(episode.danmaku, episode.animate_name, episode.episode_name)
            self.video.videos[outer_count].danmaku = name
            self.__update_log("Danmaku file of {}-{}".format(self.video.videos[outer_count].episode_name,
                                                             self.video.videos[outer_count].episode_name))
            self.__update_log("----pre-process complete")
            self.__update_progress_bar()

            # pre-process of video file
            count = 0
            for video_path in episode.video_file:
                name = self.__pre_process_video(video_path)
                try:
                    self.video.videos[outer_count].video_file[count] = name
                except TypeError:
                    print(type(self.video.videos[outer_count].video_file))
                count += 1
            self.__update_log("Video file of {}-{}"
                              "----pre-process complete".format(self.video.videos[outer_count].episode_name,
                                                                self.video.videos[outer_count].animate_name))
            self.__update_progress_bar()

            # combine
            self.video.videos[outer_count].combine_videos()
            self.__update_log("Video file of {}-{}".format(self.video.videos[outer_count].episode_name,
                                                           self.video.videos[outer_count].animate_name))
            self.__update_log("----combining complete")
            self.__update_progress_bar()

            # output
            if self.output_to_dir:
                try:
                    episode.change_file_location(self.lineEdit_2.text(),
                                                 one_ani_one_dir=self.one_ani_one_dir,
                                                 one_ep_one_dir=self.one_ep_one_dir)
                    self.__update_log("episode {}-{}".format(self.video.videos[outer_count].episode_name,
                                                             self.video.videos[outer_count].animate_name))
                    self.__update_log("---- files output to dir {}".format(self.lineEdit_2.text()))
                except FileExistsError:
                    self.__update_log("episode {}-{}".format(self.video.videos[outer_count].episode_name,
                                                             self.video.videos[outer_count].animate_name))
                    self.__update_log("---- file already exist")
            else:
                self.__update_log("Episode {}-{}".format(self.video.videos[outer_count].episode_name,
                                                         self.video.videos[outer_count].animate_name))
                self.__update_log("----skip output redirection")
                self.__update_progress_bar()

            outer_count += 1

    def output_dir_state(self):     # for check box
        if self.checkBox.checkState():
            self.output_to_dir = True
        else:
            self.output_to_dir = False

    def output_with_danmaku(self):  # for check box 2
        if self.checkBox_2.checkState():
            self.with_danmaku = True
        else:
            self.with_danmaku = False

    def one_ep_per_dir(self):       # for check box 4
        if self.checkBox_4.checkState():
            self.one_ep_one_dir = True
        else:
            self.one_ep_one_dir = False

    def one_ani_per_dir(self):      # for check box 5
        if self.checkBox_5.checkState():
            self.one_ani_one_dir = True
        else:
            self.one_ani_one_dir = False

    # external processes
    def __update_log(self, event):
        self.log += str(event)
        self.textBrowser.setText(self.log)

    def __update_progress_bar(self):
        value = self.progressBar.value()
        value += 1
        self.progressBar.setValue(value)

    @ staticmethod
    def __pre_process_video(video_file_path):         # return the changed name
        return change_format(video_file_path)

    @ staticmethod
    def __pre_process_danmaku(danmaku_file_path, animate, episode):     # return that changed name
        return change_bullet_to_ass(danmaku_file_path, animate, episode)


# some function outside of the window structure
def sort_videos(videos):
    video_list = ""
    for episode in videos:
        animate_name = episode.animate_name
        episode_name = episode.episode_name
        line = "{} - {}\n".format(animate_name, episode_name)
        video_list += line
    return video_list


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoChangerUI()
    window.show()
    sys.exit(app.exec_())
