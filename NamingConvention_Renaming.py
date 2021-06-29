# This script runs through all the assets under the given path checking its name and deciding whether they've to be renamed based on its inclusion on ClassPrefixes
# and ClassSufixes. If their class is in one of these or both dicts, it'll try to rename it, save it and once done, save all dirty packages and fix up project redirectors.

# DISCLAIMER: Even though this has been tested, renaming assets in Unreal is not as safe as one would like it to be, so it does imply risks.
# So, yeah, follow a proper naming convention so this is useless :)

# https://twitter.com/_mdavz
# 2021
# v. 1.0

import unreal
import subprocess
import os
import platform

# Path to check our assets from. Currently using the root path to check the whole project, but can be any folder below root as well.
Path = '/Game/'

# List the assets and save how many of them there are
EditorUtil = unreal.EditorAssetLibrary()
PathUtil = unreal.Paths()
AssetList = EditorUtil.list_assets(Path)
AssetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
Dependencies=[]
DependencyOptions = unreal.AssetRegistryDependencyOptions(True, True, True, False, False)

# Currently there's limitations to which assets we can rename. Structs, DataAssets and Enums are not being detected/renamed correctly. Something to investigate
# so, for now, not included in the dict.
ClassPrefixes = {
    'ActorComponent':'BPC_',
    'AnimBlueprint':'ABP_',
    'AnimSequence':'A_',
    'AnimMontage':'M_',
    'BehaviorTree':'BT_',
    'BlackboardData':'BB_',
    'Blueprint':'BP_', # This will include anything blueprint (GameModes, Characters, Actors) as generally they will use the same prefix, apart from the specific Component case.
    'DataTable':'DT_',
    'Material':'M_',
    'MaterialInstanceConstant':'MI_',
    'MaterialParameterCollection':'MPC_',
    'ParticleSystem':'PS_',
    'PhysicsAsset':'SK_',
    'SkeletalMesh':'SK_',
    'Skeleton':'SK_',
    'StaticMesh':'SM_',
    'SoundWave':'S_',
    'Texture':'T_',
    'WidgetBlueprint':'WBP_',
}

ClassSuffixes = {
    'PhysicsAsset':'_PhysicsAsset',
    'Skeleton':'_Skeleton',
}

def GetAssetClass(Asset):

    if not Asset:
        return None
    else:
        AssetClassType = unreal.get_type_from_class(Asset.get_class())
        AssetClass = AssetClassType.__name__

        # When it comes to BPs we've to specifically load it as BP to find the *correct* class
        # In this case we only care about components, really. But this could be improved with another dict including different BP types. Can't find the point really.
        if AssetClass == 'Blueprint':
            # At this point the asset is already loaded, really. But the function check that as well. So it's only loaded once. Needed to check which Blueprint class the asset is.
            LoadedBP = EditorUtil.load_blueprint_class(Asset.get_path_name())
            LoadedBPClass = unreal.get_type_from_class(LoadedBP)

            if 'ActorComponent' in LoadedBPClass.__name__:
                AssetClass = 'ActorComponent'

        return AssetClass

# Feels like these two should be just one. Something under the lines of AssetNeedsModifications() returning an EnumType with which modification we need to do.
def AssetNeedsPrefix(Asset, Prefix):
    try:
        Asset.get_name().index(Prefix, 0)
    except ValueError:
        # Prefix not found, the asset needs renaming
        return True
    else:
        return False

def AssetNeedsSuffix(Asset, Suffix):
    return not Asset.get_name().endswith(Suffix)

# Ideally there should be only a function instead to deal with both, prefixes and suffixes. Have to find a cleaner way to do it.
def AddPrefix(Asset, Prefix):
    if AssetNeedsPrefix(Asset, Prefix):
        FinalName=Prefix+Asset.get_name()
        Rename(Asset, FinalName)
    else:
        return

def AddSuffix (Asset, Suffix):
    if AssetNeedsSuffix(Asset, Suffix):
        FinalName = Asset.get_name()+Suffix
        Rename(Asset, FinalName)
    else:
        return

def Rename(Asset, FinalName):
    # Nice addition would be to check whether the current asset has an innapropiate prefix instead, so we don't just add but also replace.
    NewPath = Asset.get_path_name().replace(Asset.get_name(), FinalName)

    # This will also attempt to check out the assets once saved if Source Control is available
    EditorUtil.rename_loaded_asset(Asset, NewPath)
    ResolveDependencies(Asset.get_path_name(), Dependencies)
    
    #Save all dependencies

#Get all dependencies per asset (and dependency) and add them to be saved later on.
def ResolveDependencies(DepPkg, Dependencies):
    Dependencies.append(DepPkg)
    PackageDependencies = AssetRegistry.get_dependencies(DepPkg, DependencyOptions)
    if PackageDependencies != None:
        for _DepPkg in PackageDependencies:
            if _DepPkg != None:
                if _DepPkg not in Dependencies:
                    if not str(_DepPkg).startswith('/Engine') and not str(_DepPkg).startswith('/Script'):
                        ResolveDependencies(_DepPkg, Dependencies)

def FixUpRedirectors(platform):
    #Seems like subprocess is not working on Mac same way it does on Windows, so using os.system instead for Mac. Probably will be the same for Linux if added

    EngineDir = None
    ProjectDir = None
    ResavePackagesCmd = None

    if platform == 'Windows':
        EngineDir = '"'+PathUtil.convert_relative_path_to_full(PathUtil.engine_dir()).replace("/","\\") + 'Binaries\\Win64\\UE4Editor.exe"'
        ProjectDir = '"'+ PathUtil.convert_relative_path_to_full(PathUtil.get_project_file_path()).replace("/","\\")+'"'
        ResavePackagesCmd = EngineDir + ' ' + ProjectDir + " -run=ResavePackages -fixupredirects -autocheckout -projectonly -unnatended"
        subprocess.run(ResavePackagesCmd)
    else:
        #MacOS
        if platform == "Darwin" :
            EngineDir = PathUtil.convert_relative_path_to_full(PathUtil.engine_dir()).replace(" ","\ ") + 'Binaries/Mac/UE4Editor.app/Contents/MacOS/UE4Editor'.replace(" ", "\ ")
            ProjectDir = PathUtil.convert_relative_path_to_full(PathUtil.get_project_file_path()).replace(" ","\ " )
            ResavePackagesCmd = EngineDir + ' ' + ProjectDir + " -run=ResavePackages -fixupredirects -autocheckout -projectonly"
            os.system(ResavePackagesCmd)
        else:
            unreal.log_warning("Attempted to fix up project redirectors, but currently this script only supports Windows and MacOS, please Fix Up Redirectors manually in " + Path)

# This is the core task, iterate all our assets and check whether they need to be renamed or not and do it accordingly. Save once finished.

for Asset in AssetList:
    LoadedAsset = EditorUtil.load_asset(Asset)
    AssetClass = GetAssetClass(LoadedAsset)
    if AssetClass != None:
        if AssetClass in ClassPrefixes:
           AddPrefix(LoadedAsset, ClassPrefixes[AssetClass])

        if AssetClass in ClassSuffixes:
           AddSuffix(LoadedAsset, ClassSuffixes[AssetClass])

#Fix redirectors

for DepPkg in Dependencies:
    Pkg = EditorUtil.load_asset(DepPkg)
    EditorUtil.save_loaded_asset(Pkg, False)

FixUpRedirectors(platform.system())
