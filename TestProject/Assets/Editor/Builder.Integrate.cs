using UnityEngine;
using UnityEditor;

using System;
using System.Collections;

namespace LunarConsoleBuilder
{
    static partial class Builder
    {
        static void IntegratePlugin()
        {
            bool succeed = EditorApplication.ExecuteMenuItem("Window/Lunar Mobile Console/Install...");
            if (!succeed)
            {
                throw new Exception("Can't integrate plugin");
            }

            bool saved = EditorApplication.SaveScene();
            if (!saved)
            {
                throw new Exception("Scene not saved");
            }
        }
    }
}
