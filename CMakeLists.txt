cmake_minimum_required(VERSION 2.8.9)

project(GroupsExtension)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/GroupsExtension")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Mahmoud Mostapha (UNC)")
set(EXTENSION_DESCRIPTION "Group-wise Registration for Shape Correspondence")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/GroupsExtension.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/GroupsExtension/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(RigidAlignment)
add_subdirectory(GroupWiseRegisteration)
add_subdirectory(CLI)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
