# BilibiliVideoChanger
 Change the bilibili videos(saved in Andrion phones)to readable format
 - able to rename videos to .flv and perform combining with FFMpeg
 - able to change the danmaku file to .ass format with [danmu2ass](https://github.com/ikde/danmu2ass/tree/master/Danmu2Ass)
 - able to sort the the videos by anime and episode name
 
## Table of Content
* [Language](#language)
* [System requirements](#system-requirements)
* [Libs](#libs)
* [Environment](#environment)

## Language
Python 3.7.1

## System requirements 
The program is only tested on windows 10

## Libs
- os(Python standard lib)
- sys(Python standard lib)
- json(Python standard lib)
- tkinker(Python standard lib)
- PyQt5(can install with pip)

## Environment
- All [lib](#libs) installed.
- Make a directory called libs and put build danmu2ass files in.
- Put any image you want in the same directory as main.py, and name the image file bg0.png.(If don't want any background image, change the code)
'''
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoChangerUI(background="bg0.png")
    window.show()
    sys.exit(app.exec_())
'''
