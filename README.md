
runall : runs the 3 components

laby.py : controls the lights

cmdqmanager.py : handles the interprocess communication via Queue

labweb.py : flask app that provides the user interface

I decoupled all of these to maximize performance of the light controller.
