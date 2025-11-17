# This repository is for RUAutonomous for the 2025-2026 competition season!



# Installing and setting up the ArduPilot SITL

The ArduPilot SITL (Software-In-The-Loop) is a simulator that can simulate our drone and lets us run this simulation on our laptop/computer without the need
for the physical drone. This is useful during our early stages of planning to test our initial versions of our Python programs and make sure we haven't created problems within our drone.  
# ^^ Revise ^^

So how do we setup this ArduPilot SITL? 

## For Windows: 
First of all, install and setup an Ubuntu environment via WSL. It is also possible to use Cygwin for this setup but WSL is the most simple and efficient method to setup and run. <br><br>
> Go to your Search bar and open Powershell (WITH administrator privileges) and type: `wsl --install` <br>
By default, the distro installed will be Ubuntu. If you want a specific distro, you can see a list of distros using: `wsl.exe --list --online` and you can install
a specific distro using: `wsl.exe --install [distro_name]` <br>

When you have WSL installed, you will have to create a username and password for your Linux distro. **REMEMBER THIS INFORMATION**
<br>
More info on WSL and setup can be found here: https://learn.microsoft.com/en-us/windows/wsl/install <br>


## For MacOS

same thing but as ubuntu but get homebrew if you have it yet. ill update this section soon as I don't use macos and dont have much experience

## For Ubuntu Environments

First thing you want to do is to install git through your terminal  <br>
> `sudo apt-get update`  <br>
> `sudo apt-get install git gitk git-gui`<br> <br>


This will ask for your password  <br>

Next step is to clone the ardupilot repository by using this command (make sure you are in the directory you want to be in): <br> 
> `git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git`   <br>
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




# Running the ArduPilot SITL

When we want to run the ArduPilot SITL, we first have to activate the Python virtual environment <br>
Go to the folder in which you created your Python virtual environment and activate it:<br>
`source venv/bin/activate`<br><br>
In order to deactivate the venv, type: <br>
`deactivate` <br>

Then locate your ardupilot folder (containing the cloned ardupilot repository) and change directory into `ardupilot/ArduCopter` <br>
From there, run this command to activate the SITL: <br>
> `../Tools/autotest/sim_vehicle.py -v ArduCopter --no-rebuild --no-configure`
This will start the simulation at the default location defined. If you want a custom location (like the competition location), you have to add the -l flag 
followed by the lat,long,alt,heading
> `../Tools/autotest/sim_vehicle.py -v ArduCopter --no-rebuild --no-configure -l 40.5230578,-74.4581335,0,0` 
The location above is Busch Student Center. Want all the flags that you can add? Run this command:
`../Tools/autotest/sim_vehicle.py -v ArduCopter -D --help`
<br><br>
Once your simulation is running, you can open up QGroundControl and you will be able to see that you are connected to the drone on the SITL.