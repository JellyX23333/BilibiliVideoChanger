# Bilibili视频更改器
把bilibili的视频(安卓手机)改为电脑播放器可读文件
沒有exe版（PyInstaller打包失敗了）
 - 将视频重命名为.flv并使用FFMpeg进行整合
 - 将弹幕文件从.xml格式，改为.ass格式，使用[danmu2ass](https://github.com/ikde/danmu2ass/tree/master/Danmu2Ass)
 - 根据动漫名和集名对视频进行分类
 
## 目录
* [语言](#语言)
* [系统要求](#系统要求)
* [库](#库)
* [环境](#环境)

## 语言
Python 3.7.1

## 系统要求 
只进行过Windows 10的测试（本人没有mac并且还没有进行过linux的测试）

## 库
- os(Python自带)
- sys(Python自带)
- json(Python自带)
- tkinker(Python自带)
- PyQt5(需自行安装)

## 环境
- 安装所有的[库](#库)
- 创建文件夹「Libs」并把[Nicovert.py](https://github.com/ikde/danmu2ass/blob/master/Danmu2Ass/PythonFile/Niconvert.py)文件放进去
- 把你想要的背景图片放入与main.py相同的文件夹, 将其命名为「bg0.png」(如果不要背景图片，需自行该代码)
 -[代码文件](./Changer_中文/main.py)- 
```
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoChangerUI(background="bg0.png")
    window.show()
    sys.exit(app.exec_())
```
