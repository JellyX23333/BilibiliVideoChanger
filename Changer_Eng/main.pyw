from MAIN_UI import Ui_MainWindow
from MAIN_object_V1 import AllVideos
from MAIN_video_functions import change_format, change_bullet_to_ass

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QBrush, QImage, QPalette

from tkinter.filedialog import askdirectory
from tkinter import Tk

import sys
import os
from multiprocessing import Process


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
        self.current_process = None
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
        if self.current_process:
            self.current_process.join()
        self.current_process = Process(target=self.__process_button_start, args=(self,))
        self.current_process.start()

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

    def __pre_process_danmaku(self, danmaku_file_path, animate, episode):  # return that changed name
        try:
            return change_bullet_to_ass(danmaku_file_path, animate, episode)
        except PermissionError:
            self.__update_log(danmaku_file_path + "-- no access")
            # DO - send a notice to user

    @staticmethod
    def __process_button_start(_class):
        # detect
        try:
            _class.video
        except AttributeError:
            if not os.path.isdir(_class.lineEdit.text()):
                _class.textBrowser.setText("Please check your input directory, you have to select a valid directory.")
                return
            else:
                _class.button_confirm()

        if _class.video.videos.__len__() == 0:
            _class.textBrowser.setText("There is no bilibili video found in this directory.")
            return

        # reset
        _class.log = ""
        _class.textBrowser.setText("")
        _class.progressBar.setValue(0)

        # start
        all_task = len(_class.video.videos) * 4  # do a estimation of task
        _class.progressBar.setMaximum(all_task)  # give the task number to the progress bar
        _class.__update_log("start processing\n")
        _class.__update_log("pre-processing videos\n")

        outer_count = 0
        for episode in _class.video.videos:

            # pre-process of danmaku
            name = _class.__pre_process_danmaku(episode.danmaku, episode.animate_name, episode.episode_name)
            _class.video.videos[outer_count].danmaku = name
            _class.__update_log("Danmaku file of {}-{}\n".format(_class.video.videos[outer_count].episode_name,
                                                                 _class.video.videos[outer_count].episode_name))
            _class.__update_log("----pre-process complete\n")
            _class.__update_progress_bar()

            # pre-process of video file
            count = 0
            for video_path in episode.video_file:
                name = _class.__pre_process_video(video_path)
                try:
                    _class.video.videos[outer_count].video_file[count] = name
                except TypeError:
                    _class.__update_log(str(type(_class.video.videos[outer_count].video_file[count])) +
                                        "- {} - A type error has occurred "
                                        .format(_class.video.videos[outer_count].video_file[count]))
                count += 1

            _class.__update_log("Video file of {}-{}\n".format(_class.video.videos[outer_count].episode_name,
                                                               _class.video.videos[outer_count].animate_name))
            _class.__update_log("----pre-process complete\n")
            _class.__update_progress_bar()

            # combine
            original_files = _class.video.videos[outer_count].video_file

            _class.video.videos[outer_count].combine_videos()
            _class.__update_log("Video file of {}-{}\n".format(_class.video.videos[outer_count].episode_name,
                                                               _class.video.videos[outer_count].animate_name))
            _class.__update_log("----FFMpeg has finished its process\n")

            if os.path.isfile(_class.video.videos[outer_count].video_file):  # check the combining
                _class.__update_log("---- Combining success")
            else:
                _class.__update_log("---- A problem has occurred with combining files {}".format(original_files))
            del original_files

            _class.__update_progress_bar()

            # output
            if _class.output_to_dir:
                if os.path.isdir(_class.lineEdit_2.text()):
                    try:
                        episode.change_file_location(_class.lineEdit_2.text(),
                                                     one_ani_one_dir=_class.one_ani_one_dir,
                                                     one_ep_one_dir=_class.one_ep_one_dir)
                        _class.__update_log("episode {}-{}\n".format(_class.video.videos[outer_count].episode_name,
                                                                     _class.video.videos[outer_count].animate_name))
                        _class.__update_log("---- files output to dir {}\n".format(_class.lineEdit_2.text()))
                    except FileExistsError:
                        _class.__update_log("episode {}-{}\n".format(_class.video.videos[outer_count].episode_name,
                                                                     _class.video.videos[outer_count].animate_name))
                        _class.__update_log("---- file already exist\n")
                        _class.__update_log("----skip output redirection\n")
                else:   # If incorrect path have been entered
                    _class.textBrowser.setText("Please check your output directory\n")
                    _class.textBrowser.setText("Terminating Process")
                    return
            else:
                _class.__update_log("Episode {}-{}\n".format(_class.video.videos[outer_count].episode_name,
                                                             _class.video.videos[outer_count].animate_name))
                _class.__update_log("----skip output redirection\n")

            _class.__update_progress_bar()

            outer_count += 1

    @ staticmethod
    def __pre_process_video(video_file_path):         # return the changed name
        return change_format(video_file_path)


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
    window = VideoChangerUI(background="bg0.jpg")
    window.show()
    sys.exit(app.exec_())
