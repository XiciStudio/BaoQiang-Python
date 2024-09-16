import os
from zipfile import ZipFile
from module import *
import tkinter.messagebox
from ttkbootstrap.tooltip import ToolTip

bqtj_pictures_dir = ''


def extract_res_file(res_file_path):
    global bqtj_pictures_dir
    cache_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp')
    bqtj_pictures_dir = os.path.join(cache_dir, 'bqtj_Pictures')

    if not os.path.exists(bqtj_pictures_dir):
        os.makedirs(bqtj_pictures_dir)

    with ZipFile(res_file_path, 'r') as zip_file:
        zip_file.extractall(bqtj_pictures_dir)


# Usage example
res_file_path = './res.dat'
extract_res_file(res_file_path)
from module import *
from random import choice
import requests

import keyboard
from tkhtmlview import *
import ttkbootstrap as ttk
from ttkbootstrap import Querybox
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *


def on_key_press(event):
    if event.keysym == 'Down':
        change_theme()
    if event.keysym == 'Home':
        e1.delete('0', END)
        e1.insert('0', 'xcgam')
        e2.delete('0', END)
        e2.insert('0', '120824aa')
        get_list()
    if event.keysym == 'End':
        try:
            selected_item = tv.item(tv.selection())
            selected_index = str(selected_item['values'][0])
            data = encodeData(QUANJV_XML.export())
            Save(selected_index, data.decode(), str(selected_item['values'][1]), e1.get(), e2.get(), '100027788')
            Messagebox.ok("保存成功！")
        except:
            try:
                data = encodeData(QUANJV_XML.export())
                Messagebox.show_error("保存失败\n存档已保存至当前目录下")
                with open("保存的存档数据.txt",'wb') as f:
                    f.write(data)
            except:
                Messagebox.okcancel('你都没修改你保存个蛋啊')



QUANJV_XML = None


def Login():
    get_list()


def change_theme():
    style = ttk.Style()
    style_list = style.theme_names()
    style.theme_use(choice(style_list))


root = ttk.Window(title='曦辞')
root.geometry('200x150')
change_theme()
Button_Login = ttk.Button(text="登录", command=Login)
Data_List = ttk.Treeview()
Button_Login.pack()
root.bind("<Key>", on_key_press)
e1 = ttk.Entry(root, show=None)
e1.insert('0', "username")
e2 = ttk.Entry(root, show=None)
e2.insert('1', "password")

e1.pack()
e2.pack()

tv = ttk.Treeview(
    master=root,
    columns=[0, 1],
    show=HEADINGS,

)

# 设置Treeview的列和标题
tv.heading(0, text='索引')
tv.heading(1, text='标题')
tv.column(0, width=60, anchor=CENTER)
tv.column(1, width=125, anchor=CENTER)

tv.pack_forget()


def get_list():
    try:
        data = Get_Savelist(Get_Cookie(e1.get(), e2.get()), Get_uid(e1.get()), "100027788")
        tv.pack()
        tv.delete(*tv.get_children())
        root.geometry('300x250')
        for item in eval(data):
            tv.insert('', END, values=(item["index"], item["title"]))
    except:
        Messagebox.show_error('请检查你的账号密码输入是否有错')


def treeviewClick(event):
    global BQTJ_XML
    selected_item = tv.item(tv.selection())
    selected_index = str(selected_item['values'][0])
    data = Get_SaveData(Get_uid(e1.get()), "100027788", selected_index, 'Yes')
    XML = BurstGunAssaultXml(decodeData(data).encode())
    Get_ThingsBag(XML, bqtj_pictures_dir)


import os
from PIL import Image, ImageTk


def Get_ThingsBag(BQTJ_XML, bqtj_pictures_dir):
    global QUANJV_XML
    yuanPath = BQTJ_XML.get_path('thingsBag', '/saveXml/s')
    arrpath = BQTJ_XML.get_path('arr', yuanPath)
    images = []

    for i in BQTJ_XML.get_path_data(arrpath):
        i = BurstGunAssaultObject(i, etree.ElementTree(BQTJ_XML.root).getpath(i))
        name = i.get_value('name').text
        cnName = i.get_value('cnName').text
        num = i.get_value('nowNum').text
        image_path = os.path.join(bqtj_pictures_dir, name + '.png')

        if os.path.exists(image_path):
            image = Image.open(image_path)
            resized_image = image.resize((50, 50), Image.ANTIALIAS)
            tk_image = ImageTk.PhotoImage(resized_image)
            images.append((tk_image, cnName, name, num, i))
        else:
            image = Image.open(bqtj_pictures_dir + '/Not.png')
            resized_image = image.resize((50, 50), Image.ANTIALIAS)
            tk_image = ImageTk.PhotoImage(resized_image)
            images.append((tk_image, cnName, name, num, i))

    # Create a new window to display all the images with pagination
    window = tk.Toplevel()
    window.title("物品背包")

    # Set up the frame for the images
    frame = tk.Frame(window)
    frame.pack()

    # Set up the variables for pagination
    images_per_row = 5
    images_per_page = 5 * 5  # 5 rows per page
    current_page = 0
    total_pages = (len(images) - 1) // images_per_page + 1
    page_label = tk.Label(window, text=f"第 {current_page + 1} 页 / 共 {total_pages} 页")
    page_label.pack()

    # Function to display the images on the current page
    def display_images():
        for widget in frame.winfo_children():
            widget.destroy()
        start_index = current_page * images_per_page
        end_index = min((current_page + 1) * images_per_page, len(images))
        page_label.config(text=f"第 {current_page + 1} 页 / 共 {total_pages} 页")
        for row in range(images_per_row):
            for col in range(images_per_row):
                index = start_index + row * images_per_row + col
                if index < end_index:
                    tk_image, cnName, name, num, obj = images[index]
                    label = tk.Label(frame, image=tk_image)
                    label.grid(row=row, column=col, padx=5, pady=5)
                    label.bind('<Button-1>', lambda event, obj=obj: show_item_details(obj))
                    ToolTip(label, cnName + '\n数量：' + num)

    def search_item():
        cn_name = Querybox.get_string('输入中文名(cnName)', '搜索', parent=window)
        for image in images:
            if image[1] == cn_name:
                show_item_details(image[4])
                break
        else:
            Messagebox.show_info("未找到与输入所匹配的对象", "搜索结果")

    # Create a new button for searching items
    search_button = tk.Button(window, text="搜索", command=search_item)
    search_button.pack(side=tk.LEFT)

    # Function to show item details in a new window
    def show_item_details(obj):
        item_window = tk.Toplevel()
        item_window.title("物品详情")

        name_label = tk.Label(item_window, text="名称:")
        name_label.pack()
        name_entry = tk.Entry(item_window)
        name_entry.insert(tk.END, obj.get_value('name').text)
        name_entry.pack()

        cn_name_label = tk.Label(item_window, text="中文名:")
        cn_name_label.pack()
        cn_name_entry = tk.Entry(item_window)
        cn_name_entry.insert(tk.END, obj.get_value('cnName').text)
        cn_name_entry.pack()

        num_label = tk.Label(item_window, text="数量:")
        num_label.pack()
        num_entry = tk.Entry(item_window)
        num_entry.insert(tk.END, obj.get_value('nowNum').text)
        num_entry.pack()

        def save_changes():
            global QUANJV_XML
            obj.revise({'name': name_entry.get()}, BQTJ_XML)
            obj.revise({'cnName': cn_name_entry.get()}, BQTJ_XML)
            obj.revise({'nowNum': num_entry.get()}, BQTJ_XML)
            window.destroy()
            item_window.destroy()
            QUANJV_XML = BQTJ_XML
            Get_ThingsBag(BQTJ_XML, bqtj_pictures_dir)

        save_button = tk.Button(item_window, text="保存", command=save_changes)
        save_button.pack()

    # Function to go to the previous page
    def previous_page():
        nonlocal current_page
        if current_page > 0:
            current_page -= 1
            display_images()

    # Function to go to the next page
    def next_page():
        nonlocal current_page
        if current_page < total_pages - 1:
            current_page += 1
            display_images()

    # Create the navigation buttons
    previous_button = tk.Button(window, text="上一页", command=previous_page)
    previous_button.pack(side=tk.LEFT)
    next_button = tk.Button(window, text="下一页", command=next_page)
    next_button.pack(side=tk.LEFT)

    # Display the images on the initial page
    display_images()

    window.mainloop()


tv.bind('<Double-1>', treeviewClick)

root.mainloop()
