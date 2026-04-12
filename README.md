# This repository is for RUAutonomous for the 2025-2026 competition season!
 # FIGURE OUT HOW PLAY_TUNE_V2 WORKS!!!


# Installing and setting up the ArduPilot SITL

The ArduPilot SITL (Software-In-The-Loop) is a simulator that can simulate our drone and lets us run this simulation on our laptop/computer without the need for the physical drone. This is useful during our early stages of planning to test our initial versions of our Python programs and make sure we haven't created problems within our drone.  

<b>So how do we setup this ArduPilot SITL? </b>

## For Windows: 
First of all, install and setup an Ubuntu environment via WSL. It is also possible to use Cygwin for this setup but WSL is the most simple and efficient method to setup and run. <br><br>
Go to your Search bar and open Terminal (WITH administrator privileges) and type: `wsl --install` <br>
By default, the distro installed will be Ubuntu. If you want a specific distro, you can see a list of distros using: `wsl.exe --list --online` and you can install
a specific distro using: `wsl.exe --install [distro_name]` <br>

When you have WSL installed, you will have to create a username and password for your Linux distro. **REMEMBER THIS INFORMATION**
<br>

If WSL does not open, you will likely need to restart your computer. Now you can enter WSL by search 'wsl' in your Windows Search bar or you can open Terminal and type 'wsl'

More info on WSL and setup can be found here: https://learn.microsoft.com/en-us/windows/wsl/install 

Now to set up the rest of the Ardupilot SITL, follow the Linux instructions below...

<br>


## For MacOS

same thing but as ubuntu but get homebrew if you have it yet. ill update this section soon as I don't use macos and dont have much experience

## For Ubuntu Environments

Before doing anything, run:
> `sudo apt update && sudo apt upgrade -y`

First thing you want to do is to install git through your terminal  <br>
> `sudo apt-get update`  <br>
> `sudo apt-get install git gitk git-gui`<br> <br>

This will ask for your password<br>

Once you download git, it's time to create a Python virtual environment. Since we updated package lists, we should be able to easily create the virtual environment but why do we need this?

We use virtual environments because its like starting with a fresh slate with no unnecessary pip packages. If we never use a venv and had to install tons of different pip packages globally, some of the packages may cause conflicts with each other, leading to hours of debugging. When you create a venv, you have a Python environment with the bare minimum packages, where you can install packages needed for a specific project or program.

To create the environment, use the command:
`$: sudo apt install python3-venv`
`$: python3 -m venv venv` 
(the second 'venv' is just the name of your virtual environment so it can be whatever you want)

To activate the virtual environment, assuming you creating it in your home directory, you can run the following command:
`source ~/venv/bin/activate`
*** Replace 'venv' with whatever you named your virtual environment

Next step is to clone the ardupilot repository by using this command (make sure you are in the directory you want to be in): <br> 
`git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git`   
<br>
Once you have finished cloning the ardupilot repository, change directory into the ardupilot directory  <br>

> `cd ardupilot` <br> 

Now we have to install some required packages, which is made easy thanks to the script that is provided. Simply run this command: <br>

> `./Tools/environment_install/install-prereqs-ubuntu.sh -y`<br>

The -y is used to automatically say 'yes' to all prompts that may pop-up during the install of the required packages <br>
Now reload the path: `. ~/.profile`

Now you should be able to build with waf using the following commands: <br>
> `./waf configure --board sitl` <br>
> `./waf copter`

This will take a few minutes...

<b> Do this too! I am not sure why this is an issue but when you install all pre-requisites, some important packages don't install so run this command to install the extra required packages:</b>

`pip install empy==3.3.4 future gnureadline MAVProxy pexpect`

Also install the pip package we're going to be using to write the code pymavlink:

`pip install pymavlink`


# Running the ArduPilot SITL

When we want to run the ArduPilot SITL, we first have to activate the Python virtual environment <br>
`source ~/venv/bin/activate`<br>
This is assuming your venv is in your home directory. If not, change directories into your 'venv' folder to activate it. In order to deactivate the venv, type: <br>
`deactivate` <br>

Then locate your ardupilot folder (containing the cloned ardupilot repository) and change directory into `ardupilot/ArduCopter` <br>
From there, run this command to activate the SITL: <br>
`../Tools/autotest/sim_vehicle.py -v ArduCopter --no-rebuild --no-configure`
This will start the simulation at the default location defined. If you want a custom location (like the competition location), you have to add the -l flag 
followed by the lat,long,alt,heading
 `../Tools/autotest/sim_vehicle.py -v ArduCopter --no-rebuild --no-configure -l 40.5230578,-74.4581335,0,0` <br>
The location above is Busch Student Center. To view all modifiers, run this command:
`../Tools/autotest/sim_vehicle.py -v ArduCopter -D --help`
<br><br>
Once your simulation is running, you can open up QGroundControl and you will be able to see that you are connected to the drone on the SITL.