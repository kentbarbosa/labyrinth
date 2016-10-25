the aio branch puts everything into one flask app. this is the one used live at alchemy 2016

laby.py : controls the lights

labweb.py : flask app that provides the user interface

I decoupled all of these to maximize performance of the light controller but then found out that they run faster when put under one flask app. Simplicity works.
