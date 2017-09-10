import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# RigidAlignment
#

class RigidAlignment(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "RigidAlignment" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Mahmoud Mostapha (UNC)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# RigidAlignmentWidget
#

class RigidAlignmentWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    ###########################################################################
    ##                                                                       ##
    ##  Collapsible part for input/output parameters for RigidAlignment CLI  ##
    ##                                                                       ##
    ###########################################################################

    self.ioCollapsibleButton = ctk.ctkCollapsibleButton()
    self.ioCollapsibleButton.text = "IO"
    self.layout.addWidget(self.ioCollapsibleButton)
    self.ioQVBox = qt.QVBoxLayout(self.ioCollapsibleButton)

    # --------------------------------- #
    # ----- RigidAlignment Box DIRECTORIES ----- #
    # --------------------------------- #
    self.directoryGroupBox = qt.QGroupBox("Directories")
    self.ioQVBox.addWidget(self.directoryGroupBox)
    self.ioQFormLayout = qt.QFormLayout(self.directoryGroupBox)

    # Selection of the directory containing the input models
    self.inputMeshTypeHBox = qt.QVBoxLayout(self.directoryGroupBox)
    self.inputModelsDirectorySelector = ctk.ctkDirectoryButton()
    self.inputMeshTypeHBox.addWidget(self.inputModelsDirectorySelector)
    self.ioQFormLayout.addRow(qt.QLabel("Input Models Directory:"), self.inputMeshTypeHBox)

    # Selection of the input directory containing the landmark files 
    self.inputFiducialDirectorySelector = ctk.ctkDirectoryButton()
    self.ioQFormLayout.addRow(qt.QLabel("Input Fiducial Files Directory:"), self.inputFiducialDirectorySelector)

    # Selection of the directory which contains the common spherical model
    self.sphericalModelDirectorySelector = ctk.ctkDirectoryButton()
    self.ioQFormLayout.addRow("Input Common Unit Sphere:", self.sphericalModelDirectorySelector)

    # Selection of the output directory
    self.outputDirectorySelector = ctk.ctkDirectoryButton()
    self.ioQFormLayout.addRow(qt.QLabel("Output Directory:"), self.outputDirectorySelector)

    # Connections
    self.inputModelsDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
    self.inputFiducialDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
    self.sphericalModelDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
    self.outputDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)

    # Name simplification (string)
    self.modelsDirectory = str(self.inputModelsDirectorySelector.directory)
    self.fiducialDirectory = str(self.inputFiducialDirectorySelector.directory)
    self.sphericalDirectory = str(self.sphericalModelDirectorySelector.directory)
    self.outputDirectory = str(self.outputDirectorySelector.directory)
    # ------------------------------------------ #
    # ----- Apply button to launch the CLI ----- #
    # ------------------------------------------ #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.enabled = False
    self.ioQVBox.addWidget(self.applyButton)

    self.errorLabel = qt.QLabel("Error: Invalide inputs")
    self.errorLabel.hide()
    self.errorLabel.setStyleSheet("color: rgb(255, 0, 0);")
    self.ioQVBox.addWidget(self.errorLabel)

    # Connections
    self.applyButton.connect('clicked(bool)', self.onApplyButtonClicked)

    # ----- Add vertical spacer ----- #
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    # Update names
    self.modelsDirectory = str(self.inputModelsDirectorySelector.directory)
    self.fiducialDirectory = str(self.inputFiducialDirectorySelector.directory)
    self.sphericalDirectory = str(self.sphericalModelDirectorySelector.directory)
    self.outputDirectory = str(self.outputDirectorySelector.directory)

    # Check if each directory has been choosen
    self.applyButton.enabled = self.modelsDirectory != "." and self.fiducialDirectory != "." and self.sphericalDirectory != "." and self.outputDirectory != "."

    # Hide error message if printed
    self.errorLabel.hide()

  ## Function onSpecifyPropertyChanged(self):
  # Enable/Disable associated weights

  def onApplyButtonClicked(self):
    logic = RigidAlignmentLogic()
    self.errorLabel.hide()
    # Update names
    self.modelsDirectory = str(self.inputModelsDirectorySelector.directory)
    self.fiducialDirectory = str(self.inputFiducialDirectorySelector.directory)
    self.sphericalDirectory = str(self.sphericalModelDirectorySelector.directory)
    self.outputDirectory = str(self.outputDirectorySelector.directory)

    endRigidAlignment = logic.runRigidAlignment(modelsDir=self.modelsDirectory, fiducialDir=self.fiducialDirectory, sphereDir=self.sphericalDirectory, outputDir=self.outputDirectory)

    ## RigidAlignment didn't run because of invalid inputs
    if not endRigidAlignment:
        self.errorLabel.show()

#
# RigidAlignmentLogic
#

class RigidAlignmentLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def runRigidAlignment(self, modelsDir, fiducialDir, sphereDir, outputDir):
    print "--- function runRigidAlignment() ---"

    """
    Calling RigidAlignment CLI
        Arguments:
         --mesh [<std::string> input models directory]
         --landmark [<std::string> input fiducial files directory]
         --sphere [<std::string> common unit sphere]
         --output [<std::string> output directory] 
    """
    cli_parameters = {}
    cli_parameters["mesh"]       = modelsDir
    cli_parameters["landmark"]   = fiducialDir
    cli_parameters["sphere"]     = sphereDir
    cli_parameters["output"]     = outputDir

    self.setupModule(slicer.modules.rigidwrapper, cli_parameters)