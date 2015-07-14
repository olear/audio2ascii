# -*- coding: utf-8 -*-

#Note that Viewers are never exported
#This file was automatically generated by Natron PyPlug exporter version 1.
import NatronEngine

# extra lib added
import NatronGui
import os, time, tempfile
from os import *

def getPluginID():
    return "AudioToAscii"

def getLabel():
    return "AudioToAscii"

def getVersion():
    return 1

def getIconPath():
    return "AudioToAscii.png"

def getGrouping():
    return "Other"

def getDescription():
    return "Launch external bash script Audio2Ascii (only linux).\nIt convert audio file into ascii curve that you can import in the Natron curve editor.\You can download it at https://github.com/rcspam/audio2ascii)\nYou must have it in your $PATH."
    
# extra defs added

def error_man(titleEM, messEM):
    NatronGui.natron.warningDialog(titleEM, messEM)

def kill_pid_player(tfKPP):
    pid_file_kpp = open(tfKPP, "r")
    pid = pid_file_kpp.readline()
    os.system("kill " + pid)
    pid_file_kpp.close()

def audioToAscii(audioFileATA, asciiFileATA, dimATA, fpsATA, durationATA, xHeightATA, yHeightATA):
    if NatronEngine.natron.isUnix():
        if NatronEngine.natron.isLinux():
            audio2ascii_dir = "$HOME/.local/share/INRIA/Natron/Plugins/"
        elif NatronEngine.natron.isMacOSX():
            audio2ascii_dir = "$HOME/Library/Application\ Support/INRIA/Natron/Plugins/"
        exec_a2a = str(audio2ascii_dir + "audio2ascii.sh ")
        
        # Files to pass
        files_a2a = str("'" + str(audioFileATA) + "' '" + str(asciiFileATA) + "' ")
        # Param to pass
        param_a2a = str(dimATA) + " " +  str(fpsATA) + " " +  str(durationATA) + " " +  str(xHeightATA)  + " " + str(yHeightATA)
        # Launch audio2ascii
        ret_a2a = os.system(exec_a2a + files_a2a + param_a2a )
        return ret_a2a
    elif NatronEngine.natron.isWindows():
        # add executable for windows here
        error_man("Unix Only", "Sorry, this plugin works only on Linux and Mas Osx !")

def animCurves(thisParam, fileAC, dimAC, fpsAC, durationAC ,frameStartAC):
    # ascii file
    asciiAC = open(fileAC, "r")
    # end frame
    lineAC = int(fpsAC) * int(durationAC) + int(frameStartAC)
    # anim x
    if dimAC == 0:
        # reset x before recalculate
        thisParam.removeAnimation(0)
        for frameC in range(int(frameStartAC),lineAC):
            x, y = asciiAC.readline().split ("_")
            thisParam.setValueAtTime(float(x), frameC, 0)
    # anim y
    elif dimAC == 1:
        # reset y before recalculate
        thisParam.removeAnimation(1)
        for frameC in range(int(frameStartAC),lineAC):
            x, y = asciiAC.readline().split ("_")
            thisParam.setValueAtTime(float(y), frameC, 1)
    # anim yx
    elif dimAC == 2:
        # reset x and y before recalculate
        thisParam.removeAnimation(0)
        thisParam.removeAnimation(1)
        for frameC in range(int(frameStartAC),lineAC):
            x, y = asciiAC.readline().split ("_")
            thisParam.setValueAtTime(float(x), frameC, 0)
            thisParam.setValueAtTime(float(y), frameC, 1)
    asciiAC.close()

    

def paramHasChanged(thisParam, thisNode, thisGroup, app, userEdited):
    # audio input file
    audio_file = thisNode.inputFile.get()
    # ascii output file
    ascii_file = thisNode.curveFile.get()
    # external editing app
    ext_edit_app = thisNode.editApp.get()
    ext_edit_app_param = thisNode.editParam.get()
    
    tmp_file = thisNode.tmpFile.get()
    
    # update start at current frame
    if thisParam == thisNode.currentFrame:
        thisNode.atFrameNum.set(app.timelineGetTime())
    
    # convert dimension in comprehensive thing for audio2ascii script 
    dim = thisNode.dimEnsion.get()
    if dim == 0:
        dimension = "x"
    elif dim == 1:
        dimension = "y"
    elif dim == 2:
        dimension = "xy" 
    
    # edit with External app
    if audio_file and ext_edit_app and thisParam == thisNode.editAudio:
        # On Linux and Osx
        if NatronEngine.natron.isUnix():
            os.system(ext_edit_app + " " + ext_edit_app_param + " '" + audio_file + "' &")
        if NatronEngine.natron.isWindows():
            # add executable for windows here
            NatronGui.natron.warningDialog("Unix Only", "Sorry, this plugin works only on Linux and Mas Osx !")
    # no editor path set
    else:
        if not ext_edit_app and thisParam == thisNode.editAudio:
            error_man("Audio Editor", "You need to set a audio editor !\nUnfold group below and fill the editor settings")
        if not audio_file and thisParam == thisNode.editAudio:
            error_man("Audio Editor", "You need to set a audio file before edit it !")
    
    # Import Curve # add verif param set !!!!
    if ascii_file and audio_file and thisParam == thisNode.importCurve:
        ret_exec = audioToAscii(audio_file, ascii_file, dimension, thisNode.framesPerSec.get(), thisNode.duraTion.get(), thisNode.xHeight.get(), thisNode.yHeight.get())
        # test and wait end of audio2ascii 
        if ret_exec == 0:
            # calculate animation 
            animCurves(thisNode.curveIn, ascii_file, thisNode.dimEnsion.get(), thisNode.framesPerSec.get(), thisNode.duraTion.get(), thisNode.atFrameNum.get())
    # Is input and output files set before generate curve
    if not audio_file and thisParam == thisNode.importCurve:
        error_man("Audio File", "No Audio File set !\nYou need to set a input audio file path before generate the curves.")
    if not ascii_file and thisParam == thisNode.importCurve:
        error_man("Curve File", "No Curve File set !\nYou need to set a output curve file path before generate the curves.")
    # Reset the curve
    if thisParam == thisNode.resetCurves:
        thisNode.curveIn.removeAnimation(0)
        thisNode.curveIn.removeAnimation(1)

    # play preview
    if thisParam == thisNode.playSync:
        if audio_file and tmp_file:
            # stop viewer & ffplay if playing
            kill_pid_player(tmp_file)
            # Some init dor the Viewer
            app.pane1.Viewer1.setPlaybackMode(NatronEngine.Natron.PlaybackModeEnum(0))
            app.pane1.Viewer1.setFrameRange(thisNode.atFrameNum.get(), thisNode.duraTion.get() + thisNode.atFrameNum.get())
            # calculate ffplay duration loop
            duration_loop = thisNode.duraTion.get() / thisNode.framesPerSec.get()
            # start ffplay
            os.system("ffplay -nodisp " + str(audio_file) + " -t " + str(duration_loop) + " -loop 0  & echo $! >" + tmp_file)
            app.pane1.Viewer1.pause()
            app.pane1.Viewer1.seek(thisNode.atFrameNum.get())
            app.pane1.Viewer1.startForward()
        else:
            error_man("Audio Editor", "You need to set a audio file before preview !")
    # Stop preview
    if thisParam == thisNode.stopSync:
        if audio_file and tmp_file:
            kill_pid_player(tmp_file)
            app.pane1.Viewer1.pause()
        else:
            error_man("Audio Editor", "You need to set a audio file before preview !")

## / extra defs

def createInstance(app,group):

    #Create all nodes in the group
    lastNode = app.createNode("fr.inria.built-in.Output", 1, group)
    lastNode.setScriptName("Output1")
    lastNode.setLabel("Output1")
    lastNode.setPosition(758.75, 325.125)
    lastNode.setSize(104, 44)
    lastNode.setColor(0.699992, 0.699992, 0.699992)
    groupOutput1 = lastNode

    param = lastNode.getParam("Output_layer_name")
    if param is not None:
        param.setValue("RGBA")
        param.setVisible(False)
        del param

    param = lastNode.getParam("highDefUpstream")
    if param is not None:
        param.setVisible(False)
        del param

    del lastNode


    lastNode = app.createNode("fr.inria.built-in.Input", 1, group)
    lastNode.setScriptName("Input1")
    lastNode.setLabel("Input1")
    lastNode.setPosition(758.75, 161.125)
    lastNode.setSize(104, 44)
    lastNode.setColor(0.300008, 0.500008, 0.2)
    groupInput1 = lastNode

    param = lastNode.getParam("Output_layer_name")
    if param is not None:
        param.setValue("RGBA")
        param.setVisible(False)
        del param

    param = lastNode.getParam("highDefUpstream")
    if param is not None:
        param.setVisible(False)
        del param

    del lastNode

    #Create the parameters of the group node the same way we did for all internal nodes
    lastNode = group
    param = lastNode.getParam("highDefUpstream")
    if param is not None:
        param.setVisible(False)
        del param

    param = lastNode.getParam("onParamChanged")
    if param is not None:
        param.setValue("AudioToAscii.paramHasChanged")
        del param


    #Create the user-parameters
    lastNode.userNatron = lastNode.createPageParam("userNatron", "Settings")
    param = lastNode.createFileParam("inputFile", "Audio File")
    param.setSequenceEnabled(False)

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Path to audio file.\nSignificant number of formats are supported including:\nMP3/4, WAV, W64, AIFF, OGG, FLAC.")
    param.setAddNewLine(True)
    param.setAnimationEnabled(False)
    lastNode.inputFile = param
    del param

    param = lastNode.createButtonParam("editAudio", "Edit audio file")

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Audio editor.\nYou can setup it in 'Editor Settings")
    param.setAddNewLine(False)
    param.setPersistant(False)
    param.setEvaluateOnChange(False)
    lastNode.editAudio = param
    del param

    # Group /
    param = lastNode.createGroupParam("setEditor", "Editor setting")

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Unfold to setup audio editor ")
    param.setAddNewLine(True)
    param.setEvaluateOnChange(False)
    lastNode.setEditor = param
    del param

    param = lastNode.createFileParam("editApp", "Audio editor")
    param.setSequenceEnabled(False)

    #Add the param to the group, no need to add it to the page
    lastNode.setEditor.addParam(param)

    #Set param properties
    param.setHelp("Set the audio editor path")
    param.setAddNewLine(True)
    param.setAnimationEnabled(False)
    param.setDefaultValue("audacity")
    lastNode.editApp = param
    del param

    param = lastNode.createStringParam("editParam", "Audio editor parameters")
    param.setType(NatronEngine.StringParam.TypeEnum.eStringTypeDefault)
    param.setDefaultValue("")

    #Add the param to the group, no need to add it to the page
    lastNode.setEditor.addParam(param)

    #Set param properties
    param.setHelp("Set the audio editor command line parameters")
    param.setVisible(True)
    param.setAddNewLine(False)
    param.setAnimationEnabled(True)
    lastNode.editParam = param
    del param
    # / Group

    param = lastNode.createFileParam("curveFile", "Curve File")
    param.setSequenceEnabled(False)

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("")
    param.setAddNewLine(True)
    param.setAnimationEnabled(False)
    param.setDefaultValue("/tmp/curve.ascii")
    lastNode.curveFile = param
    del param

    param = lastNode.createChoiceParam("dimEnsion", "Dimension")
    entries = [ ("x", ""),
    ("y", ""),
    ("xy", "")]
    param.setOptions(entries)
    del entries

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Curve dimensions X/Y(Left/Right)")
    param.setAddNewLine(True)
    param.setAnimationEnabled(True)
    options = param.getOptions()
    foundOption = False
    for i in range(len(options)):
        if options[i] == "x":
            param.setValue(i)
            foundOption = True
            break
    if not foundOption:
        app.writeToScriptEditor("Could not set option for parameter dimEnsion of node AudioToAscii1")
    lastNode.dimEnsion = param
    del param

    param = lastNode.createIntParam("framesPerSec", "Frame Rate")
    param.setDisplayMinimum(0, 0)
    param.setDisplayMaximum(100, 0)
    param.setDefaultValue(24, 0)

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Calculate curve with this frame rate")
    param.setAddNewLine(True)
    param.setAnimationEnabled(True)
    lastNode.framesPerSec = param
    del param

    param = lastNode.createIntParam("duraTion", "Duration")
    param.setDisplayMinimum(0, 0)
    param.setDisplayMaximum(500, 0)
    param.setDefaultValue(240, 0)

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Duration of the curve in frames")
    param.setAddNewLine(True)
    param.setAnimationEnabled(True)
    lastNode.duraTion = param
    del param

    param = lastNode.createIntParam("xHeight", "Height X")
    param.setDisplayMinimum(0, 0)
    param.setDisplayMaximum(500, 0)
    param.setDefaultValue(100, 0)

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Height of X deviation in pixels")
    param.setAddNewLine(True)
    param.setAnimationEnabled(True)
    lastNode.xHeight = param
    del param

    param = lastNode.createIntParam("yHeight", "Height Y")
    param.setDisplayMinimum(0, 0)
    param.setDisplayMaximum(500, 0)
    param.setDefaultValue(100, 0)

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Height of Y deviation in pixels")
    param.setAddNewLine(True)
    param.setAnimationEnabled(True)
    lastNode.yHeight = param
    del param

    param = lastNode.createIntParam("atFrameNum", "Start at frame")
    param.setDisplayMinimum(1, 0)
    param.setDisplayMaximum(500, 0)
    param.setDefaultValue(1, 0)

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Start the generate curve at this frame on the timeline")
    param.setAddNewLine(True)
    param.setAnimationEnabled(True)
    lastNode.atFrameNum = param
    del param

    param = lastNode.createButtonParam("currentFrame", "Current Frame")

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Update start frame to current frame")
    param.setAddNewLine(False)
    param.setPersistant(False)
    param.setEvaluateOnChange(False)
    lastNode.currentFrame = param
    del param

    param = lastNode.createButtonParam("importCurve", "Generate the curve")

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Generate curve from parameters")
    param.setAddNewLine(True)
    param.setPersistant(False)
    param.setEvaluateOnChange(False)
    lastNode.importCurve = param
    del param
    
    param = lastNode.createDouble2DParam("curveIn", "Curve ")
    param.setMinimum(-2.14748e+09, 0)
    param.setMaximum(2.14748e+09, 0)
    param.setDisplayMinimum(0, 0)
    param.setDisplayMaximum(500, 0)
    param.setMinimum(-2.14748e+09, 1)
    param.setMaximum(2.14748e+09, 1)
    param.setDisplayMinimum(0, 1)
    param.setDisplayMaximum(500, 1)

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Resultant Curve (keyframes)")
    param.setAddNewLine(True)
    param.setAnimationEnabled(True)
    lastNode.curveIn = param
    del param

    param = lastNode.createButtonParam("resetCurves", "Reset curves")

    #Add the param to the page
    lastNode.userNatron.addParam(param)

    #Set param properties
    param.setHelp("Reset the curves to 0")
    param.setAddNewLine(False)
    param.setPersistant(False)
    param.setEvaluateOnChange(False)
    lastNode.resetCurves = param
    del param

    # ONLY Unix (test preview Viewer/Audio)
    if NatronEngine.natron.isUnix():
        param = lastNode.createStringParam("viewerAudio", "Preview Viewer/Audio")
        param.setType(NatronEngine.StringParam.TypeEnum.eStringTypeLabel)
        
        #Add the param to the page
        lastNode.userNatron.addParam(param)
        
        #Set param properties
        param.setHelp("")
        param.setAddNewLine(True)
        param.setEvaluateOnChange(False)
        param.setAnimationEnabled(False)
        lastNode.viewerAudio = param
        del param
        
        param = lastNode.createButtonParam("playSync", "\u25b6")

        #Add the param to the page
        lastNode.userNatron.addParam(param)
        
        #Set param properties
        param.setHelp("Start preview  Viewer/Audio\nFor a better sync, Play/Cache the images in the viewer before preview")
        param.setAddNewLine(True)
        param.setPersistant(False)
        param.setEvaluateOnChange(False)
        lastNode.playSync = param
        del param
        
        param = lastNode.createButtonParam("stopSync", "\u25a0")

        #Add the param to the page
        lastNode.userNatron.addParam(param)

        #Set param properties
        param.setHelp("Stop preview Viewer/Audio")
        param.setAddNewLine(False)
        param.setPersistant(False)
        param.setEvaluateOnChange(False)
        lastNode.stopSync = param
        del param
        
        param = lastNode.createStringParam("betterPreview", "It's better to Play/Cache the images\nin the viewer before start the preview")
        param.setType(NatronEngine.StringParam.TypeEnum.eStringTypeLabel)

        #Add the param to the page
        lastNode.userNatron.addParam(param)

        #Set param properties
        param.setHelp("")
        param.setAddNewLine(False)
        param.setEvaluateOnChange(False)
        param.setAnimationEnabled(False)
        lastNode.betterPreview = param
        del param
        
        # Create a tempfile within "ffplay pid"
        param = lastNode.createFileParam("tmpFile", "Temp File")
        param.setVisible(False)
        tf = tempfile.NamedTemporaryFile(delete=False)
        param.setDefaultValue(tf.name)
        lastNode.tmpFile = param
        del param

    # extra callback added
    app.AudioToAscii1.onParamChanged.set("AudioToAscii.paramHasChanged")    
    
    #Refresh the GUI with the newly created parameters
    lastNode.refreshUserParamsGUI()
    del lastNode

    #Now that all nodes are created we can connect them together, restore expressions
    groupOutput1.connectInput(0, groupInput1)

