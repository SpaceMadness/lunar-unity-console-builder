﻿using UnityEngine;
using UnityEditor;

using System;
using System.Collections;

namespace LunarConsoleBuilder
{
    static partial class Builder
    {
        private static readonly string SCENE_PATH = "Assets/Scenes/Scene.unity";

        [MenuItem("Window/Lunar Mobile Console/Build/Integrate")]
        static void IntegratePlugin()
        {
            bool opened = EditorApplication.OpenScene(SCENE_PATH);
            if (!opened)
            {
                throw new Exception("Can't open scene: " + SCENE_PATH);
            }

            bool succeed = EditorApplication.ExecuteMenuItem("Window/Lunar Mobile Console/Install...");
            if (!succeed)
            {
                throw new Exception("Can't integrate plugin");
            }

            bool saved = EditorApplication.SaveScene(SCENE_PATH);
            if (!saved)
            {
                throw new Exception("Can't save scene: " + SCENE_PATH);
            }
        }
    }
}
