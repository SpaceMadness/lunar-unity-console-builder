using UnityEngine;
using UnityEngine.UI;

using System;
using System.Collections;

using LunarConsolePlugin;

public class Logger : MonoBehaviour
{
    [SerializeField]
    Text statusText;

    bool logging;
    int nextMessageIndex;
    int consoleOpenCount;
    int consoleCloseCount;

    void Start()
    {
        LunarConsole.onConsoleOpened += delegate() {
            ++consoleOpenCount;
            UpdateStatusText();
        };
        LunarConsole.onConsoleClosed += delegate() {
            ++consoleCloseCount;
            UpdateStatusText();
        };
    }

    public void StartLogger()
    {
        logging = !logging;
        if (logging)
        {
            StartCoroutine(LogMessages());
        }
    }

    public void ShowConsole()
    {
        LunarConsole.Show();
    }

    IEnumerator LogMessages()
    {
        nextMessageIndex = 0;
        while (logging)
        {
            string message = Data.lines[nextMessageIndex];
            if (message.StartsWith("E/"))
            {
                Debug.LogError(message);
            }
            else if (message.StartsWith("W/"))
            {
                Debug.LogWarning(message);
            }
            else
            {
                Debug.Log(message);
            }
            nextMessageIndex = (nextMessageIndex + 1) % Data.lines.Length;

            yield return new WaitForSeconds(0.25f);
        }
    }

    public void ThrowException()
    {
        throw new Exception("Test exception");
    }

    #region Status text

    void UpdateStatusText()
    {
        statusText.text = "Open count: " + consoleOpenCount + "\n" +
                          "Close count: " + consoleCloseCount;
    }

    #endregion
}
