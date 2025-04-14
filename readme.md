How to run:
    Set current directory to folder (cd [path to folder])
    Create virtual environment
        windows: 
            python -m -venv venv
            venv\Scripts\activate
        mac:
            python3 -m venv venv
            source venv/bin/activate (might need to be {activate.bat})
    Run app:
        python(3) app.py

How to send to Github:
    git status: see staged files

    git add --all: add all unstaged files to stage

    git commit -m "message": commit changes to master branch with a message

    git push origin main: push commited changes from origin (myself) to main branch (on Github)

Current thing being worked on: 
    Styling and UX improvements

ToDo:
    Allow other users to connect that aren't myself

    Only display auto-fill sections when choosing website source type
    Add more source types

