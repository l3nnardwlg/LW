import turtle

turtle.setup(700, 700)
turtle.bgcolor("lightblue")
turtle.title("h = Haus | s = Schneemann | b = Baum")

stift = turtle.Turtle()
stift.hideturtle()
stift.speed(0)

spawn_x, spawn_y = 0, -200

def gehe_zu(x, y):
    stift.penup()
    stift.goto(x, y)
    stift.pendown()

def zeichne_dreieck(x1, y1, x2, y2, x3, y3, fill_color):
    stift.color("black", fill_color)
    gehe_zu(x1, y1)
    stift.begin_fill()
    stift.goto(x2, y2)
    stift.goto(x3, y3)
    stift.goto(x1, y1)
    stift.end_fill()


def zeichne_haus(x, y, size=120):
    stift.setheading(0)
    stift.color("black", "orange")
    gehe_zu(x, y)
    stift.begin_fill()
    for _ in range(4):
        stift.forward(size)
        stift.left(90)
    stift.end_fill()

    stift.color("black", "red")
    gehe_zu(x, y + size)
    stift.begin_fill()
    stift.goto(x + size, y + size)
    stift.goto(x + size / 2, y + size + size * 0.6)
    stift.goto(x, y + size)
    stift.end_fill()


def zeichne_kreis_mitte(x, y, r, fill):
    stift.setheading(0)
    stift.color("black", fill)
    stift.penup()
    stift.goto(x, y - r)
    stift.pendown()
    stift.begin_fill()
    stift.circle(r)
    stift.end_fill()


def zeichne_schneemann(x, y):
    zeichne_kreis_mitte(x, y, 35, "white")
    zeichne_kreis_mitte(x, y + 55, 25, "white")
    zeichne_kreis_mitte(x, y + 95, 18, "white")


def zeichne_baum(x, y):
    stift.setheading(0)

    
    stift.color("black", "sienna")
    gehe_zu(x - 15, y)
    stift.begin_fill()
    stift.goto(x + 15, y)
    stift.goto(x + 15, y + 45)
    stift.goto(x - 15, y + 45)
    stift.goto(x - 15, y)
    stift.end_fill()

   
    zeichne_dreieck(x - 70, y + 45,  x + 70, y + 45,  x, y + 155, "green")
    zeichne_dreieck(x - 55, y + 95,  x + 55, y + 95,  x, y + 200, "green")


def set_spawn(x, y):
    global spawn_x, spawn_y
    spawn_x, spawn_y = x, y

def key_haus():
    zeichne_haus(spawn_x, spawn_y)

def key_schnee():
    zeichne_schneemann(spawn_x, spawn_y)

def key_baum():
    zeichne_baum(spawn_x, spawn_y)

turtle.listen()
turtle.onscreenclick(set_spawn)
turtle.onkey(key_haus, "h")
turtle.onkey(key_schnee, "s")
turtle.onkey(key_baum, "b")

turtle.done()
