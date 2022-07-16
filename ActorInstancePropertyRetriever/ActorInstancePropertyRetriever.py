# Script saving on a csv file how many instances of a given actor class is present within a level.
# Optionally, look for a given property in the actor and return the value.
# Compatible ONLY with UE5. 

# Python 3 is required to run this script

# https://twitter.com/_davz_
# 2022
# v. 1.0

import unreal
import sys
import os
import csv
from datetime import datetime

EditorUtil = unreal.EditorAssetLibrary()
PathUtil = unreal.Paths()
AssetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
GameplayStatics = unreal.GameplayStatics()
StringLibrary = unreal.StringLibrary()
LevelSubsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EditorSubsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
TextLibrary = unreal.TextLibrary()
EditorDialog = unreal.EditorDialog()
SystemLibrary = unreal.SystemLibrary() 
DependencyOptions = unreal.AssetRegistryDependencyOptions(True, True, False, False, False)

def IsVersionCompatible():
    EngineVersion = SystemLibrary.get_engine_version()
    if EngineVersion.startswith("5"):
        return True
    else:
        return False
    
def GetAssetData(Asset):
    AssetData = EditorUtil.find_asset_data(Asset)
   
    return AssetData

def GetAssetPath(AssetToLoad):
    AssetData = GetAssetData(AssetToLoad)
    AssetPath = AssetData.package_name
    
    return AssetPath

def GetAssetReferences(Path):
    References = AssetRegistry.get_referencers(Path, DependencyOptions)
    
    return References

def FilterReferences(References):
    ReferencedLevels = []
    if len(References) != 0:
        for reference in References:        
            ReferenceAssetClass = GetAssetData(reference)
            if ReferenceAssetClass.asset_class == "World":
                ReferencedLevels.append(reference)
    else:
        unreal.log("There's no references to this actor in any level. Process stopped.")
                    
    return ReferencedLevels

def StoreReferences(Levels, Asset):
    LevelActors = dict()
    bNeedProperty = False
    TotalLevels = len(Levels)
    CurrentLevel = 0
    bIgnorePopups = False
    BlueprintClass = EditorUtil.load_blueprint_class(Asset) # We're sure it's a blueprint class as we have filtered that in the UE widget before, so this should be always a correct load.
    
    if ASSET_PROPERTY != None:
        bNeedProperty = True
        PropertyName = StringLibrary.conv_string_to_name(str(ASSET_PROPERTY))
    
    while CurrentLevel < TotalLevels:
        try:
            LevelSubsystem.load_level(Levels[CurrentLevel])
            Instances = GameplayStatics.get_all_actors_of_class(EditorSubsystem.get_editor_world(), BlueprintClass)
            LevelInstances = dict()
            
            for Instance in Instances:
                if bNeedProperty == True:
                    if DoesPropertyExist(Instance, PropertyName):
                        PropertyValue = GetPropertyValue(Instance, PropertyName)
                        LevelInstances[str(Instance.get_actor_label())] = PropertyValue
                    else:
                        if bIgnorePopups:
                            LevelInstances[str(Instance.get_actor_label())] = ""
                        else:
                            Answer = ShowDialog("Warning!", "Couldn't find the property "+str(ASSET_PROPERTY)+" in "+str(PACKAGE_NAME)+". Do you want to continue and save the file containing just the ocurrences of given actor?", unreal.AppMsgType.YES_NO_YES_ALL_NO_ALL, unreal.AppReturnType.NO_ALL)
                            if Answer == unreal.AppReturnType.YES or Answer == unreal.AppReturnType.YES_ALL:
                                bIgnorePopups = True
                                LevelInstances[str(Instance.get_actor_label())] = ""
                            else:
                                return LevelActors
                else:
                    LevelInstances[str(Instance.get_actor_label())] = ""
                  
            LevelActors[str(Levels[CurrentLevel])] = LevelInstances
            CurrentLevel += 1
        except:
            print("Couldn't open level: "+str(Levels[CurrentLevel]))
            CurrentLevel += 1
    
    return LevelActors

def DoesPropertyExist(Instance, Name):
    try:
        PropertyValue = Instance.get_editor_property(Name)
        unreal.log(str(PropertyValue))
        return True
    except:
        return False

def GetPropertyValue(Instance, Name):
    PropertyValue = Instance.get_editor_property(Name)
    Object = None
    try:
        Object = unreal.Object.cast(PropertyValue);
        PropertyValue = Object.get_name()
    except:
        unreal.log("Property is not an object, returning raw value")
    # Cast here the property to an object, and if so, get the fname(), return that
    return PropertyValue

    
def ShowDialog(Title, Message, MessageType, MessageReturnType):
    Result = EditorDialog.show_message(TextLibrary.conv_string_to_text(Title), TextLibrary.conv_string_to_text(Message), MessageType, default_value=MessageReturnType)
    # Message type format: unreal.AppMsgType.OK see more in documentation: https://docs.unrealengine.com/5.0/en-US/PythonAPI/class/AppMsgType.html#unreal.AppMsgType
    # Return type format: unreal.AppReturnType.NO see more in documentation: https://docs.unrealengine.com/5.0/en-US/PythonAPI/class/AppReturnType.html#unreal.AppReturnType
    
    return Result

def WriteCSV(Data):
    CurrentDateTime = datetime.now()
    StringDateTime = CurrentDateTime.strftime("%m_%d_%Y_%H_%M_%S")
    global CSV_NAME 
    CSV_NAME = "AIPR_"+str(PACKAGE_NAME)+"_"+StringDateTime+".csv"
    SaveDestination = str(PROJECT_FOLDER)+str(CSV_NAME)
    print(str(SaveDestination))
    Header = []
    if ASSET_PROPERTY != None:
        Header = ['Level', 'Instances', str(ASSET_PROPERTY)]
    else:
        Header = ['Level', 'Instances']
    
    try:
        with open (SaveDestination, 'w', encoding='UTF8', newline='') as CSVFile:
            Writer = csv.writer(CSVFile)
            Writer.writerow(Header)
            
            for Key in Data:
                LevelName = [Key, '']
                Writer.writerow(LevelName)
                Items = Data[Key]
                for Item in Items:
                    
                    if ASSET_PROPERTY != None:
                        InstanceData = ['', Item, Items[Item]]
                    else:
                        InstanceData = ['', Item]
                        
                    Writer.writerow(InstanceData)
        return True
    except:
        return False
    
def BeginTasks(AssetToLoad):
    TotalFrames = 100
    Text = "Performing tasks, please, be patient, it will all depend on the size and amount of the levels to check..."
    bFileCreated = False
    
    with unreal.ScopedSlowTask(TotalFrames, Text) as SlowTask:
        SlowTask.make_dialog(True)
        for i in range(TotalFrames):
            if SlowTask.should_cancel():
                break
            SlowTask.enter_progress_frame(0)
            Asset = GetAssetPath(AssetToLoad)
            References = GetAssetReferences(Asset)
            SlowTask.enter_progress_frame(10)
            Levels = FilterReferences(References)
            if len(Levels) == 0:
                break
            SlowTask.enter_progress_frame(40)
            Results = StoreReferences(Levels, AssetToLoad)
            if len(Results) == 0:
                break
            SlowTask.enter_progress_frame(40)
            bFileCreated = WriteCSV(Results)
            
            if bFileCreated == True:
                break
            
    return bFileCreated

def main():
    
    if len(sys.argv) < 2: # This could be better handled definitely, but it works as long as we use the widget to feed the script.
        unreal.log("No valid arguments were passed. Stopping the process...")
        return
    
    if not IsVersionCompatible():
        unreal.log("The Editor version is not valid to run this tool. This script is only compatible with UE5. Current version: "+ str(SystemLibrary.get_engine_version()))
        return
    
    global PROJECT_FOLDER, CSV_NAME, ASSET, PACKAGE_NAME, ASSET_PROPERTY
    
    ASSET = str(sys.argv[1])
    ASSET_PROPERTY = None
    PROJECT_FOLDER = SystemLibrary.get_project_directory()
    PACKAGE_NAME = str(GetAssetData(str(ASSET)).asset_name)
    CSV_NAME = ''
    
    if len(sys.argv) >= 3:
        ASSET_PROPERTY = str(sys.argv[2])
    
    bSuccess = BeginTasks(ASSET)
    
    if not bSuccess:
        ShowDialog("Error!", "The file wasn't saved.", unreal.AppMsgType.OK, unreal.AppReturnType.OK)
        return
    
    Answer = ShowDialog("Success!", "The file has been saved as: " +str(PROJECT_FOLDER)+str(CSV_NAME)+". Press OK to see it in the containing folder.", unreal.AppMsgType.OK_CANCEL, unreal.AppReturnType.OK)
    if Answer == unreal.AppReturnType.OK:
        Path = os.path.realpath(str(PROJECT_FOLDER))
        os.startfile(Path)
         
main()