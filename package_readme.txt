# Lunar Unity Mobile Console

GitHub page:
https://github.com/SpaceMadness/lunar-unity-console

Asset store link:
https://www.assetstore.unity3d.com/#!/content/43800

Forum thread:
http://forum.unity3d.com/threads/lunar-mobile-console-high-performance-unity-ios-android-logger-built-with-native-platform-ui.347650/

Requires Unity 5.0 or later.

## Project Goals

Build a high-performance Unity iOS/Android logger using the native platform UI.  

## Platform Support
- iOS: requires iOS 8 or later
- Android: requires API Level 9 or later

## Key Benefits
- Native C/Objective-C/Java code with a low memory footprint.
- Works well with a huge log amount (up to 100000 entries).
- Built with a native platform UI (does NOT rely on Unity GUI).
- Resolution independent (looks great on highres/retina displays).
- Does NOT modify scenes or add assets.
- Removes completely from the release build with a single mouse click or from the command line (absolutely NO traces left).

## Features
- Instant error notification (never miss an unhandled exception again)
- Quick logger output access with a multi touch gesture
- Crystal clear font and a nice mobile-friendly interface
- Filter by text and log type
- Collapse similar elements
- Tap log entry to view stack trace
- Scroll lock, copy-to-clipboard and e-mail options
- Automatic updates!

## Installation
- Automatic:
  Unity Editor Menu:  Window ▶ Lunar Mobile Console ▶ Install...

- Manual:
  Drag'n'Drop `LunarConsol.prefab` (Assets/LunarConsole/Scripts/LunarConsole.prefab) into your current scene's hierarchy and save your changes. You only need to do it once for your startup scene.

## Using the console

The console can be open with one of the configured multi touch gestures. By default two finger swipe is used. To set a desired gesture:

* Select 'LunarConsole' game object in the Hierarchy window.
* Find 'Lunar Console' script settings in the Inspector window.
* Chose a gesture from the 'Gesture' drop down list (to disable multi touch gestures - chose 'None')

## Stack trace frames

Touch the log entry to view its stack trace.

Important: make sure to set the "Development Build" flag in your publishing settings otherwise you will only be able to see exceptions traces.

For more info see:
http://docs.unity3d.com/Manual/PublishingBuilds.html

## Enable/Disable plugin for debug/release
- To disable:
  Window ▶ Lunar Mobile Console ▶ Disable
- To re-enable:
  Window ▶ Lunar Mobile Console ▶ Enable

  When disabled, the plugin source files and resources would NOT appear in the generated native platform project.

## Build Automation support
You can enable/disable the plugin from the command line (and make it a part of your build process)

- To disable:
  <UNITY_BIN_PATH>  -quit -batchmode  -executeMethod LunarConsoleInternal.Installer.DisablePlugin
- To enable:
  <UNITY_BIN_PATH>  -quit -batchmode  -executeMethod LunarConsoleInternal.Installer.EnablePlugin

<UNITY_BIN_PATH> locations:
- Mac OS X: /Applications/Unity/Unity.app/Contents/MacOS/Unity
- Windows: c:\Program Files\Unity\Editor\Unity.exe
- Linux: TBD

## Check for Updates
Window ▶ Lunar Mobile Console ▶ Check for updates...

## Bug Reports
Window ▶ Lunar Mobile Console ▶ Report bug...

## Contacts

For anything else: lunar.plugin@gmail.com
