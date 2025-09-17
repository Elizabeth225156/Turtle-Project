#Elizabeth ELden. 9/15/2025. Turtle Project
import turtle
import random

t = turtle.Turtle()
screen = turtle.Screen()
screen.setup(width=850, height=650)
#Set up the initial turtle
t.color('white')
t.hideturtle()
t.speed(0)

#Function to draw stars
def drawStar(xCord, yCord):
    t.teleport(xCord, yCord)
    t.dot(3, 'white')

#background as space
turtle.bgcolor('black')
#Array of randomly generated values for stars
xCordStar = []
yCordStar = []
numOfStars = 100
for i in range (numOfStars):
    xCordStar.append(random.randint(-425, 425))
    yCordStar.append(random.randint(-325, 325))
#Draw stars w/ function
for i in range (numOfStars):
    drawStar(xCordStar[i], yCordStar[i])

#Planet outline
t.penup()
t.goto(0, -300)
t.pendown()
t.circle(300)

#Thingy for drawing the planet
#Draw outlines of continents
    #Find two points on the outline
    #Randomly generate a squiggly line between them
#Color in continents
#Color in ocean. (trace oceans first?)

turtle.done()

