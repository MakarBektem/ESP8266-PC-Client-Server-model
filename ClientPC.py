import socket   # библиотека для работы с сокетами
from tkinter import *  # библиотека для организации оконного интерфейса
from tkinter import ttk
import json # библиотека для работы с JSON-пакетами

ip = '192.168.0.4'  # IP адрес платы в локальной сети роутера
port = 10000  # выбранный для общения порт

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создание сокета
conn.connect((ip, port))  # соединение с сокетом с заданным адресом и портом

tk = Tk()  # создаем объект окно

# определение переменных, хранящих значения с сенсоров макета
p = DoubleVar()
aX = DoubleVar()
aY = DoubleVar()
aZ = DoubleVar()
gest = StringVar()

# массив возможных цветов светодиодов на ленте
ledStripColors = ["красный", "синий", "зеленый"]

# список значений для ленты светодиодов, передаваемый в JSON-пакет
LScolors = [1, 2, 3, 1, 2, 3, 1, 2]

# определение переменных, хранящих состояния дискретных светодиодов
statLed1 = IntVar()
statLed2 = IntVar()
statLed3 = IntVar()

tk.title('UI')  # заголовок окна
tk.geometry('700x300')  # размеры окна

# создание виджетов типа Entry для вывода показаний датчиков
valP = ttk.Entry(textvariable=p)
valAx = ttk.Entry(textvariable=aX)
valAy = ttk.Entry(textvariable=aY)
valAz = ttk.Entry(textvariable=aZ)
valGest = ttk.Entry(textvariable=gest)

# создание виджетов типа Label для текстовых меток
labelRecieved = ttk.Label(text="Принимаемые данные")
labelP = ttk.Label(text="Давление, гПа")
labelAx = ttk.Label(text="Ускорение Х, м/с^2")
labelAy = ttk.Label(text="Ускорение Y, м/с^2")
labelAz = ttk.Label(text="Ускорение Z, м/с^2")
labelG= ttk.Label(text="Жест")
labelSend = ttk.Label(text="Отправляемые данные")
labelLed1 = ttk.Label(text="Светодиод №1")
labelLed2 = ttk.Label(text="Светодиод №2")
labelLed3 = ttk.Label(text="Светодиод №3")
labelLedS = ttk.Label(text="Выберите цвета для светодиодной ленты")

# создание виджетов типа Checkbutton для управления светодиодами
btnL1 = ttk.Checkbutton(text="вкл/выкл", variable=statLed1)
btnL2 = ttk.Checkbutton(text="вкл/выкл", variable=statLed2)
btnL3 = ttk.Checkbutton(text="вкл/выкл", variable=statLed3)

# создание виджетов типа Combobox для управления светодиодной лентой
comboLS1 = ttk.Combobox(values=ledStripColors, width=8, state="readonly")
comboLS2= ttk.Combobox(values=ledStripColors, width=8, state="readonly")
comboLS3 = ttk.Combobox(values=ledStripColors, width=8, state="readonly")
comboLS4 = ttk.Combobox(values=ledStripColors, width=8, state="readonly")
comboLS5 = ttk.Combobox(values=ledStripColors, width=8, state="readonly")
comboLS6 = ttk.Combobox(values=ledStripColors, width=8, state="readonly")
comboLS7 = ttk.Combobox(values=ledStripColors, width=8, state="readonly")
comboLS8 = ttk.Combobox(values=ledStripColors, width=8, state="readonly")

# размещение виджетов в окне
labelRecieved.place(x=50, y=10)
labelP.place(x=10, y=50)
labelP.place(x=10, y=50)
labelAx.place(x=10, y=100)
labelAy.place(x=10, y=150)
labelAz.place(x=10, y=200)
labelG.place(x=10, y=250)
valP.place(x=130, y=50)
valAx.place(x=130, y=100)
valAy.place(x=130, y=150)
valAz.place(x=130, y=200)
valGest.place(x=130, y=250)
labelSend.place(x=320, y=10)
labelLed1.place(x=300, y=50)
labelLed2.place(x=300, y=100)
labelLed3.place(x=300, y=150)
labelLedS.place(x=350, y=180)
btnL1.place(x=400, y=50)
btnL2.place(x=400, y=100)
btnL3.place(x=400, y=150)
comboLS1.place(x=300, y=210)
comboLS2.place(x=400, y=210)
comboLS3.place(x=500, y=210)
comboLS4.place(x=600, y=210)
comboLS5.place(x=300, y=250)
comboLS6.place(x=400, y=250)
comboLS7.place(x=500, y=250)
comboLS8.place(x=600, y=250)

# функция loop, обрабатывающая входящие JSON-пакеты
def loop():
    conn.setblocking(False) # неблокирующий режим работы
    try:
        data = conn.recv(80)   # принятие и запись сообщения с сокета
        y = json.loads(data)    # десериализация JSON-пакета
        # парсинг (извлечение показаний с сенсоров) и вывод в виджеты
        p.set(y["Pressure"])
        aX.set(y["Acceleration"][0])
        aY.set(y["Acceleration"][1])
        aZ.set(y["Acceleration"][2])
        gest.set(y["Gesture"])
    except:
        tk.after(1, loop)   # отложенный вызов функции loop
        return
    tk.after(1, loop)  # отложенный вызов функции loop
    return
# функция отправки JSON-пакета
def send():
    mydict = {"LED1": statLed1.get(), "LED2": statLed2.get(), "LED3": statLed3.get(), "LEDSTRIP": LScolors}  # создаем словарь
    datas = json.dumps(mydict)  # сериализуем словарь в JSON-структуру
    conn.sendall(bytes(datas, encoding="ascii")) # отправка JSON-пакета на сервер

# виджет типа Button для отправки данных на сервер
btn = ttk.Button(text="Поменять состояние светодиодов", command=send)
btn.place(x=490, y=100)

# функция сопоставления цвета его номеру
def createColor(getColor):
    if getColor == "красный":
        returnColor = 1
    elif getColor == "синий":
        returnColor = 2
    elif getColor == "зеленый":
        returnColor = 3

# функции создания массива цветов для ленты
def selectLS1(event):
    LScolors[0] = createColor(comboLS1.get())
def selectLS2(event):
    LScolors[1] = createColor(comboLS2.get())
def selectLS3(event):
    LScolors[2] = createColor(comboLS3.get())
def selectLS4(event):
    LScolors[3] = createColor(comboLS4.get())
def selectLS5(event):
    LScolors[4] = createColor(comboLS5.get())
def selectLS6(event):
    LScolors[5] = createColor(comboLS6.get())
def selectLS7(event):
    LScolors[6] = createColor(comboLS7.get())
def selectLS8(event):
    LScolors[7] = createColor(comboLS8.get())

# команды обработки изменений выбранных цветов для ленты светодиодов
comboLS1.bind("<<ComboboxSelected>>", selectLS1)
comboLS2.bind("<<ComboboxSelected>>", selectLS2)
comboLS3.bind("<<ComboboxSelected>>", selectLS3)
comboLS4.bind("<<ComboboxSelected>>", selectLS4)
comboLS5.bind("<<ComboboxSelected>>", selectLS5)
comboLS6.bind("<<ComboboxSelected>>", selectLS6)
comboLS7.bind("<<ComboboxSelected>>", selectLS7)
comboLS8.bind("<<ComboboxSelected>>", selectLS8)

tk.after(1, loop)  # отложенный вызов функции loop
tk.mainloop()  # запуск цикла обработки событий окна
