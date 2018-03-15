using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DroneScript : MonoBehaviour {

	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
        Vector3 coords = GetCoordinates("position.txt");
        Vector3 goodcoords = TransformCoordinates(coords);
        transform.position = goodcoords;
	}

    // Transform coordinates to Unity coordinates
    Vector3 TransformCoordinates (Vector3 coords)
    {
        float temp = coords.y;
        coords.x /= 1000;
        coords.y = coords.z / 1000;
        coords.z = -temp / 1000;
        return coords;
    }

    Vector3 GetCoordinates (string fileloc)
    {
        string position = System.IO.File.ReadAllText(fileloc);
        string[] test = position.Split(',');
        float x = float.Parse(test[0]);
        float y = float.Parse(test[1]);
        float z = float.Parse(test[2]);
        Vector3 coords = new Vector3(x, y, z);
        return coords;
    }
}
