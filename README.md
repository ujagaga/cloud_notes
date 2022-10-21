# Cloud Notes

Simple note-taking app easy to back up via cloud.
The app itself is just a lightweight Python desktop app with a configurable folder to be used for notes. It is this 
folder that you can back up to save your notes. All the notes are just text files which the application reads and 
displays in a simple resizable window.

## The Why ##

Some note taking apps for linux I have tried, do not do well with backing up to a cloud, start too slow, are not 
minimalistic enough or will not copy/paste just the text without any formatting. 
So I wrote my own that I can tune to my wishes. Feel free to use it and adjust as you wish.

## How to start

You will need Python3 with TkInter installed. Just run the script. The required Python libraries will be installed 
automatically. The default notes folder is `$HOME/.cloud_notes/notes` but it can be changed by clicking on the browse 
button it the notes list window. 
