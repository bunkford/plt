# plt
basic hpgl plt editor written in python & tkinter

The generated .plt files work on the engraver I have available, probably not standard hpgl code. That being said, it does open random plt files I found on the internet. 

![Image of Yaktocat](https://github.com/bunkford/plt/raw/master/screenshot.PNG)

## controls

| key      | description
| -------- | ---------------------------------------------------------------------------|
| H        | Pan around the screen with the mouse, (click & drag)
| HOME     | Return to home (0,0) position.
| C        | Draw Circle. Mouse to position. Mouse wheel to adjust size. ENTER to finish.
| L        | Draw Line. Click for first point, then click again for end point. ESC to finish.
| S        | Scale drawing using mouse wheel.
| M        | Move selected
| ESC      | Clear commands, go back to select mode.
| T        | Text Mode. Align with mouse, and start typing. Enter to finish.
| DEL      | When lines are selected, deletes them
| Ctrl     | When this is pressed, lines don't snap to eachother

## Fonts

True Type fonts can be used, it parses the fonts folder to find them. Some work, some don't, depending on how complex they are. 

## Visualize plot

You can use this menu option to visualize the path the plotter is going to take. You can hit ESC to cancel the simulation.

## Pens

I implemented basic support for changing pens. The engraver I tested on doesn't support this option, but it should work. You select the lines you want to be a different pen, and then use the menu to change them. Everything is drawn in pen 1 by default. 
