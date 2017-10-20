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
    self.parent.categories = ["Quantification"]
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

    # Selection of the output spheres directory
    self.outputSphereDirectorySelector = ctk.ctkDirectoryButton()
    self.ioQFormLayout.addRow(qt.QLabel("Output Spheres Directory:"), self.outputSphereDirectorySelector)

    # Selection of the output surfaces directory
    self.outputSurfacesDirectorySelector = ctk.ctkDirectoryButton()
    self.ioQFormLayout.addRow(qt.QLabel("Output Surfaces Directory:"), self.outputSurfacesDirectorySelector)

    # Connections
    self.inputModelsDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
    self.inputFiducialDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
    self.sphericalModelDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
    self.outputSphereDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
    self.outputSurfacesDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)

    # Name simplification (string)
    self.modelsDirectory = str(self.inputModelsDirectorySelector.directory)
    self.fiducialDirectory = str(self.inputFiducialDirectorySelector.directory)
    self.sphericalDirectory = str(self.sphericalModelDirectorySelector.directory)
    self.outputsphereDirectory = str(self.outputSphereDirectorySelector.directory)
    self.outputsurfaceDirectory = str(self.outputSurfacesDirectorySelector.directory)
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
    self.outputsphereDirectory = str(self.outputSphereDirectorySelector.directory)
    self.outputsurfaceDirectory = str(self.outputSurfacesDirectorySelector.directory)

    # Check if each directory has been choosen
    self.applyButton.enabled = self.modelsDirectory != "." and self.fiducialDirectory != "." and self.sphericalDirectory != "." and self.outputsphereDirectory != "." and self.outputsurfaceDirectory != "."

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
    self.outputsphereDirectory = str(self.outputSphereDirectorySelector.directory)
    self.outputsurfaceDirectory = str(self.outputSurfacesDirectorySelector.directory)

    endRigidAlignment = logic.runRigidAlignment(modelsDir=self.modelsDirectory, fiducialDir=self.fiducialDirectory, sphereDir=self.sphericalDirectory, outputsphereDir=self.outputDirectory, outputsurfaceDir=self.outputDirectory)

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

  def runRigidAlignment(self, modelsDir, fiducialDir, sphereDir, outputsphereDir, outputsurfaceDir):
    
    # ------------------------------------ # 
    # ---------- RigidAlignment ---------- # 
    # ------------------------------------ # 

    print "--- function runRigidAlignment() ---"
    """
    Calling RigidAlignment CLI
        Arguments:
         --mesh [<std::string> input models directory]
         --landmark [<std::string> input fiducial files directory]
         --sphere [<std::string> common unit sphere]
         --output [<std::string> output sphers directory] 
    """
    print "--- Inspecting Input ---"
    # Creation of the parameters of SPV
    SPV_parameters = {}
    SPV_parameters["Directory"] = modelsDir
    #   If a binary of SPV has been installed
    if hasattr(slicer.modules, 'shapepopulationviewer'):
      SPV = slicer.modules.shapepopulationviewer
    #   If SPV has been installed via the Extension Manager
    elif hasattr(slicer.modules, 'launcher'):
      SPV = slicer.modules.launcher
    # Launch SPV
    slicer.cli.run(module = SPV, node = None, parameters = SPV_parameters, wait_for_completion=True)
    
    print "--- Rigid Alignment Running ---"
    # Run Rigid Alignment
    RigidAlignment_parameters = {}
    RigidAlignment_parameters["mesh"]       = modelsDir
    RigidAlignment_parameters["landmark"]   = fiducialDir
    RigidAlignment_parameters["sphere"]     = sphereDir
    RigidAlignment_parameters["output"]     = outputsphereDir
    slicer.cli.run(module = slicer.modules.rigidwrapper, node = None, parameters = RigidAlignment_parameters, wait_for_completion=True)
    print "--- Rigid Alignment Done ---"

    # ------------------------------------ # 
    # ------------ SurfRemesh ------------ # 
    # ------------------------------------ # 
    print "--- function runSurfRemesh() ---"
    """
    Calling SurfRemesh CLI
        Arguments:
         -t [<std::string> input spheres directory]
         -i [<std::string> input models directory]
         -r [<std::string> common unit sphere]
         -o [<std::string> output surfaces directory] 
    """
    listMesh = os.listdir(modelsDir)
    listSphere = os.listdir(outputsphereDir)

    if listMesh.count(".DS_Store"):
      listMesh.remove(".DS_Store")
    if listSphere.count(".DS_Store"):
      listSphere.remove(".DS_Store")

    for i in range(0,len(listMesh)):
      print listSphere[i]
      print listMesh[i]
      # Run SurfRemesh
      SurfRemesh_parameters = {}
      SurfRemesh_parameters["tempModel"]     = os.path.join(outputsphereDir, listSphere[i])
      SurfRemesh_parameters["input"]     = os.path.join(modelsDir, listMesh[i]) 
      SurfRemesh_parameters["ref"]     = sphereDir
      SurfRemesh_parameters["output"]     = os.path.join( outputsurfaceDir, listSphere[i].split("_rotSphere.vtk",1)[0] + "_aligned.vtk")
      slicer.cli.run(module = slicer.modules.SRemesh, node = None, parameters = SurfRemesh_parameters, wait_for_completion=True)
      print "--- Surface Remesh Done " + str(i) + "---"

      # ------------------------------------ # 
      # ------------ Color Maps ------------ # 
      # ------------------------------------ # 
      reader_in = vtk.vtkPolyDataReader()
      reader_in.SetFileName(str(os.path.join(modelsDir, listMesh[i])))
      reader_in.Update()
      init_mesh = reader_in.GetOutput()

      phiArray = init_mesh.GetPointData().GetScalars("_paraPhi")

      reader_out = vtk.vtkPolyDataReader()
      reader_out.SetFileName(os.path.join( outputsurfaceDir, listSphere[i].split("_rotSphere.vtk",1)[0] + "_aligned.vtk"))
      reader_out.Update()
      new_mesh = reader_out.GetOutput()
      new_mesh.GetPointData().SetActiveScalars("_paraPhi")
      new_mesh.GetPointData().SetScalars(phiArray)
      new_mesh.Modified()
      # write circle out
      polyDataWriter = vtk.vtkPolyDataWriter()
      polyDataWriter.SetInputData(new_mesh)
      polyDataWriter.SetFileName(os.path.join( outputsurfaceDir, listSphere[i].split("_rotSphere.vtk",1)[0] + "_aligned.vtk"))
      polyDataWriter.Write()
    print "--- Rigid Alignment Done ---"
    
    print "--- Inspecting Results ---"
    # Inspect Results
    SPV_parameters = {}
    SPV_parameters["Directory"] = outputsurfaceDir
    slicer.cli.run(module = SPV, node = None, parameters = SPV_parameters, wait_for_completion=True)