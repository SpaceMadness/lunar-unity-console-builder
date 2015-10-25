using UnityEngine;

using System;
using System.Collections;

public class Logger : MonoBehaviour
{
    bool logging;
    int nextMessageIndex;

    public void StartLogger()
    {
        logging = !logging;
        if (logging)
        {
            StartCoroutine(LogMessages());
        }
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
}
