import easygui
import traceback
import sys
import os


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
        self.setWindowTitle("Bilibili Video Changer")

        # ------------- variables
        # str
        self.log = ""
        # class
        self.thread_pool = QThreadPool()
        # list
        self.video_names = list()
        # bool
        self.errors = False
        self.output_to_dir = False
        self.with_danmaku = True
        self.one_ep_one_dir = False
        self.one_ani_one_dir = False

        # set a background if wanted
        if background:
            image = QImage(background)              # get the image
            image = image.scaled(self.size())       # resize to window size
            palette = QPalette()
            palette.setBrush(10, QBrush(image))
            self.setPalette(palette)                # set the image

        # ------------ signal and slots
        # push buttons with signal 「clicked」
        self.pushButton_2.clicked.connect(self.button_browse_input)     # browse the computer to find the directory
        self.pushButton.clicked.connect(self.button_confirm)            # confirm the path found by browse
        self.pushButton_3.clicked.connect(self.button_start)            # start the process of combining
        self.pushButton_4.clicked.connect(self.button_browse_output)    # browse to find the output directory
        # check boxes- signal「stateChanged」
        self.checkBox.stateChanged.connect(self.output_dir_state)       # when check box's state been changed,
        self.checkBox_2.stateChanged.connect(self.output_with_danmaku)  # change the variable at the same time
        self.checkBox_4.stateChanged.connect(self.one_ep_per_dir)       # one episode per one dir when saving the file
        self.checkBox_5.stateChanged.connect(self.one_ani_per_dir)      # the videos one animate save into one dir

    # ----------------- slots to be connected
    # connected with pushButton
    def button_confirm(self):
        # create a AllVideo class named video
        try:
            self.video = AllVideos(str(self.lineEdit.text()))
        except NotADirectoryError:
            easygui.msgbox("A valid input directory is required", title="Warning")
            return

        if self.video.videos.__len__() == 0:
            easygui.msgbox("There is no bilibili video found in this directory.", title="Warning")
            del self.video
            return

        self.video_names = sort_videos(self.video)          # list videos in the AllVideo object
        self.textBrowser_2.setText(self.video_names)        # show the texts in textBrowser

    # connected with pushButton 2
    def button_browse_input(self):
        # hide the tk window
        root = Tk()
        root.withdraw()

        # use askdirectory to create a selecting window
        file_dir = askdirectory(title='Select the directory to be input from')

        # show the finding in the lineEdit bar
        self.lineEdit.setText(file_dir)

    # connected with pushButton 4
    def button_browse_output(self):
        # hide the tk window
        root = Tk()
        root.withdraw()

        # use askdirectory to create a selecting window
        file_dir = askdirectory(title='Select the directory to be output to')

        # show the finding in the lineEdit bar
        self.lineEdit_2.setText(file_dir)

    # connected with pushButton 3
    def button_start(self):
        # reset
        self.log = ""
        self.textBrowser.setText("")
        self.progressBar.setValue(0)
        self.errors = False
        self.thread_pool.clear()

        # detect
        try:
            assert self.videos
        except AssertionError:
            if not os.path.isdir(self.lineEdit.text()):
                easygui.msgbox("A valid input directory is required", title='Warning')
                return
            else:
                easygui.msgbox("Please confirm first before starting the process.", title="Warning")
                return
        except AttributeError:
            if not os.path.isdir(self.lineEdit.text()):
                easygui.msgbox("A valid input directory is required", title='Warning')
                return
            self.button_confirm()

        if not os.path.isdir(self.lineEdit_2.text()):
            easygui.msgbox("A valid output directory is required", title="Warning")
            return

        # set thread ready
        thread = Thread(self.__process_button_start,
                        self.progressBar, self.video,
                        self.output_to_dir, self.one_ep_one_dir, self.one_ani_one_dir,
                        self.lineEdit_2.text()
                        )

        # connect signals
        thread.signals.error.connect(self.thread_error)
        thread.signals.finish.connect(self.thread_process_finished)
        thread.signals.log.connect(self.__update_log)
        thread.signals.progress.connect(self.__update_progress_bar)

        # execute thread
        self.thread_pool.start(thread)

    # connected with checkBox
    def output_dir_state(self):     # for check box
        if self.checkBox.checkState():
            self.output_to_dir = True
        else:
            self.output_to_dir = False

    # connected with checkBox 2
    def output_with_danmaku(self):  # for check box 2
        if self.checkBox_2.checkState():
            self.with_danmaku = True
        else:
            self.with_danmaku = False

    # connected with checkBox 4
    def one_ep_per_dir(self):       # for check box 4
        if self.checkBox_4.checkState():
            self.one_ep_one_dir = True
        else:
            self.one_ep_one_dir = False

    # connected with checkBox 5
    def one_ani_per_dir(self):      # for check box 5
        if self.checkBox_5.checkState():
            self.one_ani_one_dir = True
        else:
            self.one_ani_one_dir = False

    # connected with thread's signal「finish」
    def thread_process_finished(self):
        self.__update_log("\n---------\nProcessing finished")

        if self.errors:
            if easygui.boolbox("Error has occurred in the process\ncreate a log file?", title="Bilibili Video Changer"):
                with open("runtime_log.txt", "w") as log_file:
                    log_file.write(self.log)
                    log_file.close()
                easygui.msgbox("The runtime log has saved into file {}\\runtime_log.txt"
                               .format(os.path.dirname(__file__)))

    # connected with thread's signal 「error」
    def thread_error(self, error_info):
        self.errors += 1
        self.__update_log(error_info)

    # external processes
    def __update_log(self, event):
        self.log += str(event)
        self.textBrowser.setText(self.log)

    def __update_progress_bar(self):
        value = self.progressBar.value()
        value += 1
        self.progressBar.setValue(value)

    # ----------- staticmethod

    # this function is to be pass to the thread worker
    @staticmethod
    def __process_button_start(progress_bar, videos,
                               output_to_dir, one_ep_one_dir, one_ani_one_dir,
                               output_dir,
                               signal_error, signal_progress, signal_log):

        # start
        all_task = len(videos.videos) * 4  # do a estimation of task
        progress_bar.setMaximum(all_task)  # give the task number to the progress bar
        signal_log.emit("start processing\n")
        signal_log.emit("pre-processing videos\n")

        outer_count = 0
        for episode in videos.videos:

            # pre-process of danmaku
            signal_log.emit("Danmaku file of {}-{}\n".format(videos.videos[outer_count].episode_name,
                                                             videos.videos[outer_count].episode_name))
            try:
                name = change_bullet_to_ass(episode.danmaku,
                                            episode.animate_name, episode.episode_name, episode.episode_index)
                videos.videos[outer_count].danmaku = name
                signal_log.emit("----pre-process complete\n")
                signal_progress.emit()
            except PermissionError:
                signal_error.emit("{} has occurred, error value:{}\nError detail:\n{}\n".format(sys.exc_info()[0],
                                                                                                sys.exc_info()[1],
                                                                                                traceback.format_exc()))
                signal_log.emit("----pre-process failed\n")

            # pre-process of video file
            count = 0
            for video_path in episode.video_file:
                name = change_format_to_flv(video_path)
                videos.videos[outer_count].video_file[count] = name
                count += 1

            signal_log.emit("Video file of {}-{}\n".format(videos.videos[outer_count].episode_name,
                                                           videos.videos[outer_count].animate_name))
            signal_log.emit("----pre-process complete\n")
            signal_progress.emit()

            # combine
            original_files = videos.videos[outer_count].video_file

            videos.videos[outer_count].combine_videos()
            signal_log.emit("Video file of {}-{}\n".format(videos.videos[outer_count].episode_name,
                                                           videos.videos[outer_count].animate_name))
            signal_log.emit("----FFMpeg has finished its process\n")

            if os.path.isfile(videos.videos[outer_count].video_file):  # check the combining
                signal_log.emit("---- Combining success\n")
            else:
                signal_log.emit("---- A problem has occurred with combining files {}\n".format(original_files))

            signal_progress.emit()

            # output
            if output_to_dir:
                if os.path.isdir(output_dir):
                    signal_log.emit("episode {}-{}\n".format(videos.videos[outer_count].episode_name,
                                                             videos.videos[outer_count].animate_name))
                    try:
                        episode.change_file_location(output_dir,
                                                     one_ani_one_dir=one_ani_one_dir,
                                                     one_ep_one_dir=one_ep_one_dir)
                    except FileExistsError:
                        signal_log.emit("---- file already exist\n")
                        signal_log.emit("----skip output redirection\n")
                    else:
                        signal_log.emit("---- files output to dir {}\n".format(output_dir))
                else:   # If incorrect path have been entered
                    signal_log.emit("Please check your output directory\n")
                    signal_log.emit("Terminating Process\n")
                    return
            else:
                signal_log.emit("Episode {}-{}\n".format(videos.videos[outer_count].episode_name,
                                                         videos.videos[outer_count].animate_name))
                signal_log.emit("----skip output redirection\n")

            signal_progress.emit()

            outer_count += 1


# some function outside of the window structure
def sort_videos(videos):
    video_list = ""
    for episode in videos:
        line = "{} - {}\n".format(episode.animate_name, episode.episode_name)
        video_list += line
    return video_list


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoChangerUI(background="bg0.jpg")
    window.show()
    sys.exit(app.exec_())
    
