# Main Game

import math,random,pickle,pygame,sys
from tkinter import *
from operator import itemgetter
from superwires import games,color

pygame.init()

# Initialize PyGame Fonts
pygame.font.init()

"""
Get Display Information of Computer Screen.
Return a Dictionary
It will fetch width and height of the screen as well as other info such as
Hardware & Software Acceleration. Number of Bits & Bytes used to store Pixel etc.
"""
displayInfo = pygame.display.Info()

# Print the Width & Height of Current Computer Screen
print("Width:",displayInfo.current_w,"\nHeight:",displayInfo.current_h)

# Initialize the PyGame Window with current Screen Width & Height minus 1 inch space.
# 1 inch = 96 pixels
games.init(screen_width=displayInfo.current_w-96, screen_height=displayInfo.current_h-96,fps=50)

# Load the Icon of the Game
gameicon = pygame.image.load("Images/gameicon.png")

# Set the Title of Game Window in Title-Bar
pygame.display.set_caption("Astro - Destroyer")

# Set the Icon
pygame.display.set_icon(gameicon)

class Wrapper(games.Sprite):

    """ A Sprite that wraps around the screen """

    def update(self):
        """ Wrap sprties around scrren. """

        # If sprite's top leaves the bottom, it appears at the top
        if self.top > games.screen.height:
            self.bottom = 0

        # If sprite's bottom leaves the top, it appears at the bottom
        if self.bottom < 0:
            self.top = games.screen.height

        # If sprite's right leaves the left, it appears at the right of the screen
        if self.right < 0:
            self.left = games.screen.width

        # If sprite's left leaves the right, it appears at the left of the screen
        if self.left > games.screen.width:
            self.right = 0


    def die(self):
        """ Destroy itself """
        self.destroy()


class Collider(Wrapper):

    """ A Wrapper that can collide with another sprite/object. """

    def update(self):
        """ Check for Overlapping Sprites. """
        super(Collider, self).update()

        # Check if any Sprite(Object) is overlapping with each other
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.die() # Invoking die() method of that Object
            self.die() # Also invoking it's own die() method

        def die(self):
            """ Destroying itself and creates Explosion. """

            new_explosion =  Explosion(x = self.x, y = self.y)
            games.screen.add(new_explosion)
            self.destroy()

class Asteroid(Wrapper):

    """ An Asteroid which floats across the Screen. """

    # Constant Attributes to Select the size of Asteroids.
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    
    # Dictionary store the address of Images of all type of Asteroids
    # can be accessed by above Constants Attributes.
    IMAGES = {SMALL : games.load_image("Images/ast_small.png"),
              MEDIUM : games.load_image("Images/ast_med.png"),
              LARGE : games.load_image("Images/ast_big.png")}

    # Initial Speed of Asteroid. Velocity factor of Asteroid.
    SPEED = 2

    # Number of Asteroid creates when Big or Medium is Destroyed.
    SPAWN = 2

    # Starting Point/Score.
    POINTS = 30

    # Total number of Asteroids on the screen.
    total = 0

    def __init__(self, game, x, y, size):
        """ Initialize Asteroid Sprite. """

        # Increment the number of Asteroid on screen.
        Asteroid.total += 1

        # Invoke Super Class constructor to create the Asteroid Object.
        super(Asteroid,self).__init__(
            image = Asteroid.IMAGES[size],
            x = x, y = y,
            dx = random.choice([1,-1]) * Asteroid.SPEED * random.random()/size, 
            dy = random.choice([1,-1]) * Asteroid.SPEED * random.random()/size)

        # Store game object.
        self.game = game

        # Store current size of asteroid.
        self.size = size

    def die(self):
        """ Destroying Asteroid. """

        # When an Asteroid is destroyed
        Asteroid.total -= 1

        # Calculate and Add Scores. 10 Point for Big Asteroid, 15 Points for Medium and 30 Points for Small Asteroids.
        self.game.score.value += int(Asteroid.POINTS / self.size)

        # Re-Align the text that used to show the Score on the Screen.
        self.game.score.right = games.screen.width - 10

        # If Asteroid is Big or Medium, then replace it with 2 Medium or Smaller Asteroid
        if self.size != Asteroid.SMALL:
            for i in range(Asteroid.SPAWN):
                new_asteroid = Asteroid(game = self.game,
                                        x = self.x,
                                        y = self.y,
                                        size = self.size - 1)
                games.screen.add(new_asteroid)

        # If all Asteroid are gone, advance to Next Level
        if Asteroid.total == 0:
            self.game.advance()


        # Destroy the Current Asteroid and also creates an Explosion Animation.
        new_explosion = Explosion(x = self.x, y = self.y)
        games.screen.add(new_explosion)
        self.destroy()

class Ship(Collider):
    """ The Player's Ship. """

    # Load image of Ship
    IMAGE = games.load_image("Images/alienblaster(2).png")

    # Load Thrust Sound, which will played whenever ship moves forward.
    SOUND = games.load_sound("Sounds/thrust.wav")

    # Number of Steps the ship rotates.
    ROTATION_STEP = 3

    # Number of Frames per Second (FPS), the Ship wait to create the individual Missile object.
    MISSILE_DELAY = 25

    def __init__(self, game, x, bottom):
        """ Initialize the Ship Sprite. """

        # Invoke the Super Class Constructor to create the Ship Object at Particular Location of the Screen.
        super(Ship,self).__init__(image = Ship.IMAGE,
                                  x = x,
                                  bottom = bottom)

        # Store the Game Object
        self.game = game

        # Initialize the property MISSILE_WAIT, upto which ship has to wait to create the Missile Object.
        self.missile_wait = 0

    def update(self):
        """ Rotate, Move and Fire the Missile based on the key pressed. """

        super(Ship, self).update()

        ## Rotate the Ship

        # 1. Rotate using the Left and Right Keys.
        if games.keyboard.is_pressed(games.K_LEFT):
            self.angle -= Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.angle += Ship.ROTATION_STEP

        # 2. Applying Thrust based on "W" Keys
        if games.keyboard.is_pressed(games.K_w):
            Ship.SOUND.play()

            """ Change Velocity Components based on Ship's Angle """

            # Converts to current angle of Ship into Radian Value.
            angle = self.angle * math.pi / 180

            # Calculate, whether the Ship move on X-Axis ( Horizontal ) on the Screen.
            self.x+=1*math.sin(angle)

            # Calculate, whether the Ship move on Y-Axis ( Vertical ) on the Screen.
            self.y+=1*-math.cos(angle)

        # 3. Reduce the Thrust based on "S" Keys
        if games.keyboard.is_pressed(games.K_s):
            # Converts to ship's angle into Radian.
            angle = self.angle * math.pi / 180

            # Calculate, whether the Ship move on X-Axis ( Horizontal ) on the Screen.
            self.x-=1*math.sin(angle)

            # Calculate, whether the Ship move on Y-Axis ( Vertical ) on the Screen.
            self.y-=1*-math.cos(angle)
          
        # 4. Rotate Ship using "1","2","3","4" Keys
        if games.keyboard.is_pressed(games.K_1):
            self.angle = 0          # Rotate to 0 and 360 degrees
        if games.keyboard.is_pressed(games.K_2):
            self.angle = 90         # Rotate to 90 degrees
        if games.keyboard.is_pressed(games.K_3):
            self.angle = 180        # Rotate to 180 degrees
        if games.keyboard.is_pressed(games.K_4):
            self.angle = 270        # Rotate to 270 degrees

        # 5. If Waiting until the Ship fires Missiles, decrease Wait
        if self.missile_wait > 0:
            self.missile_wait -= 1

        # 6. Fire Missiles if SPACEBAR is pressed and missile wait is over
        if games.keyboard.is_pressed(games.K_SPACE) and self.missile_wait == 0:

            # Create the Missile
            new_missile = Missile(self.x, self.y, self.angle)
            games.screen.add(new_missile)

            # Stop firing missile till 25FPS
            self.missile_wait = Ship.MISSILE_DELAY

        # 7. Move the Ship left and right using "A" and "D" Keys

        """ Convert ship's current angle into Radian. Move the Ship Left and Right according to Ship's Angle """
        if games.keyboard.is_pressed(games.K_a):
            angle = self.angle * math.pi / 180
            self.x -= math.cos(angle)*1
            self.y -= math.sin(angle)*1

        if games.keyboard.is_pressed(games.K_d):
            angle = self.angle * math.pi / 180
            self.x += math.cos(angle)*1
            self.y += math.sin(angle)*1

        # 8. Exit the Game when user Presses "ESCAPE" key
        if games.keyboard.is_pressed(games.K_ESCAPE):

            # Quit the PyGame Window.
            pygame.display.quit()

            # Quit the PyGame Object.
            pygame.quit()

            # Exit the Program.
            sys.quit()

    def die(self):
        """ Destroy the Ship and End the Game. """
        the_explosion = Explosion(self.x,self.y)
        games.screen.add(the_explosion)
        self.game.end()


class Missile(Collider):
    """ A Missile launched by the player's ship. """
    IMAGE = games.load_image("Images/newMissile.png")
    SOUND = games.load_sound("Sounds/missile.wav")

    # Initialize the Pixel Area as BUFFER around Ship. The Missile is created outside this area, so that the Ship is not destroyed by the Missile.
    BUFFER = 60

    # Number of Pixel the Missile move in 1 second.
    VELOCITY_FACTOR = 7

    def __init__(self, ship_x, ship_y, ship_angle):
        """ Initialize Missiles Sprite """

        # Play the Sound whenever the Missile is Created.
        Missile.SOUND.play()

        # Converts to Ship's angle into Radians.
        angle = ship_angle * math.pi / 180

        # Calculate the Direction in which the Missile will move, based on the Angle of Ship Object.
        """ Move on straight X-Axis, if angle is 90 and 270 """
        buffer_x = Missile.BUFFER * math.sin(angle)  

        """ Move on straight Y-Axis, if angle is 0/360 and 180 """
        buffer_y = Missile.BUFFER * -math.cos(angle)

        # Calculate the position of pixel on X-Axis of the Screen on which new Missile is created.
        x = ship_x + buffer_x

        # Calculate the position of pixel on Y-Axis of the Screen on which new Missile is created.
        y = ship_y + buffer_y

        """ Calculate Missile's Velocity Components. """
        # Moving the Missile on X and Y-Axis based on Ship's Angle.
        dx = Missile.VELOCITY_FACTOR * math.sin(angle)
        dy = Missile.VELOCITY_FACTOR * -math.cos(angle)

        # Creating the Missiles
        super(Missile,self).__init__(image = Missile.IMAGE,
                                     x = x, y = y,
                                     dx = dx, dy = dy)


    def update(self):
        """ Move the Missile """
        super(Missile, self).update()

        # Check if Missile reached at Screen Boundaries. If yes, then destroy the Missiles.
        if self.x < 0 or self.x > games.screen.width or self.y < 0 or self.y > games.screen.height:
            self.destroy()

class Explosion(games.Animation):

    """ Explosion Animation """

    # Load the Sound of Explosion.
    SOUND = games.load_sound("Sounds/explosion.wav")

    # Create the List of Images, that together become the Animation.
    IMAGES = ["Images/explosion1.bmp",
              "Images/explosion2.bmp",
              "Images/explosion3.bmp",
              "Images/explosion4.bmp",
              "Images/explosion5.bmp",
              "Images/explosion6.bmp",
              "Images/explosion7.bmp",
              "Images/explosion8.bmp",
              "Images/explosion9.bmp"]

    def __init__(self, x, y):

        """
        Invoke the Super Class Constructor to create Explosion Object.
        The Object will be created at X & Y coordinate of the Object which destroys.
        Every Image will be repeated after 4 FPS.
        & the animation is repeated only 1 time. If 'n_repeats' = 0, the Animation will be in loop until the PyGame exits.
        The Object will be non-collideable, as it doesnot collide with any object on the screen.
        """
        super(Explosion, self).__init__(images = Explosion.IMAGES,
                                        x = x, y = y,
                                        repeat_interval = 4,
                                        n_repeats = 1,
                                        is_collideable = False)
        # Play the Explosion Sound.
        Explosion.SOUND.play()

class Game:
    """ The Game Itself """

    # Initialize the Player Name, Total Score of the Game.
    playerName = None
    totalScore = None

    def __init__(self):
            
        # Set Initial Level
        self.level = 0

        # Load Sound for Level Advance
        self.sound = games.load_sound("Sounds/level.wav")

        # Create Scores Text of color White and on the right side of the Screen.
        # Also, it is non-collideable.
        self.score = games.Text(value = 0,
                                size = 30,
                                color = color.white,
                                top = 5,
                                right = games.screen.width - 10,
                                is_collideable = False)

        games.screen.add(self.score)

        # Create Ship Object on the Screen at particular X & Y coordinate.
        self.ship = Ship(game = self,
                         x = games.screen.width/2,
                         bottom = games.screen.height - 10)

        games.screen.add(self.ship)

    def play(self):
        """ Play the Game """

        # Begin the Theme Music and play it forever until PyGame exits.
        games.music.load("Sounds/theme.wav")
        games.music.play(-1)

        # Loads the Background
        background = games.load_image("Images/Red-Galaxy-4k.jpg")

        # Scale the Background image according to the Screen Resolution of Computer System.
        background = pygame.transform.scale(background,(games.screen.width,games.screen.height))

        # Set the Background Image.
        games.screen.background = background

        # Invoke the Advance() method to Level Up the Game.
        self.advance()

        # Starts the Gameplay.
        games.screen.mainloop()

    def advance(self):
        """ Advanced to Next Level Game """

        # Increment the Level of Game by 1.
        self.level += 1

        # Amount of space Around the Ship to preserve when creating Asteroids, so that the ship is not destroyed when Asteroids is created.
        BUFFER = 150

        # Create number of new Asteroids according to Level of the Game.
        for i in range(self.level):

            """ Creates the Buffer Space around the Ship on the X & Y axis """

            # Choose Minimum distance on X-Axis and Y-Axis
            x_min = random.randrange(BUFFER)
            y_min = BUFFER - x_min

            # Choose Distance along X-Axis & Y-Axis based on Minimum Distance, so that asteroid is created not so far from Ship.
            x_dist = random.randrange(x_min, games.screen.width - x_min)
            y_dist = random.randrange(y_min, games.screen.height - y_min)

            # Calculate the Location of new Asteroid that will be created based on Distance calculated.
            x = self.ship.x + x_dist
            y = self.ship.y + y_dist

            # Wrap Around Screen, if necessary i.e If asteroid is created out of Screen Boundaries, then it will created on opposite side of the Screen.
            x %= games.screen.width
            y %= games.screen.height

            # Create Big Asteroids
            new_asteroid = Asteroid(game = self,
                                    x = x, y = y,
                                    size = Asteroid.LARGE)
            games.screen.add(new_asteroid)

        # Display Level Number, when Incremented for 3 Seconds at Center of the Screen.
        self.level_message = games.Message(value = "Level " + str(self.level),
                                      size = 40,
                                      color = color.yellow,
                                      x = games.screen.width/2,
                                      y = games.screen.height/2,
                                      lifetime = games.screen.fps * 3,
                                      is_collideable = False)
        games.screen.add(self.level_message)

        # Play New Level Sound (except for Level 1)
        if self.level > 1:
            self.sound.play()

    def endTheGame(self):
        """ To End the GamePlay and start other Processes """
        
        games.screen.quit()

        # Invoke the GUI interface to get Player's Name.
        self.getPlayerName()

    def getPlayerName(self):
        """ Get Player's Name """

        # Create the Tkinter Window.
        self.root = Tk()
        
        # Set the Size or Geometry of Tkinter Window.
        self.root.geometry("170x100")
        
        # Set the title of Window.
        self.root.title("Player Name")

        # Set Window non-resizable.
        self.root.resizable(False,False)

        # Create Frame within the Window.
        app = Frame(self.root)
        
        # Apply Grid Layout Manager
        app.grid()

        """ Creating Various Component/Widgets on Screen. """
        # Create and Place Label on Frame.
        Label(app,text="Enter your Name : ").grid(row=0,column=0,columnspan=2,sticky=N,padx=3,pady=5)

        # Create and Place the Entry Field on Window. Text within the field is aligned to Center.
        self.nameEntry = Entry(app,justify="center")
        self.nameEntry.grid(row=1,column=0,columnspan=2,padx=2,pady=3,sticky=N)
            
        # Set Focus on the Entry Widgets.
        self.nameEntry.focus_set()

        # Create the Submit Button.
        submitBtn = Button(app,text="Submit",command=self.setPlayerName)
        submitBtn.grid(row=2,column=0,sticky=SW,pady=2,padx=5)

        # Create the Exit Button.
        exitBtn = Button(app,text=" Exit ",command=self.exitTheGame)
        exitBtn.grid(row=2,column=1,sticky=S,pady=2)

        # Adjust all widget within the Window.
        app.pack()

        # Start the Loop until Player clicks the Button
        self.root.mainloop()


    def setPlayerName(self):
        """ Set the Player's name in 'playerName' field """

        # Get the Name from the Entry widget.
        Game.playerName = str(self.nameEntry.get())

        # Check whether the user enter the name or not.
        if len(Game.playerName) == 0:
            # If user doesnot enter any name, the playerName field will be set to "UNKNOWN PLAYER"
            Game.playerName = "Unknown Player"

        # Get the Total Score
        Game.totalScore = int(self.score.value)

        # Write the Score in the file.
        self.writeHighScore()

    def writeHighScore(self):
        """ Save the HighScores by using Pickling Method, i.e. Save in the way only Program understands. """

        # Creates and Initialize the file pointer.
        fp = None

        # Empty List to store the Highscore from the File.
        highscore = []

        """ Open the file and get the Highscore.
            1.If the file is not created, then it will be created.
            2.Unknown type of data will be Correctly fetched.
            3.If file doesnot contain any data, it will create temporary file.
        """
        try:
            fp = open("Scores/highscores.dat","rb") #open the file
            highscore = pickle.load(fp) #load the date from file.
            highscore.append((Game.playerName,Game.totalScore)) #append new data to the list
            highscore = sorted(highscore,key=itemgetter(1),reverse=True) #sorted the data according to Highscore in descending order.
            fp.close() #close the file.
        except TypeError:
            fp = open("Scores/highscores.dat","rb")
            highscore = pickle.load(fp)
            highscore.append((Game.playerName,Game.totalScore))
            highscore = sorted(highscore,key=itemgetter(1),reverse=True)
            fp.close()
        except FileNotFoundError:
            fp = open("Scores/highscores.dat","wb")
            fp.close()
        except EOFError:
            # If the file is empty,then it will dump some value into it.
            fp = open("Scores/highscores.dat","wb")
            high = [("Mohit",90000),("Monika",1000000)]
            pickle.dump(high,fp)
            fp.close()

            # Again open file in read mode, perform same operation as in Try Block.
            fp = open("Scores/highscores.dat","rb")
            highscore = pickle.load(fp)
            highscore.append((Game.playerName,Game.totalScore))
            highscore = sorted(highscore,key=itemgetter(1),reverse=True)
            fp.close()

        # Write the Data into file again.
        fp = open("Scores/highscores.dat","wb")
        pickle.dump(highscore,fp)
        fp.close()


        # Display the Scores.
        self.getHighScore()

    def getHighScore(self):
        """ Get the HighScore List """

        # Create Root Window using Tkinter
        high_score_screen = Tk()

        # Set Title of Window.
        high_score_screen.title("High Score List")

        # Set Geometry of Window.
        high_score_screen.geometry("400x450")

        # Making Window Non-Resizable
        high_score_screen.resizable(False,False)

        # Create Frame within Root Window
        frame = Frame(high_score_screen)

        # Apply Grid Layout Manager on Frame.
        frame.grid()

        print("I am in High Score") # For System Purposes.

        # Open the File
        fp = open("Scores/highscores.dat","rb")

        # Load data from file into List.
        highscore = pickle.load(fp)

        # Close the File.
        fp.close()

        # Create Widgets to display the Player's Name along with their HighScores.
        Label(frame,text="       ").grid(row=0,column=0)
        text_box1 = Text(frame,height=30,width=20,borderwidth=0,background='#d9d9d9')
        text_box2 = Text(frame,height=30,width=20,borderwidth=0,background='#d9d9d9')
        text_box1.grid(row=1,column=1)
        text_box2.grid(row=1,column=3)
        text_box1.delete(0.0,END)
        text_box2.delete(0.0,END)
        i=0

        # Fill Data in Text Boxes.
        for player in highscore:

            # Store the each player information into variables 'name' and 'score'
            name,score = player

            print(name,"\t",score)
            name = str(name)+"\n"
            score=str(score)+"\n"

            # Insert data into Text Boxes.
            text_box1.insert(END,name)
            text_box2.insert(END,score)
            i+=1
            if i==10:
                # Only Top - 10 scores will be displayed.
                break
                

        # Give title to each Text Box.
        text_box1.insert(0.0,"PLAYER NAME\n\n")
        text_box2.insert(0.0,"SCORE\n\n")

        # Making Text Boxes un-editable.
        text_box1["state"]=DISABLED
        text_box2["state"]=DISABLED
        
        # Adjust widgets in frame.
        frame.pack()

        # Destroy the Player Name GUI interface.
        self.root.destroy()

        # Quit the screen.
        games.screen.quit()

        # High Score Root Window within the Loop until user close it.
        high_score_screen.mainloop()

        # Quit PyGame Display
        pygame.display.quit()

        # Quit PyGame
        pygame.quit()
    

    def end(self):
        """ End the Game. """
        
        # Show "Game Over" for 5 seconds
        print("Ending the Game")
        end_message = games.Message(value = "Game Over",
                                    size = 90,
                                    color = color.white,
                                    x = games.screen.width/2,
                                    y = games.screen.height/2,
                                    lifetime = games.screen.fps * 5,
                                    after_death = self.endTheGame,
                                    is_collideable = False)

        games.screen.add(end_message)

    def exitTheGame(self):
        """ If player chooses to exits in getPlayerName window. """

        # All windows will be closed and Music will be stopped
        pygame.display.quit()
        games.screen.quit()
        games.music.stop()
        self.root.destroy()
        pygame.quit()

def main():
    """ Creates the Game Object and starts the Gameplay. """
    
    astro_destroyer = Game()
    astro_destroyer.play()

def intro():
    """ Create the Introduction or Starting PyGame Window. """

    # Load the Background Image.
    background = games.load_image("Images/Game_Front.jpg")

    # Scale the Image according to current resolution of Player's Computer System
    background = pygame.transform.scale(background,(games.screen.width,games.screen.height))

    # Set the Background Image.
    games.screen.background = background

    # Initialize the intro variable.
    intro = True

    # Loop the Screen until Player presses ESC or START key.
    while intro == True:
        for event in pygame.event.get():
            if games.keyboard.is_pressed(games.K_ESCAPE):
                # If User presses ESC then pygame quits and the program will be closed.
                pygame.quit()
                sys.exit()
            elif games.keyboard.is_pressed(games.K_SPACE):
                # If user pressed START key, then the gameplay will be started.
                intro=False

    games.screen.clear()

# lets play
# start the intro screen then gameplay

#intro()
main()
