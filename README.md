[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5b24d3105ea34ab1a4414c8f0c31e51d)](https://www.codacy.com/app/Kaiz0r/AppImages-Manager?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Kaiz0r/AppImages-Manager&amp;utm_campaign=Badge_Grade)

# AppImages-Manager
A little project i made for myself to sort my AppImages collection.
I made it really just for myself to be able to sort and categorize my AppImages in an automated method, but I thought i'd share it incase anyone else finds it useful.

Open the Config button in the app to choose where your Downloads folder is (where your browser will download appimages to), and the Storage path (Where this app stores the appimages).
Press Install button to move all apps from Downloads in to Storage.
Refresh reloads the list box with the files that are in Storage.
Run launches the selected app. If the app doesn't have permissions to execute, it'll handle that automatically.
Delete removes the selected appimage file from the system.
Group button allows you to sort the selected image in to categories or groups. Either enter a name in the box for a new group, or select a button for an existing group.
Edit button lets you edit the groups. (For now, just used for removing images from a group.

# Requires
Just tkinter. Everything else should be stock python3 libraries.
Only tested in python3.
