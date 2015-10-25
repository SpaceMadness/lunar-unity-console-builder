using UnityEngine;
using UnityEditor;

using System;
using System.Collections;
using System.IO;

namespace LunarConsoleBuilder
{
    static partial class Builder
    {
        private static readonly string BuildsDir = "Build";

        [MenuItem("Window/Lunar Mobile Console/Build/iOS")]
        static void BuildIOS()
        {
            string outDir = BuildsDir + "/iOS";
            Cleanup(outDir);
            
            EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTarget.iOS);
            BuildPipeline.BuildPlayer(GetScenePaths(), outDir, BuildTarget.iOS, BuildOptions.None);
        }
        
        [MenuItem("Window/Lunar Mobile Console/Build/Android")]
        static void BuildAndroid()
        {
            string outDir = BuildsDir + "/Android";
            Cleanup(outDir);
            
            string productName = PlayerSettings.productName;
            
            EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTarget.Android);
            BuildPipeline.BuildPlayer(GetScenePaths(), outDir + "/" + productName + ".apk", BuildTarget.Android, BuildOptions.None);
        }

        [MenuItem("Window/Lunar Mobile Console/Build/All")]
        static void BuildAll()
        {
            BuildIOS();
            BuildAndroid();
        }

        private static string[] GetScenePaths()
        {
            string[] scenes = new string[EditorBuildSettings.scenes.Length];
            
            for(int i = 0; i < scenes.Length; i++)
            {
                scenes[i] = EditorBuildSettings.scenes[i].path;
            }
            
            return scenes;
        }

        private static void Cleanup(string dir)
        {
            if (Directory.Exists(dir))
            {
                Directory.Delete(dir, true);
            }
            Directory.CreateDirectory(dir);
        }
    }
}
