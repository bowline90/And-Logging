# Android Logging Tool

## Description
This tool allow to speed up the reverse engineering activity automating some typical reverse engineering operation on Android APK.
It allow to automate:
- Insert *logging* method
- Repack smali code into *APK*
- Install *APK* into device
- Start application and output *Logcat*

## Installation
*Android Logging Tool* requirement:
- Python 2.7
- [ApkTool] (https://ibotpeaches.github.io/Apktool/)
- Android SDK
- JDK (for jarsigner)

Step to use Android Logging Tool:

1. Install all requirements
2. Adding to environment path the folder where you download the tool
3. Run `explore.py`

## Configuration
The first time run, the tool ask at user the path where subprogram can be found. In order to avoid problems, I suggest to insert absolute path.

If you want to modify this configuration, you should modify the *init.cfg* file in root directory of tool. If you erase that, the program asks the path again.

## Usage

In order to execute the tool run:

`explore.py <directory>`

If `<directory>` is missing, the script start from the current directory. In order to avoid problems, I suggest to use the directory created by *ApkTool*

For example (with *app-debug.apk*):
```
1. apktool d app-debug.apk
2. cd app-debug
3. explore.py
4. Have fun
```
### Logging features
This tool allow to insert log (throught *Logcat*) function in order to log the value of the variables

To insert log features, you should write on *smali* file:
- `#LOG PARAMETERS` to log the method's parameters
- `#LOG STACK` to log the stack trace
- `#LOG v#` to log the register `v#` (this function is not yet implemented)

**Pay Attention**: The script insert smali command just after the `#LOG` command. In order to avoid problems with the correct execution-flow, I suggest to insert `#LOG` BEFORE the first smali command.

## Limitations

This project is in the first stage, so that are a lot of problem and limitations (e.g. only one device connected at the time and *Logcat* print only "Injection" log).
