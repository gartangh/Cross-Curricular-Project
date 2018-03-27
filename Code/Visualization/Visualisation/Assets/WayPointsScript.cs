using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WayPointsScript : MonoBehaviour {

    public GameObject WayPoint;
    GameObject[] waypoints;
	// Use this for initialization
	void Start () {
        waypoints = MakeWaypointsFromFile("waypointpositions.txt");
        for(int i = 0; i<waypoints.Length-1; i++)
        {
            DrawLine(waypoints[i].transform.position, waypoints[i+1].transform.position, new Color(0, 0, 255));
        }
    }
	
	// Update is called once per frame
	void Update () {
		
	}   

    GameObject[] MakeWaypointsFromFile(string fileloc)
    {
        // create an array of strings with each element being a line from the file representing 1 waypoint's coordinates
        string[] positions = System.IO.File.ReadAllLines(fileloc);
        // create array to contain all waypoints
        GameObject[] waypoints = new GameObject[positions.Length];
        // instantiate all waypoints
        for (int i = 0; i < positions.Length; i++)
        {
            string[] position = positions[i].Split(',');
            float x = float.Parse(position[0]);
            float y = float.Parse(position[1]);
            float z = float.Parse(position[2]);
            // transform coordinates to unity coordinates
            Vector3 coords = TransformCoordinates(new Vector3(x, y, z));
            GameObject waypoint = Instantiate(WayPoint, coords, Quaternion.identity);
            waypoints[i] = waypoint;
        }
        return waypoints;
    }

    Vector3 TransformCoordinates(Vector3 coords)
    {
        float temp = coords.y;
        coords.x /= 1000;
        coords.y = coords.z / 1000;
        coords.z = -temp / 1000;
        return coords;
    }

    void DrawLine(Vector3 start, Vector3 end, Color color)
    {
        GameObject myLine = new GameObject();
        myLine.transform.position = start;
        myLine.AddComponent<LineRenderer>();
        LineRenderer lr = myLine.GetComponent<LineRenderer>();
        lr.material = new Material(Shader.Find("Particles/Alpha Blended Premultiply"));
        lr.SetColors(color, color);
        lr.SetWidth(0.01f, 0.01f);
        lr.SetPosition(0, start);
        lr.SetPosition(1, end);
    }


}
