## Actor Instance Property Retriever (AIPR)

The **Actor Instance Property Retriever (AIPR)** is a tool designed to be used on Unreal Engine 5 to gather all the levels where an actor is being used, consult any property and store the results in a .csv file. The AIPR is comprised by two files, a Widget, and a Pyhton script. 

### How does it work?

Once the user has selected an actor in the widget and an optional property to query, the tool will gather all the levels where the selected actor is in use, will open them automatically and individually and will store the results in a .csv file. 

## How to use

1. Place *WBP_ActorInstancePropertyRetriever* anywhere under the content folder in your UE5 project. 
2. Place *ActorInstancePropertyRetriever.py*  in the root folder of your project.
3. Once your project has been loaded, Run the Editor Utily Widget (*WBP_ActorInstancePropertyRetriever*). To do so, right click on the asset and select the first option _Run Editor Utility Widget_
4. A Widget will appear. On it, select using the Drop Down which actor are you looking for. Optionally add a property name to gather its value.
5. Press Run Utility

If everything went as expected, a prompt will show the name of the save file and will ask you if you want to open the resulting file path.

## Images

### Widget 

![Widget](https://github.com/davz91/UEPython/blob/main/ActorInstancePropertyRetriever/Images/AIPR_Widget.png)

### Success Window

![Success](https://github.com/davz91/UEPython/blob/main/ActorInstancePropertyRetriever/Images/AIPR_Success.png)

### Demo results

![DemoResults](https://github.com/davz91/UEPython/blob/main/ActorInstancePropertyRetriever/Images/AIPR_DemoResults.png)