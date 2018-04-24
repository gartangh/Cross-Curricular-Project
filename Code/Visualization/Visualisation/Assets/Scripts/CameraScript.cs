using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraScript : MonoBehaviour {
    public float speed = 50.0f;
    private bool follow;
    public GameObject drone;
    private Transform trans;
    public float xMargin = 1f; // Distance in the x axis the player can move before the camera follows.
    public float zMargin = 1f; // Distance in the y axis the player can move before the camera follows.
    public float xSmooth = 8f; // How smoothly the camera catches up with it's target movement in the x axis.
    public float zSmooth = 8f; // How smoothly the camera catches up with it's target movement in the y axis.

    // Camera rotations (according to unity axis system)
    public Vector3 lookDown = new Vector3(90, 0, 0);
    public Vector3 lookXplus = new Vector3(0, 90, 0);
    public Vector3 lookXmin = new Vector3(0, 270, 0);
    public Vector3 lookZplus = new Vector3(0, 0, 0);
    public Vector3 lookZmin = new Vector3(0, 180, 0);

    // Use this for initialization
    void Start () {
        follow = false;
        trans = drone.transform;
        Camera.main.transform.position = new Vector3(15000, 10000, -5000);
	}

    // Update is called once per frame
    void Update()
    {
        if (follow)
        {
            // TrackPlayer();
            ArrowControl();
        }
		else
        {
            ArrowControl();
        }
    }

    public void startFollowing()
    {
        follow = true;
    }

    public void ArrowControl()
    {
        if (Input.GetKey(KeyCode.RightArrow))
        {
            transform.Translate(new Vector3(speed * Time.deltaTime * 1000, 0, 0));
        }
        if (Input.GetKey(KeyCode.LeftArrow))
        {
            transform.Translate(new Vector3(-speed * Time.deltaTime * 1000, 0, 0));
        }
        if (Input.GetKey(KeyCode.DownArrow))
        {
            transform.Translate(new Vector3(0, -speed * Time.deltaTime * 1000, 0));
        }
        if (Input.GetKey(KeyCode.UpArrow))
        {
            transform.Translate(new Vector3(0, speed * Time.deltaTime * 1000, 0));
        }
        if (Input.GetKey(KeyCode.M))
        {
            if (transform.rotation.eulerAngles == lookDown)
            {
                Camera.main.transform.rotation = Quaternion.Euler(lookXplus);
                Camera.main.transform.position = new Vector3(Camera.main.transform.position.x, 3000, Camera.main.transform.position.z);
            }
            else if (transform.rotation.eulerAngles == lookXplus)
            {
                Camera.main.transform.rotation = Quaternion.Euler(lookZplus);
            }
            else if (transform.rotation.eulerAngles == lookZplus)
            {
                Camera.main.transform.rotation = Quaternion.Euler(lookXmin);
            }
            else if (transform.rotation.eulerAngles == lookXmin)
            {
                Camera.main.transform.rotation = Quaternion.Euler(lookZmin);
            }
            else if (transform.rotation.eulerAngles == lookZmin)
            {
                Camera.main.transform.rotation = Quaternion.Euler(lookDown);
                Camera.main.transform.position = new Vector3(Camera.main.transform.position.x, 10000, Camera.main.transform.position.z);
            }
        }
    }

    private bool CheckXMargin()
    {
        // Returns true if the distance between the camera and the player in the x axis is greater than the x margin.
        return Mathf.Abs(transform.position.x - trans.position.x) > xMargin;
    }


    private bool CheckZMargin()
    {
        // Returns true if the distance between the camera and the player in the y axis is greater than the y margin.
        return Mathf.Abs(transform.position.z - trans.position.z) > zMargin;
    }


    private void TrackPlayer()
    {
        // By default the target x and y coordinates of the camera are it's current x and y coordinates.
        float targetX = transform.position.x;
        float targetZ = transform.position.z;

        // If the player has moved beyond the x margin...
        if (CheckXMargin())
        {
            // ... the target x coordinate should be a Lerp between the camera's current x position and the player's current x position.
            targetX = Mathf.Lerp(transform.position.x, trans.position.x, xSmooth * Time.deltaTime);
        }

        // If the player has moved beyond the y margin...
        if (CheckZMargin())
        {
            // ... the target y coordinate should be a Lerp between the camera's current y position and the player's current y position.
            targetZ = Mathf.Lerp(transform.position.z, trans.position.z, zSmooth * Time.deltaTime);
        }

        // Set the camera's position to the target position with the same y component.
        transform.position = new Vector3(targetX, transform.position.y, targetZ);
    }
}
