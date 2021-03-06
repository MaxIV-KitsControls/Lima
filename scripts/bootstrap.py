###########################################################################
# This file is part of LImA, a Library for Image Acquisition
#
#  Copyright (C) : 2009-2017
#  European Synchrotron Radiation Facility
#  BP 220, Grenoble 38043
#  FRANCE
# 
#  Contact: lima@esrf.fr
# 
#  This is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
# 
#  This software is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
############################################################################
import sys, os
import platform, multiprocessing
	
def check_options(options_pass):
	options_lima=[]
	options_script=[]
	for arg in options_pass:
		if arg=="--help" or arg=="-h" or arg=="-help" or arg=="-?":
			with open("INSTALL.txt", 'r') as f:
			    print(f.read())
			    sys.exit()
		if "--install-prefix=" in arg:
			options_script.append(arg)
		elif arg=="-g" or arg=="--git":
			options_script.append("git")
		elif "--install-python-prefix=" in arg:
			options_script.append(arg)
		elif "--find-root-path=" in arg:
			options_script.append(arg)
		else:
			options_lima.append(arg)
	return(options_script,options_lima)

def git_clone_submodule(submodules):
	submodules.append("third-party/Processlib")
	try:
		for submodule in submodules:
			if submodule not in not_submodule:
				if submodule in camera_list:
					submodule="camera/"+str(submodule)
				if submodule=="espia":
					submodule="camera/common/"+str(submodule)
				if submodule=="pytango-server":
					submodule="applications/tango/python"
				init_check = os.system("git submodule init " +str(submodule))
				if str(init_check)!="0":
					raise Exception("Couldn't init the following submodule : "+str(submodule))
		os.system("git submodule update")
		checkout_check = os.system("git submodule foreach 'git checkout cmake'")
		if str(checkout_check)!="0":
			raise Exception("Make sure every submodule has a branch cmake.")
	except Exception as inst:
				if str(init_check)!="0":
					sys.exit("Problem with submodule init")
				else:
					sys.exit("Problem with cmake branch")

def config_cmake_options(options):
	configFile = 'scripts/config.txt'
	option_name = []
	config_cmake = []
	for arg in options:
		for config_prefix, sub_dir in [("limacamera", "camera"), 
					       ("lima-enable", "third-party")]:
			prefix=sub_dir+"/"
			if arg.startswith(prefix):
				arg=config_prefix+'-'+arg[len(prefix):]
		arg=arg.replace("-", "_")
		option_name.append(arg.upper())
	#return option in config.txt activated (=1) if passed as argument
	#and also those not specified as empty (=) or disabled (=0) in file
	with open(configFile) as f:
		for line in f:
			line=line.strip()
			if not line or line.startswith("#"):
				continue
			config_option,val=line.split("=")
			if " " in val and not val.startswith('"'):
				val='"%s"'%val
			for option in option_name:
				if option == config_option:
					val=str(1)
					break
				#arg-passed option must match the end of config_option
				#and must be preceeded by '_' separator
				t = config_option.split(option)
				if (len(t) == 2) and (t[0][-1] == '_') and not t[1]:
					val=str(1)
					break
			if val and (val != str(0)):
				config_cmake.append("-D%s=%s" % (config_option, val))
		config_cmake = " ".join(config_cmake)
	return config_cmake

def install_lima_linux():
	if not os.path.exists(build_path):
		os.mkdir(build_path)
	os.chdir(build_path)
	global install_path, install_python_path, find_root_path
	try:
                if install_path != "": install_path = " -DCMAKE_INSTALL_PREFIX="+str(install_path)
                if install_python_path != "": install_python_path =  " -DPYTHON_SITE_PACKAGES_DIR="+str(install_python_path)
                if find_root_path != "": find_root_path = " -DCMAKE_FIND_ROOT_PATH="+str(find_root_path)
                cmake_check = os.system("cmake -G\"Unix Makefiles\" "+source_path+" "+cmake_config+install_path+install_python_path+find_root_path)
                if str(cmake_check)!="0":
                        raise Exception("Something is wrong in your CMake environement. Make sure your configuration is good.")
        
                compilation_check = os.system("make -j"+str(multiprocessing.cpu_count()+1))
                if str(compilation_check)!="0":
                        raise Exception("CMake couldn't build Lima. Contact lima@esrf.fr for help.")
                install_check = os.system("make install")
                if str(install_check)!="0":
                        raise Exception("CMake couldn't install libraries. Make sure you have necessaries rights.")
	except Exception as inst:
                if str(cmake_check)!="0":
                        sys.exit("Problem in CMake configuration")
                elif str(compilation_check)!="0":
                        sys.exit("Problem in CMake compilation")
                else:
                        sys.exit("Problem in CMake installation")

def install_lima_windows():
	global install_path, install_python_path, find_root_path
	# for windows check compat between installed python and mandatory vc++ compiler
	# See, https://wiki.python.org/moin/WindowsCompilers
	if sys.version_info < (2, 6):
		sys.exit("Only python > 2.6 supported")
	elif sys.version_info <= (3, 2):
		win_compiler = "Visual Studio 9 2008"
	elif sys.version_info <= (3, 4):
		win_compiler = "Visual Studio 10 2010" 
	else:
		win_compiler = "Visual Studio 14 2015"
	# now check architecture
	if platform.architecture()[0] == '64bit': arch = ' Win64'
	else: arch = ''
	win_compiler+=arch
	
	print ('Found Python ', sys.version)
	print ('Used compiler: ', win_compiler)
	cmake_cmd = 'cmake -G"'+win_compiler+'" '
	
	if not os.path.exists(build_path):
		os.mkdir(build_path)
	os.chdir(build_path)
	try :
		if install_path != "": install_path = " -DCMAKE_INSTALL_PREFIX="+str(install_path)
		if install_python_path != "": install_python_path =  " -DPYTHON_SITE_PACKAGES_DIR="+str(install_python_path)
		if find_root_path != "": find_root_path = " -DCMAKE_FIND_ROOT_PATH="+str(find_root_path)
                
		cmake_check = os.system(cmake_cmd+source_path+" "+cmake_config+install_path+install_python_path+find_root_path)

		if str(cmake_check)!="0":
			raise Exception("Something went wrong in the CMake preparation. Make sure your configuration is good.")

		compilation_check = os.system("cmake --build . --target install --config Release")
		if str(compilation_check)!="0":
			raise Exception("CMake couldn't build or install libraries. Contact lima@esrf.fr for help.")
	except Exception as inst:
		if str(cmake_check)!="0":
			sys.exit("Problem in CMake configuration")
		else:
			sys.exit("Problem in CMake compilation or installation.")
			


if __name__ == '__main__':
	OS_TYPE=platform.system()
	del sys.argv[0]
	not_submodule=('git', 'python', 'tests', 'test', 'cbf', 'lz4', 'fits', 'gz', 'tiff', 'hdf5')
	camera_list=('adsc', 'andor3', 'basler', 'dexela', 'frelon', 'hexitec', 'marccd', 'merlin', 'mythen3', 'perkinelmer', 'pilatus', 'pointgrey', 'rayonixhs', 'ultra', 'xh', 'xspress3', 'andor', 'aviex', 'eiger', 'hamamatsu', 'imxpad', 'maxipix', 'mythen', 'pco', 'photonicscience','pixirad', 'prosilica', 'roperscientific', 'ueye', 'v4l2', 'xpad', 'lambda', 'slsdetector','fli')
	install_path=""
	install_python_path=""
	find_root_path = ""
	source_path=os.getcwd()
	build_path=os.path.join(source_path, "build")
	script_options, lima_options = check_options(sys.argv)

	#No git option under windows for obvious reasons.
	if OS_TYPE=="Linux":
		if "git" in script_options:
                        git_clone_submodule(lima_options)

	cmake_config = config_cmake_options(lima_options)
	print (cmake_config)
	sys.stdout.flush()
	for option in script_options:
		if "--install-prefix=" in option:
			install_path=option[17:]
		if "--install-python-prefix=" in option:
			install_python_path=option[24:]
		if "--find-root-path=" in option:
			print (option)
			find_root_path=option[17:]
	if OS_TYPE=="Linux":
		install_lima_linux()
		
	elif OS_TYPE=="Windows":
		install_lima_windows()

	
