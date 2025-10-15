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

First thing you want to do is to install git through your terminal  <br>
> `sudo apt-get update`  <br>
> `sudo apt-get install git gitk git-gui`  <br>
This will ask for your password  <br>

Next step is to clone the ardupilot repository by using this command (make sure you are in the directory you want to be in): <br> 
> `git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git`   <br>
<br>
Once you have finished cloning the ardupilot repository, change directory into the ardupilot directory  <br>

> `cd ardupilot` <br>
Now we have to install some required packages, which is made easy thanks to the script that is provided. Simply run this command: <br>
> `Tools/environment_install/install-prereqs-ubuntu.sh -y`<br>
The -y is used to automatically say 'yes' to all prompts that may pop-up during the install of the required packages <br>
Now reload the path: `. ~/.profile`

Now you should be able to build with waf using the following commands: <br>
> `./waf configure --board sitl` <br>
> `./waf copter`

This will take a few minutes...




# Running the ArduPilot SITL
