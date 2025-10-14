# This repository is for RUAutonomous for the 2025-2026 competition season!



# Installing and setting up the ArduPilot SITL

The ArduPilot SITL (Software-In-The-Loop) is a simulator that can simulate our drone and lets us run this simulation on our laptop/computer without the need
for the physical drone. This is useful during our early stages of planning to test our initial versions of our Python programs and make sure we haven't created problems within our drone.  
# ^^ Revise ^^

So how do we setup this ArduPilot SITL? 

# For Windows: 
First of all, install and setup an Ubuntu environment via WSL. It is also possible to use Cygwin for this setup but WSL is the most simple and efficient method to setup and run. 

# For MacOS



# For Ubuntu Environments

First thing you want to do is to install git through your terminal
> `sudo apt-get update`
> `sudo apt-get install git gitk git-gui`
This will ask for your password

Next step is to clone the ardupilot repository by using this command (make sure you are in the directory you want to be in):
> `git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git` 
Once you have finished cloning the ardupilot repository, change directory into the ardupilot directory

> `cd ardupilot`
Now we have to install some required packages, which is made easy thanks to the script that is provided. Simply run this command: 
> `Tools/environment_install/install-prereqs-ubuntu.sh -y`
The -y is used to automatically say 'yes' to all prompts that may pop-up during the install of the required packages
Now reload the path: `. ~/.profile`

Now you should be able to build with waf using the following commands:
> `./waf configure --board sitl`
> `./waf copter`






# Running the ArduPilot SITL
