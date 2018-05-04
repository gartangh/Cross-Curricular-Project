using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class DragScript : MonoBehaviour
{

    void OnMouseDrag()
    {
        Vector3 heading = transform.position - Camera.main.transform.position;
        float distance = Vector3.Dot(heading, Camera.main.transform.forward);
        Vector3 mousePosition = new Vector3(Input.mousePosition.x, Input.mousePosition.y, distance);
        Vector3 objPosition = Camera.main.ScreenToWorldPoint(mousePosition);

        transform.position = objPosition;
    }

    // Use this for initialization
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {

    }
}