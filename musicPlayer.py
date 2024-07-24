import textwrap
import tkinter as tk
from PIL import Image, ImageTk
import pygame
import os
#---------------音乐播放-------------
class Music():
    def __init__(self,music_list,lrc_list):
        self.music_list = music_list #所有音乐文件列表
        self.lrc_list=lrc_list #所有歌词文件列表
        self.music_index=0 #音乐序号索引
        self.pause_state=0 #暂停状态
        self.change_state=0 #切歌状态
    def play_music(self): #音乐重播
        pygame.mixer.music.load(self.music_list[self.music_index])
        pygame.mixer.music.play()
    def next_music(self): #切换下一首
        self.music_index = (self.music_index + 1) % len(self.music_list)
        pygame.mixer.music.load(self.music_list[self.music_index])
        self.change_state=1
        if self.pause_state==0:
            pygame.mixer.music.play()
            self.change_state=0
    def post_music(self): #切换上一首
        self.music_index=(self.music_index-1)%len(self.music_list)
        pygame.mixer.music.load(self.music_list[self.music_index])
        self.change_state=1  #切歌状态置1
        if self.pause_state == 0: #如果没有暂停
            pygame.mixer.music.play() #继续播放下一首
            self.change_state=0  #此时切歌状态清0
    def pause_music(self):
        if self.change_state == 0: #如果没有切歌
            pygame.mixer.music.pause() #正常暂停
        else:                      #如果切歌了
            pygame.mixer.music.stop()  #该音乐停止，切换加载下一首
        self.pause_state=1
    def unpause_music(self):
        if self.change_state==0:   #如果没有切歌
            pygame.mixer.music.unpause() #正常继续播放
        else:                       #如果切歌了
            pygame.mixer.music.play() #按继续播放新的音乐
        self.pause_state=0
    def get_music(self): #输出音乐的名字
        return self.music_list[self.music_index]
    def get_lrc(self): #输出该音乐的歌词
        with open(self.lrc_list[self.music_index], 'r', encoding='utf-8') as file: #读取歌词文件
            lrc_lines = file.readlines()
        lrc = []
        for line in lrc_lines:
            parts = line.strip().split(']')
            if len(parts) > 1:
                time_str = parts[0][1:]
                content = parts[1].strip()
                lrc.append((time_str, content)) #分为时间点，和歌词两部分
        return lrc

#----------------主框架------------------
class MainWindow(tk.Tk):
    def __init__(self,music_list,lrc_list):
        #tk
        self.root = tk.Tk()
        self.root.title('音乐播放器')
        self.root.geometry('600x250') # 设置窗口大小
        self.root.resizable(False, False) # 禁止调整窗口大小
        #音乐
        self.music_list=music_list #所有音乐的列表
        self.lrc_list=lrc_list  #所有歌词文件列表
        self.music=Music(self.music_list,self.lrc_list)
        pygame.mixer.init()
        self.music.play_music()
        #全局变量
        self.is_update=1 #歌词是否继续滚动bool型变量
        self.music_name = self.music.get_music()[7:-4]#歌曲的名字
        #加载的图片
        self.image = Image.open('bg.png').resize((200, 200))
        self.photo = ImageTk.PhotoImage(self.image)
        self.signimage = Image.open('sign.png').resize((50, 65))
        self.signphoto = ImageTk.PhotoImage(self.signimage)
        #显示
        self.display()

    def update_button(self):
        def change_play():
            self.music.play_music()
            self.display_lrc()
        def change_pause():
            self.music.pause_music()
            self.button2.config(text='继续',command=change_unpause)
            self.is_update=0
            self.display_lrc(0)
        def change_unpause():
            self.music.unpause_music()
            self.button2.config(text='暂停',command=change_pause)
            self.is_update=1
            self.display_lrc(0)
        def change_next():
            self.music.next_music()
            self.music_name=self.music.get_music()[7:-4]
            self.musicLabel.config(text=self.music_name)
            self.display_lrc(0)
        def change_post():
            self.music.post_music()
            self.music_name=self.music.get_music()[7:-4]
            self.musicLabel.config(text=self.music_name)
            self.display_lrc(0)
        self.button1 = tk.Button(self.playerframe, text='重播', fg='red', bg='skyblue',height=3,width=6,command=change_play)
        self.button1.pack(side='top')
        self.button2=tk.Button(self.playerframe,text='暂停',fg='red',bg='skyblue',height=3,width=6,command=change_pause)
        self.button2.pack(side='bottom')
        self.button3=tk.Button(self.playerframe,text='下一首',fg='red',bg='skyblue',height=3,width=6,command=change_next).pack(side='left')
        self.button4=tk.Button(self.playerframe,text='上一首',fg='red',bg='skyblue',height=3,width=6,command=change_post).pack(side='right')
        self.sign=tk.Label(self.playerframe,image=self.signphoto,borderwidth=0)
        self.sign.image=self.signphoto
        self.sign.pack(side='top')

    # 解析歌词时间
    def parse_time_str(self, time_str):
        minutes, seconds = map(float, time_str.split(':'))
        return minutes * 60 + seconds
    #显示歌词
    def display_lrc(self, index=0,pause=False):
        if self.is_update==1:
            self.lrc = self.music.get_lrc()
            if index < len(self.lrc):
                time_str, content = self.lrc[index]
                # 根据中英文字符数进行自动换行
                content = textwrap.fill(content, width=30, break_long_words=False)
                self.lrcLabel.config(text=content)
                next_index = index + 1
                if next_index < len(self.lrc):
                    next_time_str, _ = self.lrc[next_index]
                    next_time = self.parse_time_str(next_time_str)
                    current_time = pygame.mixer.music.get_pos() / 1000
                    delay = next_time - current_time
                    if self.is_update==1:
                        self.root.after(int(delay * 1000), lambda: self.display_lrc(next_index))
            else:
                self.lrcLabel.config(text='无歌词')
    #主显示
    def display(self):
        #定义组件框架
        self.playerframe = tk.Frame(self.root, borderwidth=0, relief='solid', bg='steelblue')
        self.topframe=tk.Frame(self.root,borderwidth=3,relief='solid')
        self.disframe1=tk.Frame(self.root,borderwidth=0,relief='solid')
        self.disframe2=tk.Frame(self.root,borderwidth=0,relief='solid')
        self.bgframe=tk.Frame(self.root,borderwidth=0,relief='solid')

        #组固定文本和背景图片
        self.label = tk.Label(self.topframe, text='MusicPlayer', font=('Arial', 15), height=2, width=60, fg='red',bg='skyblue')
        self.label.pack()
        self.musicLabel=tk.Label(self.disframe1,text=self.music_name,font=('Arial', 13), fg='blue', bg='skyblue', height=1,width=60, pady=10, padx=10)
        self.musicLabel.pack(side='top')
        self.lrcLabel = tk.Label(self.disframe2, text='无歌词', font=('Arial', 13), fg='blue', bg='skyblue', height=10,width=50, pady=10, padx=10,justify='center')
        self.lrcLabel.pack(side='bottom')
        self.bg=tk.Label(self.bgframe,image=self.photo)
        self.bg.image=self.photo
        self.bg.pack()
        #组件布局
        self.topframe.pack()
        self.playerframe.pack(side='left')
        self.bgframe.pack(side='left')
        self.disframe1.pack(side='top')
        self.disframe2.pack(side='right')
        #显示
        self.update_button()
        self.display_lrc()
        self.root.mainloop()

if __name__=='__main__':
    # 指定文件夹路径
    music_path = 'musics'
    # 读取文件夹中所有文件的名字为一个列表
    music_list = [os.path.join(music_path, f) for f in os.listdir(music_path)]
    lrc_path='lrc'
    lrc_list = [os.path.join(lrc_path, f) for f in os.listdir(lrc_path)]
    MainWindow(music_list=music_list,lrc_list=lrc_list)