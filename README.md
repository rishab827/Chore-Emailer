# Chore Emailer Project

This project was created as a tool to continiously send emails (specifically chore instructions) on a rotating basis 

It is implemented as primarily a Python script (chorescript.py) that uses Google Mail servers to send emails from an account, as well as several other functions that allow the emails to send repeatedly in specific time frames (implemented to send weekly, currently)
Then, this is integrated with a Flask front-end (hello.py), that transforms the script to work with flask variables to create an customizable interface.
